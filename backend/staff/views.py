from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Staff, StaffPhoto
from .serializers import StaffSerializer, StaffCSVUploadSerializer, StaffBulkCreateSerializer
from .permission import IsAdministrator, CanManageStaff
import logging
from django.db import transaction
from django.utils import timezone
import csv
import io
from django.http import HttpResponse

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

            # Add photo information if exists
            staff = self.get_object()
            if hasattr(staff, 'photo') and staff.photo and staff.photo.photo:
                response.data['photo'] = {
                    'url': request.build_absolute_uri(staff.photo.photo.url),
                    'uploaded_at': staff.photo.uploaded_at
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
        """
        Upload staff data via CSV file.

        Available to both Administrators and Registration Officers.

        Expected CSV format:
        surname,first_name,middle_name,mobile_phone,staff_number,department,position,employment_status

        Required fields: surname, first_name, staff_number, department, position
        Optional fields: middle_name, mobile_phone, employment_status
        """
        try:
            # Add detailed user info to logs for auditing
            user_info = f"{request.user.username} ({request.user.user_type}) - {getattr(request.user, 'full_name', 'N/A')}"
            logger.info(f"CSV upload initiated by {user_info}")

            # Validate the uploaded file
            upload_serializer = StaffCSVUploadSerializer(data=request.data)
            if not upload_serializer.is_valid():
                logger.warning(f"CSV upload validation failed by {user_info}: {upload_serializer.errors}")
                return Response(
                    {
                        'success': False,
                        'message': 'Invalid file upload',
                        'errors': upload_serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            csv_file = upload_serializer.validated_data['csv_file']

            # Validate CSV data
            try:
                valid_rows = upload_serializer.validate_csv_data(csv_file)
            except Exception as e:
                logger.error(f"CSV data validation failed by {user_info}: {str(e)}")
                return Response(
                    {
                        'success': False,
                        'message': 'CSV validation failed',
                        'errors': str(e)
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create staff members one by one to handle duplicates
            created_staff = []
            skipped_records = []

            with transaction.atomic():
                for row_data in valid_rows:
                    try:
                        # Create the staff member
                        staff = Staff.objects.create(**row_data)
                        created_staff.append(staff)
                        logger.info(f"Created staff member: {staff.staff_number} - {staff.first_name} {staff.surname}")
                    except Exception as e:
                        # If creation fails, skip this record
                        staff_number = row_data.get('staff_number', 'Unknown')
                        skipped_records.append({
                            'staff_number': staff_number,
                            'reason': str(e)
                        })
                        logger.warning(f"Skipped staff member {staff_number}: {str(e)}")

            logger.info(f"Successfully created {len(created_staff)} staff members via CSV upload by {user_info}")
            logger.info(f"Skipped {len(skipped_records)} duplicate/problematic records")

            return Response(
                {
                    'success': True,
                    'message': f'Successfully created {len(created_staff)} staff members, skipped {len(skipped_records)} problematic records',
                    'data': {
                        'total_created': len(created_staff),
                        'total_skipped': len(skipped_records),
                        'skipped_records': skipped_records,
                        'staff_members': StaffSerializer(created_staff, many=True).data,
                        'uploaded_by': {
                            'username': request.user.username,
                            'user_type': request.user.user_type,
                            'full_name': getattr(request.user, 'full_name', request.user.username),
                            'upload_timestamp': timezone.now().isoformat()
                        }
                    }
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"Unexpected error during CSV upload by {user_info}: {str(e)}")
            return Response(
                {
                    'success': False,
                    'message': 'An error occurred during upload',
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(
        detail=False,
        methods=['get'],
        url_path='csv-template',
        permission_classes=[CanManageStaff]
    )
    def csv_template(self, request):
        """
        Download a CSV template file for staff upload.
        """
        logger.info(f"CSV template downloaded by {request.user.username} ({request.user.user_type})")

        # Create a StringIO object to write CSV data
        output = io.StringIO()
        writer = csv.writer(output)

        # Write headers matching the expected format
        headers = [
            'Your Staff Number:',
            'Your Surname:',
            'Your First_Name:',
            'Your Middle_Name',
            'Your Active Mobile Phone number:',
            'Your Department',
            'Your Position',
            'Your Employment Status'
        ]
        writer.writerow(headers)

        # Write example row
        example_row = [
            'STF001',  # Staff number
            'Doe',
            'John',
            'Michael',
            '255712345678',
            'Computer Engineering',
            'Lecturer',
            'Active'
        ]
        writer.writerow(example_row)

        # Get the CSV content
        csv_content = output.getvalue()
        output.close()

        # Return HttpResponse directly to bypass DRF content negotiation
        response = HttpResponse(csv_content, content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename=staff_upload_template.csv'
        return response

    @action(
        detail=False,
        methods=['get'],
        url_path='validation-info',
        permission_classes=[CanManageStaff]
    )
    def validation_info(self, request):
        return Response({
            'required_fields': ['surname', 'first_name', 'staff_number', 'department', 'position'],
            'optional_fields': ['middle_name', 'mobile_phone', 'employment_status'],
            'employment_status_choices': [choice[0] for choice in Staff.EMPLOYMENT_STATUS_CHOICES],
            'file_requirements': {
                'format': 'CSV',
                'max_size': '5MB',
                'encoding': 'UTF-8'
            },
            'validation_rules': {
                'staff_number': 'Must be unique across all staff members',
                'mobile_phone': 'Optional. Maximum 15 characters for phone number',
                'employment_status': 'Must be one of the valid choices if provided. Defaults to "Active"',
                'department': 'Required field',
                'position': 'Required field'
            },
            'user_permissions': {
                'current_user': request.user.username,
                'user_type': request.user.user_type,
                'can_create': True,
                'can_upload_csv': True,
                'can_download_template': True,
                'can_upload_photos': True,
                'can_modify': request.user.user_type == 'administrator',
                'can_delete': request.user.user_type == 'administrator'
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
