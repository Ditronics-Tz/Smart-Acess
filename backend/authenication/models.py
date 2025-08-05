# authentication/models.py

import uuid
from django.db import models
from django.contrib.auth.hashers import make_password, check_password



class Administrator(models.Model):
    admin_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    password_hash = models.CharField(max_length=255)
    salt = models.CharField(max_length=255, null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    password_changed_at = models.DateTimeField(auto_now_add=True)
    failed_login_attempts = models.IntegerField(default=0)
    account_locked = models.BooleanField(default=False)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "administrators"
        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["email"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["deleted_at"]),
        ]

    def __str__(self):
        return self.username
    
    @property
    def id(self):
        return self.admin_id


# authentication/models.py (continued)

class OTPVerification(models.Model):
    otp_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_type = models.CharField(max_length=30, choices=[
        ('administrator', 'Administrator'),
        ('registration_officer', 'Registration Officer')
    ])
    user_id = models.UUIDField()
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    attempts_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "otp_verifications"
        indexes = [
            models.Index(fields=["user_type", "user_id"]),
            models.Index(fields=["otp_code"]),
            models.Index(fields=["expires_at"]),
        ]
