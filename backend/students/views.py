from .permissions import IsAdministrator, CanManageStudents
from .models import Student, StudentPhoto
from .serializers import StudentSerializer, StudentCSVUploadSerializer, StudentBulkCreateSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .renderers import CSVRenderer  # Import from the correctly named file
from django.db import transaction
from django.utils import timezone  # Add this missing import
import logging

logger = logging.getLogger(__name__)


class StudentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows students to be viewed or edited.
    
    Permissions:
    - Administrators: Full CRUD access to all student operations
    - Registration Officers: Can view, create students, and upload CSV files
    """
    queryset = Student.objects.filter(is_active=True).order_by('surname', 'first_name')
    serializer_class = StudentSerializer
    permission_classes = [CanManageStudents]  # Updated to use flexible permission
    lookup_field = 'student_uuid'

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        Customize permissions per action for better security control.
        """
        if self.action in ['list', 'retrieve', 'create', 'upload_csv', 'csv_template', 'validation_info', 'upload_photo']:
            # Both administrators and registration officers can access these
            permission_classes = [CanManageStudents]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Only administrators can modify/delete existing students
            permission_classes = [IsAdministrator]
        else:
            # Default to the class-level permission
            permission_classes = self.permission_classes
            
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """
        Create a new student record.
        Available to both Administrators and Registration Officers.
        """
        # Log who is creating the student for audit purposes
        user_info = f"{request.user.username} ({request.user.user_type})"
        logger.info(f"Student creation initiated by {user_info}")
        
        response = super().create(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_201_CREATED:
            logger.info(f"Student created successfully by {user_info}: {response.data.get('registration_number', 'N/A')}")
            
            # Add creator info to response for audit trail
            response.data['created_by'] = {
                'username': request.user.username,
                'user_type': request.user.user_type,
                'full_name': getattr(request.user, 'full_name', request.user.username)
            }
        
        return response

    def list(self, request, *args, **kwargs):
        """
        List all students with pagination.
        Available to both Administrators and Registration Officers.
        """
        response = super().list(request, *args, **kwargs)
        
        # Add user context to response
        if hasattr(response, 'data') and isinstance(response.data, dict):
            response.data['user_permissions'] = {
                'current_user': request.user.username,
                'user_type': request.user.user_type,
                'can_create': True,
                'can_upload_csv': True,
                'can_modify': request.user.user_type == 'administrator',
                'can_delete': request.user.user_type == 'administrator'
            }
        
        return response

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single student record.
        Available to both Administrators and Registration Officers.
        """
        response = super().retrieve(request, *args, **kwargs)
        
        # Add user permissions to the response
        if response.status_code == status.HTTP_200_OK:
            response.data['user_permissions'] = {
                'can_modify': request.user.user_type == 'administrator',
                'can_delete': request.user.user_type == 'administrator'
            }
            
            # Add photo information if exists
            student = self.get_object()
            if hasattr(student, 'photo') and student.photo and student.photo.photo:
                response.data['photo'] = {
                    'url': request.build_absolute_uri(student.photo.photo.url),
                    'uploaded_at': student.photo.uploaded_at
                }
        
        return response

    @action(
        detail=False, 
        methods=['post'], 
        parser_classes=[MultiPartParser, FormParser],
        url_path='upload-csv',
        permission_classes=[CanManageStudents]
    )
    def upload_csv(self, request):
        """
        Upload students data via CSV file.
        
        Available to both Administrators and Registration Officers.
        
        Expected CSV format:
        surname,first_name,middle_name,mobile_phone,registration_number,department,soma_class_code,academic_year_status,student_status
        
        Required fields: surname, first_name, registration_number, department
        Optional fields: middle_name, mobile_phone, soma_class_code, academic_year_status, student_status
        """
        try:
            # Add detailed user info to logs for auditing
            user_info = f"{request.user.username} ({request.user.user_type}) - {getattr(request.user, 'full_name', 'N/A')}"
            logger.info(f"CSV upload initiated by {user_info}")
            
            # Validate the uploaded file
            upload_serializer = StudentCSVUploadSerializer(data=request.data)
            if not upload_serializer.is_valid():
                logger.warning(f"CSV upload validation failed for {user_info}: {upload_serializer.errors}")
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
                logger.error(f"CSV data validation failed for {user_info}: {str(e)}")
                return Response(
                    {
                        'success': False,
                        'message': 'CSV validation failed',
                        'errors': str(e)
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create students one by one to handle duplicates
            created_students = []
            skipped_records = []
            
            for row_data in valid_rows:
                reg_number = row_data.get('registration_number')
                try:
                    # Check if student with this registration number already exists
                    if Student.objects.filter(registration_number=reg_number).exists():
                        skipped_records.append(reg_number)
                        continue
                        
                    # Create the student
                    student = Student(**row_data)
                    student.save()
                    created_students.append(student)
                except Exception as e:
                    logger.error(f"Error creating student with reg number {reg_number}: {str(e)}")
                    skipped_records.append(reg_number)
            
            logger.info(f"Successfully created {len(created_students)} students via CSV upload by {user_info}")
            logger.info(f"Skipped {len(skipped_records)} duplicate records")
            
            return Response(
                {
                    'success': True,
                    'message': f'Successfully created {len(created_students)} students, skipped {len(skipped_records)} duplicates',
                    'data': {
                        'total_created': len(created_students),
                        'total_skipped': len(skipped_records),
                        'skipped_registration_numbers': skipped_records,
                        'students': StudentSerializer(created_students, many=True).data,
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
        permission_classes=[CanManageStudents],
        renderer_classes=[CSVRenderer]
    )
    def csv_template(self, request):
        """
        Download a CSV template file for student upload.
        """
        from django.http import HttpResponse
        import csv
        import io
        
        logger.info(f"CSV template downloaded by {request.user.username} ({request.user.user_type})")
        
        # Create a StringIO object to write CSV data
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers matching the expected format
        headers = [
            'Your Registration Number:',
            'Your Surname:',
            'Your First_Name:',
            'Your Middle_Name',
            'Your Active Mobile Phone number:',
            'Your Department',
            'Your Status in Academic Year 2024/25:',
            'Your SOMA Class(eg OD24CE,BENG24EE,ME24SE etc):'
        ]
        writer.writerow(headers)
        
        # Write example row
        example_row = [
            '240126000000',  # Plain number format
            'Doe',
            'John',
            'Michael',
            '255712345678',
            'CE',
            'Continuing',
            'BENG24CE'
        ]
        writer.writerow(example_row)
        
        # Get the CSV content
        csv_content = output.getvalue()
        output.close()
        
        # Create response
        response = HttpResponse(
            csv_content,
            content_type='text/csv',
        )
        response['Content-Disposition'] = 'attachment; filename=student_upload_template.csv'
        
        return response

    @action(
        detail=False, 
        methods=['get'], 
        url_path='validation-info',
        permission_classes=[CanManageStudents]  # Both user types can get validation info
    )
    def validation_info(self, request):
        """
        Get information about CSV upload validation rules and formats.
        Available to both Administrators and Registration Officers.
        """
        return Response({
            'required_fields': ['surname', 'first_name', 'registration_number', 'department'],
            'optional_fields': ['middle_name', 'mobile_phone', 'soma_class_code', 'academic_year_status', 'student_status'],
            'academic_year_status_choices': [choice[0] for choice in Student.ACADEMIC_YEAR_STATUS_CHOICES],
            'student_status_choices': [choice[0] for choice in Student.STUDENT_STATUS_CHOICES],
            'file_requirements': {
                'format': 'CSV',
                'max_size': '5MB',
                'encoding': 'UTF-8'
            },
            'validation_rules': {
                'registration_number': 'Must be unique across all students',
                'mobile_phone': 'Optional. Maximum 15 characters for phone number',
                'academic_year_status': 'Must be one of the valid choices if provided',
                'student_status': 'Must be one of the valid choices if provided'
            },
            'user_permissions': {
                'current_user': request.user.username,
                'user_type': request.user.user_type,
                'full_name': getattr(request.user, 'full_name', request.user.username),
                'can_upload': True,
                'can_download_template': True,
                'can_create_students': True,
                'can_view_students': True,
                'can_modify_students': request.user.user_type == 'administrator',
                'can_delete_students': request.user.user_type == 'administrator'
            }
        })

    @action(
        detail=True,
        methods=['post'],
        parser_classes=[MultiPartParser, FormParser],
        url_path='upload-photo',
        permission_classes=[CanManageStudents]
    )
    def upload_photo(self, request, student_uuid=None):
        """
        Upload a photo for a specific student.
        Available to both Administrators and Registration Officers.
        """
        try:
            # Get the student (already handled by get_object in ViewSet)
            student = self.get_object()
            
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
            
            # Rename the file to use student UUID
            extension = 'jpg' if photo_file.content_type in ['image/jpeg', 'image/jpg'] else 'png'
            photo_file.name = f"{student.student_uuid}.{extension}"
            
            # Create or update StudentPhoto
            student_photo, created = StudentPhoto.objects.get_or_create(
                student=student,
                defaults={'photo': photo_file}
            )
            
            if not created:
                # Update existing photo - delete old file first
                if student_photo.photo:
                    student_photo.photo.delete(save=False)
                student_photo.photo = photo_file
                student_photo.save()
            
            # Log the action
            user_info = f"{request.user.username} ({request.user.user_type})"
            action = 'uploaded' if created else 'updated'
            logger.info(f"Photo {action} for student {student.registration_number} by {user_info}")
            
            return Response({
                'success': True,
                'message': f'Photo {action} successfully',
                'data': {
                    'student_uuid': student.student_uuid,
                    'registration_number': student.registration_number,
                    'photo_url': request.build_absolute_uri(student_photo.photo.url) if student_photo.photo else None,
                    'uploaded_at': student_photo.uploaded_at,
                    'uploaded_by': {
                        'username': request.user.username,
                        'user_type': request.user.user_type,
                        'full_name': getattr(request.user, 'full_name', request.user.username)
                    }
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error uploading photo for student {student_uuid}: {str(e)}")
            return Response(
                {'success': False, 'error': 'An error occurred while uploading the photo'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        """
        Update student record - Only available to Administrators.
        """
        user_info = f"{request.user.username} ({request.user.user_type})"
        logger.info(f"Student update initiated by {user_info}")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially update student record - Only available to Administrators.
        """
        user_info = f"{request.user.username} ({request.user.user_type})"
        logger.info(f"Student partial update initiated by {user_info}")
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete student record - Only available to Administrators.
        """
        user_info = f"{request.user.username} ({request.user.user_type})"
        logger.warning(f"Student deletion initiated by {user_info}")
        return super().destroy(request, *args, **kwargs)
