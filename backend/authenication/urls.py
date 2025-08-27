# authentication/urls.py

from django.urls import path
from .views import (
    DeactivateUserAPIView, LoginAPIView, RetrieveUserAPIView, VerifyOTPAPIView, ResendOTPAPIView,
    CreateUserAPIView, RefreshTokenAPIView, LogoutAPIView
)

urlpatterns = [
    path("login", LoginAPIView.as_view(), name="login"),
    path("verify-otp", VerifyOTPAPIView.as_view(), name="verify-otp"),
    path("resend-otp", ResendOTPAPIView.as_view(), name="resend-otp"),
    path("create-user", CreateUserAPIView.as_view(), name="create-user"), ##for registration-officer
    path("users/<uuid:user_id>", RetrieveUserAPIView.as_view(), name="retrieve-user"), #admin gets single reg officer
    path("users/<uuid:user_id>/deactivate", DeactivateUserAPIView.as_view(), name="deactivate-user"),
    path("refresh", RefreshTokenAPIView.as_view(), name="refresh-token"),
    path("logout", LogoutAPIView.as_view(), name="logout"),
]