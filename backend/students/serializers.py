from rest_framework import serializers
from .models import Student
import csv
import io


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['id', 'student_uuid', 'created_at', 'updated_at']


class StudentCSVUploadSerializer(serializers.Serializer):
    csv_file = serializers.FileField()
    
    def validate_csv_file(self, value):
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("File must be a CSV file.")
        
        # Check file size (limit to 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 5MB.")
        
        return value
    
    def validate_csv_data(self, csv_file):
        """Validate CSV structure and data"""
        errors = []
        valid_rows = []
        
        try:
            # Read CSV content
            csv_file.seek(0)  # Reset file pointer
            content = csv_file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(content))
            
            # Required fields based on your model
            required_fields = ['surname', 'first_name', 'registration_number', 'department', 'program']
            
            # Check if all required columns exist
            missing_columns = set(required_fields) - set(csv_reader.fieldnames or [])
            if missing_columns:
                raise serializers.ValidationError(
                    f"Missing required columns: {', '.join(missing_columns)}"
                )
            
            row_number = 1
            existing_reg_numbers = set(Student.objects.values_list('registration_number', flat=True))
            new_reg_numbers = set()
            
            for row in csv_reader:
                row_number += 1
                row_errors = []
                
                # Validate required fields
                for field in required_fields:
                    if not row.get(field, '').strip():
                        row_errors.append(f"Column '{field}' is required")
                
                # Validate registration number uniqueness
                reg_number = row.get('registration_number', '').strip()
                if reg_number:
                    if reg_number in existing_reg_numbers:
                        row_errors.append(f"Registration number '{reg_number}' already exists in database")
                    elif reg_number in new_reg_numbers:
                        row_errors.append(f"Registration number '{reg_number}' appears multiple times in CSV")
                    else:
                        new_reg_numbers.add(reg_number)
                
                # Validate email format if provided
                email = row.get('email', '').strip()
                if email:
                    try:
                        serializers.EmailField().to_internal_value(email)
                    except serializers.ValidationError:
                        row_errors.append(f"Invalid email format: '{email}'")
                
                # Validate choice fields
                academic_year_status = row.get('academic_year_status', '').strip()
                if academic_year_status and academic_year_status not in [choice[0] for choice in Student.ACADEMIC_YEAR_STATUS_CHOICES]:
                    row_errors.append(f"Invalid academic_year_status: '{academic_year_status}'. Valid choices: {[choice[0] for choice in Student.ACADEMIC_YEAR_STATUS_CHOICES]}")
                
                student_status = row.get('student_status', '').strip()
                if student_status and student_status not in [choice[0] for choice in Student.STUDENT_STATUS_CHOICES]:
                    row_errors.append(f"Invalid student_status: '{student_status}'. Valid choices: {[choice[0] for choice in Student.STUDENT_STATUS_CHOICES]}")
                
                if row_errors:
                    errors.append(f"Row {row_number}: {'; '.join(row_errors)}")
                else:
                    # Clean and prepare the row data
                    clean_row = {
                        'surname': row.get('surname', '').strip(),
                        'first_name': row.get('first_name', '').strip(),
                        'middle_name': row.get('middle_name', '').strip() or None,
                        'email': email or None,
                        'registration_number': reg_number,
                        'department': row.get('department', '').strip(),
                        'program': row.get('program', '').strip(),
                        'soma_class_code': row.get('soma_class_code', '').strip() or None,
                        'academic_year_status': academic_year_status or 'Continuing',
                        'student_status': student_status or 'Enrolled',
                    }
                    valid_rows.append(clean_row)
            
            if errors:
                raise serializers.ValidationError({
                    'csv_errors': errors,
                    'total_rows': row_number - 1,
                    'valid_rows': len(valid_rows),
                    'error_rows': len(errors)
                })
            
            return valid_rows
            
        except UnicodeDecodeError:
            raise serializers.ValidationError("File encoding error. Please ensure the file is UTF-8 encoded.")
        except Exception as e:
            raise serializers.ValidationError(f"Error processing CSV file: {str(e)}")


class StudentBulkCreateSerializer(serializers.Serializer):
    students_data = serializers.ListField(child=StudentSerializer())
    
    def create(self, validated_data):
        students_data = validated_data['students_data']
        students = []
        
        for student_data in students_data:
            students.append(Student(**student_data))
        
        # Bulk create all students
        created_students = Student.objects.bulk_create(students)
        return created_students
