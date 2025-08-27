# authentication/urls.py

from django.urls import path
from .views import (
    ChangeUserPasswordAPIView, DeactivateUserAPIView, LoginAPIView, RetrieveUserAPIView, VerifyOTPAPIView, ResendOTPAPIView,
    CreateUserAPIView, RefreshTokenAPIView, LogoutAPIView, ListRegistrationOfficersAPIView
)

urlpatterns = [
    path("login", LoginAPIView.as_view(), name="login"),
    path("verify-otp", VerifyOTPAPIView.as_view(), name="verify-otp"),
    path("resend-otp", ResendOTPAPIView.as_view(), name="resend-otp"),
    path("create-user", CreateUserAPIView.as_view(), name="create-user"), ##for registration-officer
    path("registration-officers", ListRegistrationOfficersAPIView.as_view(), name="list-registration-officers"), #admin gets all reg officers
    path("users/<uuid:user_id>", RetrieveUserAPIView.as_view(), name="retrieve-user"), #admin gets single reg officer
    path("users/<uuid:user_id>/deactivate", DeactivateUserAPIView.as_view(), name="deactivate-user"), #asdmin deactivates reg
    path("users/<uuid:user_id>/change-password", ChangeUserPasswordAPIView.as_view(), name="change-password"), #admin to change reg  pass
    path("refresh", RefreshTokenAPIView.as_view(), name="refresh-token"),
    path("logout", LogoutAPIView.as_view(), name="logout"),
]
