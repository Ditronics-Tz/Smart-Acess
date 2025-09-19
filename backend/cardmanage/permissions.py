from rest_framework.permissions import BasePermission


class IsAdministrator(BasePermission):
    """
    Allows access only to authenticated users with a user_type of 'administrator'.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'user_type') and
            request.user.user_type == 'administrator'
        )


class CanManageCards(BasePermission):
    """
    Permission for card management operations.
    - Administrators: Full CRUD access
    - Registration Officers: Can view, create, and manage cards
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        if not hasattr(request.user, 'user_type'):
            return False
            
        # Both administrators and registration officers can manage cards
        return request.user.user_type in ['administrator', 'registration_officer']

    def has_object_permission(self, request, view, obj):
        """
        Object-level permissions for individual card records.
        """
        if not request.user.is_authenticated:
            return False
            
        # Both user types have full access to card objects
        return request.user.user_type in ['administrator', 'registration_officer']