# authentication/urls.py

from django.urls import path
from .views import LoginAPIView, VerifyOTPAPIView

urlpatterns = [
    path("login", LoginAPIView.as_view(), name="login"),
    path("verify-otp", VerifyOTPAPIView.as_view(), name="verify-otp"),
]
