from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Staff, StaffPhoto
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

    @action(
        detail=True,
        methods=['post'],
        parser_classes=[MultiPartParser, FormParser],
        url_path='upload-photo',
        permission_classes=[CanManageStaff]
    )
    def upload_photo(self, request, staff_uuid=None):
        """
        Upload a photo for a specific staff member.
        Available to both Administrators and Registration Officers.
        """
        try:
            # Get the staff member (already handled by get_object in ViewSet)
            staff = self.get_object()

            # Check if photo file is provided
            if 'photo' not in request.FILES:
                return Response(
                    {'success': False, 'error': 'No photo file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            photo_file = request.FILES['photo']

            # Validate file type
            allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
            if photo_file.content_type not in allowed_types:
                return Response(
                    {'success': False, 'error': 'Invalid file type. Only JPEG and PNG images are allowed.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate file size (max 5MB)
            max_size = 5 * 1024 * 1024  # 5MB
            if photo_file.size > max_size:
                return Response(
                    {'success': False, 'error': 'File size too large. Maximum size is 5MB.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Rename the file to use staff UUID
            extension = 'jpg' if photo_file.content_type in ['image/jpeg', 'image/jpg'] else 'png'
            photo_file.name = f"{staff.staff_uuid}.{extension}"

            # Create or update StaffPhoto
            staff_photo, created = StaffPhoto.objects.get_or_create(
                staff=staff,
                defaults={'photo': photo_file}
            )

            if not created:
                # Update existing photo - delete old file first
                if staff_photo.photo:
                    staff_photo.photo.delete(save=False)
                staff_photo.photo = photo_file
                staff_photo.save()

            # Log the action
            user_info = f"{request.user.username} ({request.user.user_type})"
            action = 'uploaded' if created else 'updated'
            logger.info(f"Photo {action} for staff {staff.staff_number} by {user_info}")

            return Response({
                'success': True,
                'message': f'Photo {action} successfully',
                'data': {
                    'staff_uuid': staff.staff_uuid,
                    'staff_number': staff.staff_number,
                    'photo_url': request.build_absolute_uri(staff_photo.photo.url) if staff_photo.photo else None,
                    'uploaded_at': staff_photo.uploaded_at,
                    'uploaded_by': {
                        'username': request.user.username,
                        'user_type': request.user.user_type,
                        'full_name': getattr(request.user, 'full_name', request.user.username)
                    }
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error uploading photo for staff {staff_uuid}: {str(e)}")
            return Response(
                {'success': False, 'error': 'An error occurred while uploading the photo'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
