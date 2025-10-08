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


class IsRegistrationOfficer(BasePermission):
    """
    Allows access only to authenticated users with a user_type of 'registration_officer'.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'user_type') and
            request.user.user_type == 'registration_officer'
        )


class CanManageStudents(BasePermission):
    """
    Permission for student management operations.
    - Administrators: Full CRUD access
    - Registration Officers: Can view, create, and upload CSV (no update/delete)
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        if not hasattr(request.user, 'user_type'):
            return False
            
        # Administrators have full access
        if request.user.user_type == 'administrator':
            return True
            
        # Registration Officers have limited access
        if request.user.user_type == 'registration_officer':
            # Allow specific actions for registration officers
            allowed_actions = ['list', 'retrieve', 'create', 'upload_csv', 'csv_template', 'validation_info', 'upload_photo']
            
            # Check if this is a custom action
            if hasattr(view, 'action') and view.action in allowed_actions:
                return True
                
            # For regular CRUD operations, check the HTTP method
            # Allow GET (list/retrieve) and POST (create)
            if request.method in ['GET', 'POST', 'HEAD', 'OPTIONS']:
                return True
                
            # Deny PUT, PATCH, DELETE for registration officers
            return False
            
        return False

    def has_object_permission(self, request, view, obj):
        """
        Object-level permissions for individual student records.
        """
        if not request.user.is_authenticated:
            return False
            
        # Administrators have full access to all objects
        if request.user.user_type == 'administrator':
            return True
            
        # Registration Officers can only view individual students, not modify/delete
        # But allow POST for upload-photo action
        if request.user.user_type == 'registration_officer':
            if request.method in ['GET', 'HEAD', 'OPTIONS']:
                return True
            # Allow POST for photo upload
            if request.method == 'POST' and 'upload-photo' in request.path:
                return True
            return False
            
        return False