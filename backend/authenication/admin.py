from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTPVerification

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_active', 'is_staff', 'last_login', 'created_at')
    search_fields = ('username', 'email', 'full_name')
    list_filter = ('is_active', 'is_staff', 'user_type', 'created_at')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('full_name', 'email', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at')}),
        ('Custom Fields', {'fields': ('user_type', 'password_changed_at', 'failed_login_attempts', 'account_locked', 'account_locked_until', 'deleted_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'full_name', 'user_type', 'password'),
        }),
    )
    ordering = ('email',)

admin.site.register(User, UserAdmin)

@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp_code', 'is_verified', 'expires_at', 'attempts_count')
    search_fields = ('email', 'otp_code')
    list_filter = ('is_verified',)