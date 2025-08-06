# authentication/views.py

from datetime import timedelta
import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.core.cache import cache
from .models import Administrator, RegistrationOfficer, OTPVerification
from .serializers import LoginSerializer, VerifyOTPSerializer
import uuid
from django.contrib.auth.hashers import check_password
from .utils import send_otp_email


class RateLimitMixin:
    """
    Rate limiting mixin for API views
    """
    
    def check_rate_limit(self, request, key_suffix, max_attempts=5, window_minutes=15):
        """
        Check if request exceeds rate limit
        """
        client_ip = self.get_client_ip(request)
        cache_key = f"rate_limit_{key_suffix}_{client_ip}"
        
        attempts = cache.get(cache_key, 0)
        
        if attempts >= max_attempts:
            return False, f"Too many attempts. Try again in {window_minutes} minutes."
        
        # Increment attempts
        cache.set(cache_key, attempts + 1, timeout=window_minutes * 60)
        return True, None
    
    def get_client_ip(self, request):
        """
        Get client IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LoginAPIView(APIView, RateLimitMixin):
    """
    POST /api/auth/login

    Accepts: username, password, user_type
    Validates and returns session_id for OTP verification.
    Also sends OTP to user email.
    """

    def post(self, request):
        # Rate limiting - 5 login attempts per IP per 15 minutes
        is_allowed, error_message = self.check_rate_limit(request, "login", max_attempts=5, window_minutes=15)
        if not is_allowed:
            return Response({"detail": error_message}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]
        user_type = serializer.validated_data["user_type"]

        # Additional rate limiting per username - 3 attempts per username per 10 minutes
        username_rate_key = f"login_username_{username}"
        username_attempts = cache.get(username_rate_key, 0)
        if username_attempts >= 3:
            return Response({"detail": "Too many login attempts for this username. Try again in 10 minutes."}, 
                          status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Handle different user types
        if user_type == "administrator":
            try:
                user = Administrator.objects.get(username=username)
            except Administrator.DoesNotExist:
                # Increment username attempts on failed login
                cache.set(username_rate_key, username_attempts + 1, timeout=10 * 60)
                return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

            if user.account_locked:
                return Response({"detail": "Account is locked."}, status=status.HTTP_403_FORBIDDEN)

            # Validate password
            if not check_password(password, user.password_hash):
                user.failed_login_attempts += 1
                user.save(update_fields=["failed_login_attempts"])
                # Increment username attempts on failed password
                cache.set(username_rate_key, username_attempts + 1, timeout=10 * 60)
                return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

            # Successful login - reset username attempts
            cache.delete(username_rate_key)
            user.failed_login_attempts = 0
            user.last_login = timezone.now()
            user.save(update_fields=["last_login", "failed_login_attempts"])
            
            user_id = user.admin_id

        elif user_type == "registration_officer":
            try:
                user = RegistrationOfficer.objects.get(username=username)
            except RegistrationOfficer.DoesNotExist:
                # Increment username attempts on failed login
                cache.set(username_rate_key, username_attempts + 1, timeout=10 * 60)
                return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

            if not user.is_active:
                return Response({"detail": "Account is inactive."}, status=status.HTTP_403_FORBIDDEN)

            # Validate password
            if not check_password(password, user.password_hash):
                # Increment username attempts on failed password
                cache.set(username_rate_key, username_attempts + 1, timeout=10 * 60)
                return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

            # Successful login - reset username attempts
            cache.delete(username_rate_key)
            user_id = user.officer_id

        else:
            return Response({"detail": "Invalid user type."}, status=status.HTTP_400_BAD_REQUEST)

        # Rate limiting for OTP generation - 3 OTP requests per email per 5 minutes
        otp_rate_key = f"otp_generation_{user.email}"
        otp_attempts = cache.get(otp_rate_key, 0)
        if otp_attempts >= 3:
            return Response({"detail": "Too many OTP requests. Try again in 5 minutes."}, 
                          status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Generate OTP
        otp_code = str(random.randint(100000, 999999))
        session_id = uuid.uuid4()

        # Save OTP record
        OTPVerification.objects.create(
            otp_id=session_id,
            user_type=user_type,
            user_id=user_id,
            email=user.email,
            otp_code=otp_code,
            expires_at=timezone.now() + timedelta(minutes=5)
        )

        # Send OTP to email
        send_otp_email(user.email, otp_code)
        
        # Increment OTP generation attempts
        cache.set(otp_rate_key, otp_attempts + 1, timeout=5 * 60)

        # Return session ID
        return Response({
            "session_id": str(session_id),
            "message": "Login successful. OTP sent to your email."
        }, status=status.HTTP_200_OK)


class VerifyOTPAPIView(APIView, RateLimitMixin):
    """
    POST /api/auth/verify-otp
    Verifies the OTP and returns JWT tokens if successful.
    """

    def post(self, request):
        # Rate limiting - 10 OTP verification attempts per IP per 10 minutes
        is_allowed, error_message = self.check_rate_limit(request, "otp_verify", max_attempts=10, window_minutes=10)
        if not is_allowed:
            return Response({"detail": error_message}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session_id = serializer.validated_data["session_id"]
        otp_code = serializer.validated_data["otp_code"]
        user_type = serializer.validated_data["user_type"]

        # Rate limiting per session - 5 attempts per session
        session_rate_key = f"otp_session_{session_id}"
        session_attempts = cache.get(session_rate_key, 0)
        if session_attempts >= 5:
            return Response({"detail": "Too many OTP attempts for this session. Please request a new OTP."}, 
                          status=status.HTTP_429_TOO_MANY_REQUESTS)

        try:
            otp_obj = OTPVerification.objects.get(otp_id=session_id, otp_code=otp_code, user_type=user_type)
        except OTPVerification.DoesNotExist:
            # Increment session attempts on failed OTP
            cache.set(session_rate_key, session_attempts + 1, timeout=10 * 60)
            return Response({"detail": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

        if otp_obj.is_verified:
            return Response({"detail": "OTP already used."}, status=status.HTTP_400_BAD_REQUEST)

        if otp_obj.expires_at < timezone.now():
            return Response({"detail": "OTP expired."}, status=status.HTTP_400_BAD_REQUEST)

        # Successful OTP verification - clear session attempts
        cache.delete(session_rate_key)
        
        otp_obj.is_verified = True
        otp_obj.verified_at = timezone.now()
        otp_obj.save()

        # Get user based on user type
        if user_type == "administrator":
            user_model = Administrator
        elif user_type == "registration_officer":
            user_model = RegistrationOfficer
        else:
            return Response({"detail": "Invalid user type."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = user_model.objects.get(pk=otp_obj.user_id)
        except user_model.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user_type": user_type,
            "user_id": str(otp_obj.user_id),
            "username": user.username
        }, status=status.HTTP_200_OK)