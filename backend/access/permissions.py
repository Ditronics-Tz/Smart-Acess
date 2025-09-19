from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsAdministrator(BasePermission):
    """
    Permission to only allow administrators to access the view.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'user_type') and
            request.user.user_type == 'administrator'
        )


class CanManageAccess(BasePermission):
    """
    Permission to allow administrators and security personnel to manage access logs.
    This includes viewing access logs, statistics, and managing access control.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'user_type'):
            return False
        
        # Allow administrators and registration officers to manage access
        allowed_user_types = ['administrator', 'registration_officer']
        return request.user.user_type in allowed_user_types


class IsAccessControlDevice(BasePermission):
    """
    Permission for access control devices/systems.
    This allows the RFID access endpoint to be accessed without strict user authentication.
    Should be used with API key authentication or device-specific tokens in production.
    """
    def has_permission(self, request, view):
        # For now, allow access to the RFID check endpoint
        # In production, you might want to check for API keys or device tokens
        if view.action == 'check_access':
            return True
        
        # For other actions, require authentication
        return request.user and request.user.is_authenticated


class CanViewAccessLogs(BasePermission):
    """
    Permission to view access logs.
    Allows administrators, registration officers, and security personnel.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'user_type'):
            return False
        
        # Allow these user types to view access logs
        allowed_user_types = ['administrator', 'registration_officer', 'security']
        return request.user.user_type in allowed_user_types