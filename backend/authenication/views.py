# authentication/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from .models import Administrator, OTPVerification
from .serializers import LoginSerializer, VerifyOTPSerializer
import uuid
from django.contrib.auth.hashers import check_password
import hashlib


class LoginAPIView(APIView):
    """
    POST /api/auth/login

    Accepts: username, password, user_type
    Validates and returns session_id for OTP verification.
    """

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]
        user_type = serializer.validated_data["user_type"]

        # For now, we only handle administrator login
        if user_type != "administrator":
            return Response({"detail": "Only administrator login supported now."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Administrator.objects.get(username=username)
        except Administrator.DoesNotExist:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if account is locked
        if user.account_locked:
            return Response({"detail": "Account is locked."}, status=status.HTTP_403_FORBIDDEN)

        # ✅ Validate password using Django's password checking
        if not check_password(password, user.password_hash):
            user.failed_login_attempts += 1
            user.save(update_fields=["failed_login_attempts"])
            Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)


        # Reset failed attempts if successful
        user.failed_login_attempts = 0
        user.last_login = timezone.now()
        user.save(update_fields=["last_login", "failed_login_attempts"])

        # Generate session ID (UUID) for OTP verification
        session_id = str(uuid.uuid4())

        # You will store this in your OTP table and send OTP later
        return Response({
            "session_id": session_id,
            "message": "Login successful. Proceed to OTP verification."
        }, status=status.HTTP_200_OK)

class VerifyOTPAPIView(APIView):
    """
    POST /api/auth/verify-otp
    Verifies the OTP and returns JWT tokens if successful.
    """

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session_id = serializer.validated_data["session_id"]
        otp_code = serializer.validated_data["otp_code"]
        user_type = serializer.validated_data["user_type"]

        try:
            otp_obj = OTPVerification.objects.get(otp_id=session_id, otp_code=otp_code, user_type=user_type)
        except OTPVerification.DoesNotExist:
            return Response({"detail": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

        if otp_obj.is_verified:
            return Response({"detail": "OTP already used."}, status=status.HTTP_400_BAD_REQUEST)

        if otp_obj.expires_at < timezone.now():
            return Response({"detail": "OTP expired."}, status=status.HTTP_400_BAD_REQUEST)

        otp_obj.is_verified = True
        otp_obj.verified_at = timezone.now()
        otp_obj.save()

        # Get user
        if user_type == "administrator":
            user_model = Administrator
        else:
            return Response({"detail": "Not implemented."}, status=400)

        try:
            user = user_model.objects.get(pk=otp_obj.user_id)
        except user_model.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user_type": user_type,
        })