# authentication/urls.py

from django.urls import path
from .views import (
    LoginAPIView, VerifyOTPAPIView, ResendOTPAPIView,
    CreateRegistrationOfficerAPIView, RefreshTokenAPIView, LogoutAPIView
)

urlpatterns = [
    path("login", LoginAPIView.as_view(), name="login"),
    path("verify-otp", VerifyOTPAPIView.as_view(), name="verify-otp"),
    path("resend-otp", ResendOTPAPIView.as_view(), name="resend-otp"),
    path("create-registration-officer", CreateRegistrationOfficerAPIView.as_view(), name="create-registration-officer"),
    path("refresh", RefreshTokenAPIView.as_view(), name="refresh-token"),
    path("logout", LogoutAPIView.as_view(), name="logout"),
]
