# authentication/views.py

from datetime import timedelta
import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from .models import Administrator, OTPVerification
from .serializers import LoginSerializer, VerifyOTPSerializer
import uuid
from django.contrib.auth.hashers import check_password
from .models import OTPVerification
from .utils import send_otp_email


class LoginAPIView(APIView):
    """
    POST /api/auth/login

    Accepts: username, password, user_type
    Validates and returns session_id for OTP verification.
    Also sends OTP to administrator email.
    """

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]
        user_type = serializer.validated_data["user_type"]

        if user_type != "administrator":
            return Response({"detail": "Only administrator login supported now."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Administrator.objects.get(username=username)
            
        except Administrator.DoesNotExist:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        if user.account_locked:
            return Response({"detail": "Account is locked."}, status=status.HTTP_403_FORBIDDEN)

        #  Validate password using Django's secure method
        if not check_password(password, user.password_hash):
            user.failed_login_attempts += 1
            user.save(update_fields=["failed_login_attempts"])
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        # ✅ Successful login
        user.failed_login_attempts = 0
        user.last_login = timezone.now()
        user.save(update_fields=["last_login", "failed_login_attempts"])

        # ✅ Generate OTP
        otp_code = str(random.randint(100000, 999999))
        session_id = uuid.uuid4()

        # ✅ Save OTP record
        OTPVerification.objects.create(
            otp_id=session_id,
            user_type="administrator",
            user_id=user.admin_id,
            email=user.email,
            otp_code=otp_code,
            expires_at=timezone.now() + timedelta(minutes=5)
        )

        # ✅ Send OTP to email
        send_otp_email(user.email, otp_code)

        # ✅ Return session ID
        return Response({
            "session_id": str(session_id),
            "message": "Login successful. OTP sent to your email."
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