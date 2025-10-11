from rest_framework.permissions import BasePermission

class IsAdministrator(BasePermission):
    """
    Permission class that allows both administrators and registration officers
    to access the administrator app functionality.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'user_type') and
            request.user.user_type in ['administrator', 'registration_officer']
        )

class IsAdministratorOrRegistrationOfficer(BasePermission):
    """
    Explicit permission class for administrator and registration officer access.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'user_type') and
            request.user.user_type in ['administrator', 'registration_officer']
        )

class IsAdministratorOnly(BasePermission):
    """
    Permission class that allows only administrators access.
    Use this for sensitive operations that should be restricted to administrators only.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'user_type') and
            request.user.user_type == 'administrator'
        )
