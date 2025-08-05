# authentication/serializers.py

from rest_framework import serializers


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
