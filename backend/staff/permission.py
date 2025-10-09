from rest_framework.permissions import BasePermission

class IsAdministrator(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'user_type') and
            request.user.user_type == 'administrator'
        )

class IsRegistrationOfficer(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'user_type') and
            request.user.user_type == 'registration_officer'
        )

class CanManageStaff(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if not hasattr(request.user, 'user_type'):
            return False

        if request.user.user_type == 'administrator':
            return True

        if request.user.user_type == 'registration_officer':
            allowed_actions = ['list', 'retrieve', 'create', 'upload_csv', 'csv_template', 'validation_info']

            if hasattr(view, 'action') and view.action in allowed_actions:
                return True

            if request.method in ['GET', 'POST', 'HEAD', 'OPTIONS']:
                return True

            return False

        return False

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if request.user.user_type == 'administrator':
            return True

        if request.user.user_type == 'registration_officer':
            if request.method in ['GET', 'HEAD', 'OPTIONS']:
                return True
            return False

        return False
