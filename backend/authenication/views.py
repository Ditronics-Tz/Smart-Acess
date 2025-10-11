# authentication/views.py

from datetime import timedelta
from os import access
import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator
from .models import User, OTPVerification
from django.db import models
from .serializers import (
    LoginSerializer, VerifyOTPSerializer, CreateUserSerializer,
    ResendOTPSerializer, RefreshTokenSerializer, LogoutSerializer
)
import uuid
from .utils import send_otp_email
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken


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

        try:
            user = User.objects.get(username=username, user_type=user_type)
        except User.DoesNotExist:
            cache.set(username_rate_key, username_attempts + 1, timeout=10 * 60)
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        if user.account_locked:
            return Response({"detail": "Account is locked."}, status=status.HTTP_403_FORBIDDEN)

        if not user.check_password(password):
            user.failed_login_attempts += 1
            user.save(update_fields=["failed_login_attempts"])
            cache.set(username_rate_key, username_attempts + 1, timeout=10 * 60)
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        cache.delete(username_rate_key)
        user.failed_login_attempts = 0
        user.last_login = timezone.now()
        user.save(update_fields=["last_login", "failed_login_attempts"])
        user_id = user.id

        # OTP disabled - directly generate JWT tokens
        # Generate JWT tokens without using RefreshToken.for_user()
        refresh = RefreshToken.for_user(user)
        refresh['user_type'] = user.user_type
        refresh['username'] = user.username

        # Add same claims to access token
        access = refresh.access_token
        access['user_type'] = user.user_type
        access['username'] = user.username

        return Response({
            "access": str(access),
            "refresh": str(refresh),
            "user_type": user.user_type,
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

        try:
            user = User.objects.get(pk=otp_obj.user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Generate JWT tokens without using RefreshToken.for_user()
        refresh = RefreshToken.for_user(user)
        refresh['user_type'] = user.user_type
        refresh['username'] = user.username

        # Add same claims to access token
        access = refresh.access_token
        access['user_type'] = user.user_type
        access['username'] = user.username

        return Response({
            "access": str(access),
            "refresh": str(refresh),
            "user_type": user.user_type,
            "user_id": str(user.id),
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


class CreateUserAPIView(APIView):
    """
    POST /api/auth/create-user
    Only administrators can create users
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Check if user is administrator
        if not request.user.user_type == 'administrator':
            return Response({"detail": "Only administrators can create users."},
                          status=status.HTTP_403_FORBIDDEN)

        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            "message": "User created successfully.",
            "user_id": str(user.id),
            "username": user.username,
            "email": user.email
        }, status=status.HTTP_201_CREATED)


class RetrieveUserAPIView(APIView):    # endpoint for retrieving registration-officer details
    """
    GET /api/auth/users/<user_id>/
    Only administrators can view user details
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        if request.user.user_type != 'administrator':
            return Response({"detail": "Only administrators can retrieve users."},
                            status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "user_id": str(user.id),
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "phone_number": user.phone_number,
            "user_type": user.user_type,
            "is_active": user.is_active,
        }, status=status.HTTP_200_OK)


class ListRegistrationOfficersAPIView(APIView):
    """
    GET /api/auth/registration-officers/
    Only administrators can list registration officers
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.user_type != 'administrator':
            return Response({"detail": "Only administrators can list registration officers."},
                            status=status.HTTP_403_FORBIDDEN)

        # Get query parameters
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 10)
        search = request.GET.get('search', '')
        is_active = request.GET.get('is_active', None)

        # Base queryset - only registration officers
        queryset = User.objects.filter(user_type='registration_officer')

        # Apply filters
        if search:
            queryset = queryset.filter(
                models.Q(username__icontains=search) |
                models.Q(full_name__icontains=search) |
                models.Q(email__icontains=search)
            )

        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)

        # Order by creation date (newest first)
        queryset = queryset.order_by('-created_at')

        # Pagination
        try:
            page_size = min(int(page_size), 100)  # Max 100 items per page
            page = int(page)
        except (ValueError, TypeError):
            page = 1
            page_size = 10

        paginator = Paginator(queryset, page_size)

        try:
            users_page = paginator.page(page)
        except:
            users_page = paginator.page(1)

        # Serialize user data
        users_data = []
        for user in users_page:
            users_data.append({
                "user_id": str(user.id),
                "username": user.username,
                "full_name": user.full_name,
                "email": user.email,
                "phone_number": user.phone_number,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "failed_login_attempts": user.failed_login_attempts,
                "account_locked": user.account_locked
            })

        return Response({
            "registration_officers": users_data,
            "pagination": {
                "current_page": users_page.number,
                "total_pages": paginator.num_pages,
                "total_count": paginator.count,
                "has_next": users_page.has_next(),
                "has_previous": users_page.has_previous(),
                "page_size": page_size
            }
        }, status=status.HTTP_200_OK)


class DeactivateUserAPIView(APIView): #deactivating registration-officer
    """
    PATCH /api/auth/users/<user_id>/deactivate/
    Only administrators can deactivate users
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, user_id):
        if request.user.user_type != 'administrator':
            return Response({"detail": "Only administrators can deactivate users."},
                            status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        user.is_active = False
        user.save()

        return Response({"message": f"User {user.username} deactivated successfully."},
                        status=status.HTTP_200_OK)


class ChangeUserPasswordAPIView(APIView):   # view for administartor to change reg-officer password
    """
    PATCH /api/auth/users/<user_id>/change-password/
    Only administrators can reset user passwords
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, user_id):
        if request.user.user_type != 'administrator':
            return Response({"detail": "Only administrators can change passwords."},
                            status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not new_password or not confirm_password:
            return Response({"detail": "Both new_password and confirm_password are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({"detail": "Passwords do not match."},
                            status=status.HTTP_400_BAD_REQUEST)

        if len(new_password) < 8:
            return Response({"detail": "Password must be at least 8 characters long."},
                            status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"message": f"Password updated successfully for {user.username}."},
                        status=status.HTTP_200_OK)


class RefreshTokenAPIView(APIView):
    """
    POST /api/auth/refresh
    """

    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_str = serializer.validated_data['refresh']

        try:
            refresh_token = RefreshToken(refresh_str)
            access_token = refresh_token.access_token

            data = {'access': str(access_token)}

            if api_settings.ROTATE_REFRESH_TOKENS:
                if api_settings.BLACKLIST_AFTER_ROTATION:
                    refresh_token.blacklist()
                refresh_token.set_jti()
                refresh_token.set_exp()
                refresh_token.set_iat()
                data['refresh'] = str(refresh_token)

            return Response(data, status=status.HTTP_200_OK)
        except TokenError as e:
            raise InvalidToken(e.args[0])


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