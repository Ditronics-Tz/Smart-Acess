from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import Administrator, OTPVerification ,RegistrationOfficer


@admin.register(Administrator)
class AdministratorAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_active', 'account_locked', 'last_login', 'created_at')
    search_fields = ('username', 'email', 'full_name')
    list_filter = ('is_active', 'account_locked', 'created_at')

    # Automatically hash password before saving
    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get("password_hash") and not obj.password_hash.startswith("pbkdf2_"):
            obj.password_hash = make_password(form.cleaned_data["password_hash"])
        super().save_model(request, obj, form, change)


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp_code', 'is_verified', 'expires_at', 'attempts_count')
    search_fields = ('email', 'otp_code')
    list_filter = ('is_verified',)


@admin.register(RegistrationOfficer)
class RegistrationOfficerAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'full_name')
    list_filter = ('is_active', 'created_at')

    # Automatically hash password before saving
    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get("password_hash") and not obj.password_hash.startswith("pbkdf2_"):
            obj.password_hash = make_password(form.cleaned_data["password_hash"])
        super().save_model(request, obj, form, change)

