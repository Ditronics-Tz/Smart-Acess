# authentication/serializers.py

from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'email', 'phone_number', 'user_type', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=3, max_length=50)
    password = serializers.CharField(min_length=8, write_only=True)
    user_type = serializers.ChoiceField(choices=[("administrator", "Administrator"), ("registration_officer", "Registration Officer")])


class VerifyOTPSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    otp_code = serializers.CharField(min_length=6, max_length=6)
    user_type = serializers.ChoiceField(choices=[
        ("administrator", "Administrator"),
        ("registration_officer", "Registration Officer")
    ])

    #  additional validation:
    def validate_otp_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits")
        return value


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'full_name', 'email', 'phone_number', 'user_type', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user


class ResendOTPSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    user_type = serializers.ChoiceField(choices=[
        ("administrator", "Administrator"),
        ("registration_officer", "Registration Officer")
    ])


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()