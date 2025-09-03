from django.db import models
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