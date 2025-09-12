from .permissions import IsAdministrator
from .models import Student
from .serializers import StudentSerializer, StudentCSVUploadSerializer, StudentBulkCreateSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class StudentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows students to be viewed or edited.
    """
    queryset = Student.objects.filter(is_active=True).order_by('surname', 'first_name')
    serializer_class = StudentSerializer
    permission_classes = [IsAdministrator]
    lookup_field = 'student_uuid'

    @action(
        detail=False, 
        methods=['post'], 
        parser_classes=[MultiPartParser, FormParser],
        url_path='upload-csv'
    )
    def upload_csv(self, request):
        """
        Upload students data via CSV file.
        
        Expected CSV format:
        surname,first_name,middle_name,email,registration_number,department,program,soma_class_code,academic_year_status,student_status
        
        Required fields: surname, first_name, registration_number, department, program
        Optional fields: middle_name, email, soma_class_code, academic_year_status, student_status
        """
        try:
            # Validate the uploaded file
            upload_serializer = StudentCSVUploadSerializer(data=request.data)
            if not upload_serializer.is_valid():
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
                return Response(
                    {
                        'success': False,
                        'message': 'CSV validation failed',
                        'errors': str(e)
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create students in a transaction
            with transaction.atomic():
                students = []
                for row_data in valid_rows:
                    students.append(Student(**row_data))
                
                # Bulk create all students
                created_students = Student.objects.bulk_create(students)
                
                logger.info(f"Successfully created {len(created_students)} students via CSV upload")
                
                return Response(
                    {
                        'success': True,
                        'message': f'Successfully created {len(created_students)} students',
                        'data': {
                            'total_created': len(created_students),
                            'students': StudentSerializer(created_students, many=True).data
                        }
                    },
                    status=status.HTTP_201_CREATED
                )
                
        except Exception as e:
            logger.error(f"Error during CSV upload: {str(e)}")
            return Response(
                {
                    'success': False,
                    'message': 'An error occurred during upload',
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='csv-template')
    def csv_template(self, request):
        """
        Download a CSV template file for student upload.
        """
        from django.http import HttpResponse
        import csv
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="student_upload_template.csv"'
        
        writer = csv.writer(response)
        
        # Write header
        headers = [
            'surname',
            'first_name', 
            'middle_name',
            'email',
            'registration_number',
            'department',
            'program',
            'soma_class_code',
            'academic_year_status',
            'student_status'
        ]
        writer.writerow(headers)
        
        # Write example row
        example_row = [
            'Doe',
            'John',
            'Michael',
            'john.doe@example.com',
            'REG2024001',
            'Computer Science',
            'Bachelor of Computer Science',
            'CS2024A',
            'Continuing',
            'Enrolled'
        ]
        writer.writerow(example_row)
        
        return response

    @action(detail=False, methods=['get'], url_path='validation-info')
    def validation_info(self, request):
        """
        Get information about CSV upload validation rules and formats.
        """
        return Response({
            'required_fields': ['surname', 'first_name', 'registration_number', 'department', 'program'],
            'optional_fields': ['middle_name', 'email', 'soma_class_code', 'academic_year_status', 'student_status'],
            'academic_year_status_choices': [choice[0] for choice in Student.ACADEMIC_YEAR_STATUS_CHOICES],
            'student_status_choices': [choice[0] for choice in Student.STUDENT_STATUS_CHOICES],
            'file_requirements': {
                'format': 'CSV',
                'max_size': '5MB',
                'encoding': 'UTF-8'
            },
            'validation_rules': {
                'registration_number': 'Must be unique across all students',
                'email': 'Must be valid email format if provided',
                'academic_year_status': 'Must be one of the valid choices if provided',
                'student_status': 'Must be one of the valid choices if provided'
            }
        })
