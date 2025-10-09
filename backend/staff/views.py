from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Staff, StaffPhoto
from .serializers import StaffSerializer
from .permission import IsAdministrator, CanManageStaff
import logging

logger = logging.getLogger(__name__)ramework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Staff
from .serializers import StaffSerializer
from .permission import IsAdministrator, CanManageStaff
import logging

logger = logging.getLogger(__name__)

class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.filter(is_active=True).order_by('surname', 'first_name')
    serializer_class = StaffSerializer
    permission_classes = [CanManageStaff]
    lookup_field = 'staff_uuid'

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create', 'upload_csv', 'csv_template', 'validation_info']:
            permission_classes = [CanManageStaff]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAdministrator]
        else:
            permission_classes = self.permission_classes

        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        user_info = f"{request.user.username} ({request.user.user_type})"
        logger.info(f"Staff creation initiated by {user_info}")

        response = super().create(request, *args, **kwargs)

        if response.status_code == status.HTTP_201_CREATED:
            logger.info(f"Staff created successfully by {user_info}: {response.data.get('staff_number', 'N/A')}")

            response.data['created_by'] = {
                'username': request.user.username,
                'user_type': request.user.user_type,
                'full_name': getattr(request.user, 'full_name', request.user.username)
            }

        return response

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        if hasattr(response, 'data') and isinstance(response.data, dict):
            total_staff = Staff.objects.count()
            active_staff = Staff.objects.filter(is_active=True).count()

            response.data['summary'] = {
                'total_staff': total_staff,
                'active_staff': active_staff,
                'inactive_staff': total_staff - active_staff
            }

            response.data['user_permissions'] = {
                'current_user': request.user.username,
                'user_type': request.user.user_type,
                'can_create': True,
                'can_modify': request.user.user_type == 'administrator',
                'can_delete': request.user.user_type == 'administrator'
            }

        return response

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            response.data['user_permissions'] = {
                'can_modify': request.user.user_type == 'administrator',
                'can_delete': request.user.user_type == 'administrator'
            }

        return response

    @action(
        detail=False,
        methods=['post'],
        parser_classes=[MultiPartParser, FormParser],
        url_path='upload-csv',
        permission_classes=[CanManageStaff]
    )
    def upload_csv(self, request):
        return Response({'message': 'CSV upload functionality to be implemented'}, status=status.HTTP_501_NOT_IMPLEMENTED)

    @action(
        detail=False,
        methods=['get'],
        url_path='csv-template',
        permission_classes=[CanManageStaff]
    )
    def csv_template(self, request):
        return Response({'message': 'CSV template functionality to be implemented'}, status=status.HTTP_501_NOT_IMPLEMENTED)

    @action(
        detail=False,
        methods=['get'],
        url_path='validation-info',
        permission_classes=[CanManageStaff]
    )
    def validation_info(self, request):
        return Response({
            'required_fields': ['surname', 'first_name', 'staff_number', 'department', 'position'],
            'optional_fields': ['middle_name', 'mobile_phone'],
            'field_constraints': {
                'staff_number': {'unique': True, 'max_length': 20},
                'mobile_phone': {'max_length': 15},
                'department': {'max_length': 255},
                'position': {'max_length': 100}
            }
        })

    def update(self, request, *args, **kwargs):
        user_info = f"{request.user.username} ({request.user.user_type})"
        logger.info(f"Staff update initiated by {user_info}")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        user_info = f"{request.user.username} ({request.user.user_type})"
        logger.info(f"Staff partial update initiated by {user_info}")
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        user_info = f"{request.user.username} ({request.user.user_type})"
        logger.warning(f"Staff deletion initiated by {user_info}")
        return super().destroy(request, *args, **kwargs)
