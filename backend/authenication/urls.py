# authentication/urls.py

from django.urls import path
from .views import LoginAPIView, VerifyOTPAPIView

urlpatterns = [
    path("auth/login", LoginAPIView.as_view(), name="login"),
    path("auth/verify-otp", VerifyOTPAPIView.as_view(), name="verify-otp"),
]
