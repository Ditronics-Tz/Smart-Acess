# authentication/views.py

from datetime import timedelta
import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth.hashers import make_password, check_password
from .models import Administrator, RegistrationOfficer, OTPVerification
from .serializers import (
    LoginSerializer, VerifyOTPSerializer, CreateRegistrationOfficerSerializer,
    ResendOTPSerializer, RefreshTokenSerializer, LogoutSerializer
)
import uuid
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
                cache.set(username_rate_key, username_attempts + 1, timeout=10 * 60)
                return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

            if user.account_locked:
                return Response({"detail": "Account is locked."}, status=status.HTTP_403_FORBIDDEN)

            if not check_password(password, user.password_hash):
                user.failed_login_attempts += 1
                user.save(update_fields=["failed_login_attempts"])
                cache.set(username_rate_key, username_attempts + 1, timeout=10 * 60)
                return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

            cache.delete(username_rate_key)
            user.failed_login_attempts = 0
            user.last_login = timezone.now()
            user.save(update_fields=["last_login", "failed_login_attempts"])
            user_id = user.admin_id

        elif user_type == "registration_officer":
            try:
                user = RegistrationOfficer.objects.get(username=username)
            except RegistrationOfficer.DoesNotExist:
                cache.set(username_rate_key, username_attempts + 1, timeout=10 * 60)
                return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

            if not user.is_active:
                return Response({"detail": "Account is inactive."}, status=status.HTTP_403_FORBIDDEN)

            if not check_password(password, user.password_hash):
                cache.set(username_rate_key, username_attempts + 1, timeout=10 * 60)
                return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

            cache.delete(username_rate_key)
            user_id = user.officer_id

        else:
            return Response({"detail": "Invalid user type."}, status=status.HTTP_400_BAD_REQUEST)

        # OTP disabled - directly generate JWT tokens
        # Generate JWT tokens without using RefreshToken.for_user()
        refresh = RefreshToken()
        refresh['user_id'] = str(user_id)
        refresh['user_type'] = user_type
        refresh['username'] = user.username
        
        # Add same claims to access token
        access = refresh.access_token
        access['user_id'] = str(user_id)
        access['user_type'] = user_type
        access['username'] = user.username

        return Response({
            "access": str(access),
            "refresh": str(refresh),
            "user_type": user_type,
            "user_id": str(user_id),
            "username": user.username,
            "message": "Login successful."
        }, status=status.HTTP_200_OK)


class VerifyOTPAPIView(APIView, RateLimitMixin):
    """
    POST /api/auth/verify-otp
    """

    def post(self, request):
        is_allowed, error_message = self.check_rate_limit(request, "otp_verify", max_attempts=10, window_minutes=10)
        if not is_allowed:
            return Response({"detail": error_message}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session_id = serializer.validated_data["session_id"]
        otp_code = serializer.validated_data["otp_code"]
        user_type = serializer.validated_data["user_type"]

        session_rate_key = f"otp_session_{session_id}"
        session_attempts = cache.get(session_rate_key, 0)
        if session_attempts >= 5:
            return Response({"detail": "Too many OTP attempts for this session. Please request a new OTP."}, 
                          status=status.HTTP_429_TOO_MANY_REQUESTS)

        try:
            otp_obj = OTPVerification.objects.get(otp_id=session_id, otp_code=otp_code, user_type=user_type)
        except OTPVerification.DoesNotExist:
            cache.set(session_rate_key, session_attempts + 1, timeout=10 * 60)
            return Response({"detail": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

        if otp_obj.is_verified:
            return Response({"detail": "OTP already used."}, status=status.HTTP_400_BAD_REQUEST)

        if otp_obj.expires_at < timezone.now():
            return Response({"detail": "OTP expired."}, status=status.HTTP_400_BAD_REQUEST)

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

        # Generate JWT tokens without using RefreshToken.for_user()
        refresh = RefreshToken()
        refresh['user_id'] = str(otp_obj.user_id)
        refresh['user_type'] = user_type
        refresh['username'] = user.username
        
        # Add same claims to access token
        access = refresh.access_token
        access['user_id'] = str(otp_obj.user_id)
        access['user_type'] = user_type
        access['username'] = user.username

        return Response({
            "access": str(access),
            "refresh": str(refresh),
            "user_type": user_type,
            "user_id": str(otp_obj.user_id),
            "username": user.username
        }, status=status.HTTP_200_OK)


class ResendOTPAPIView(APIView, RateLimitMixin):
    """
    POST /api/auth/resend-otp
    """

    def post(self, request):
        is_allowed, error_message = self.check_rate_limit(request, "resend_otp", max_attempts=3, window_minutes=5)
        if not is_allowed:
            return Response({"detail": error_message}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        serializer = ResendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session_id = serializer.validated_data["session_id"]
        user_type = serializer.validated_data["user_type"]

        try:
            otp_obj = OTPVerification.objects.get(otp_id=session_id, user_type=user_type, is_verified=False)
        except OTPVerification.DoesNotExist:
            return Response({"detail": "Invalid session or OTP already verified."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if last OTP is still valid (prevent spam)
        if otp_obj.expires_at > timezone.now():
            time_left = int((otp_obj.expires_at - timezone.now()).total_seconds() / 60)
            return Response({"detail": f"Current OTP is still valid for {time_left} minutes."}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # Generate new OTP
        new_otp_code = str(random.randint(100000, 999999))
        otp_obj.otp_code = new_otp_code
        otp_obj.expires_at = timezone.now() + timedelta(minutes=5)
        otp_obj.attempts_count = 0
        otp_obj.save()

        # Send new OTP
        send_otp_email(otp_obj.email, new_otp_code)

        return Response({
            "message": "New OTP sent to your email.",
            "session_id": str(session_id)
        }, status=status.HTTP_200_OK)


class CreateRegistrationOfficerAPIView(APIView):
    """
    POST /api/auth/create-registration-officer
    Only administrators can create registration officers
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Check if user is administrator
        try:
            admin = Administrator.objects.get(admin_id=request.user.id)
        except Administrator.DoesNotExist:
            return Response({"detail": "Only administrators can create registration officers."}, 
                          status=status.HTTP_403_FORBIDDEN)

        serializer = CreateRegistrationOfficerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create registration officer
        registration_officer = RegistrationOfficer.objects.create(
            username=serializer.validated_data['username'],
            full_name=serializer.validated_data['full_name'],
            email=serializer.validated_data['email'],
            phone_number=serializer.validated_data.get('phone_number'),
            password_hash=make_password(serializer.validated_data['password'])
        )

        return Response({
            "message": "Registration officer created successfully.",
            "officer_id": str(registration_officer.officer_id),
            "username": registration_officer.username,
            "email": registration_officer.email
        }, status=status.HTTP_201_CREATED)


class RefreshTokenAPIView(APIView):
    """
    POST /api/auth/refresh
    """

    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh_token = RefreshToken(serializer.validated_data['refresh'])
            access_token = refresh_token.access_token
            
            return Response({
                "access": str(access_token),
                "refresh": str(refresh_token)
            }, status=status.HTTP_200_OK)
        except Exception:
            return Response({"detail": "Invalid refresh token."}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutAPIView(APIView):
    """
    POST /api/auth/logout
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh_token = RefreshToken(serializer.validated_data['refresh'])
            refresh_token.blacklist()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)