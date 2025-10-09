from rest_framework import serializers
from .models import Staff
import csv
import io


class StaffSerializer(serializers.ModelSerializer):
	class Meta:
		model = Staff
		fields = [
			'staff_uuid', 'surname', 'first_name', 'middle_name', 'mobile_phone',
			'staff_number', 'department', 'position', 'employment_status', 'is_active',
			'created_at', 'updated_at'
		]


class StaffCSVUploadSerializer(serializers.Serializer):
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
        import csv
        import io

        try:
            # Reset file pointer to the beginning
            csv_file.seek(0)

            # Read the file with COMMA delimiter
            decoded_file = csv_file.read().decode('utf-8-sig')  # Handle BOM
            csv_file.seek(0)

            # Use comma delimiter
            reader = csv.reader(io.StringIO(decoded_file), delimiter=',')

            # Get headers
            try:
                headers = next(reader)
                # Strip BOM from the first header if present
                if headers and headers[0].startswith('\ufeff'):
                    headers[0] = headers[0].replace('\ufeff', '')
                print(f"Detected headers: {headers}")  # Debug line
            except StopIteration:
                raise serializers.ValidationError("CSV file is empty")

            # Map the user-friendly headers to the model field names
            header_mapping = {
                'Your Staff Number:': 'staff_number',
                'Your Surname:': 'surname',
                'Your First_Name:': 'first_name',
                'Your Middle_Name': 'middle_name',
                'Your Active Mobile Phone number:': 'mobile_phone',
                'Your Department': 'department',
                'Your Position': 'position',
                'Your Employment Status': 'employment_status',
                # Add variations to be more forgiving
                'Your Staff Number': 'staff_number',
                'Staff Number': 'staff_number',
                'Your Surname': 'surname',
                'Surname': 'surname',
                'Your First_Name': 'first_name',
                'First Name': 'first_name',
                'First_Name': 'first_name',
                'Middle Name': 'middle_name',
                'Middle_Name': 'middle_name',
                'Your Active Mobile Phone number': 'mobile_phone',
                'Mobile Phone': 'mobile_phone',
                'Department': 'department',
                'Your Position': 'position',
                'Position': 'position',
                'Your Employment Status': 'employment_status',
                'Employment Status': 'employment_status'
            }

            # Create a mapping of indices to field names
            field_indices = {}
            for i, header in enumerate(headers):
                # Strip any whitespace
                header = header.strip()

                if header in header_mapping:
                    field_indices[i] = header_mapping[header]
                else:
                    # Try without the colon
                    header_no_colon = header.rstrip(':')
                    if header_no_colon in header_mapping:
                        field_indices[i] = header_mapping[header_no_colon]
                    else:
                        # Try to match approximately by checking each part
                        for user_header, field_name in header_mapping.items():
                            if (header.lower() == user_header.lower() or
                                header.lower() == user_header.lower().rstrip(':') or
                                header.lower() == user_header.lower().replace('your ', '') or
                                header.lower().startswith(user_header.lower().rstrip(':').replace('your ', ''))):
                                field_indices[i] = field_name
                                break

            print(f"Field mapping: {field_indices}")  # Debug output

            # Check for required columns
            required_fields = ['surname', 'first_name', 'staff_number', 'department', 'position']
            missing_fields = [field for field in required_fields if field not in field_indices.values()]
            if missing_fields:
                print(f"Missing required fields: {missing_fields}")  # Debug output
                raise serializers.ValidationError(f"Missing required columns: {', '.join(missing_fields)}")

            # Process rows
            valid_rows = []
            errors = []

            # Get existing staff numbers for uniqueness check
            existing_staff_numbers = set(Staff.objects.values_list('staff_number', flat=True))

            # Dictionary to track staff numbers in the current CSV for uniqueness check
            csv_staff_numbers = set()

            row_idx = 1  # Initialize outside the loop for use in error reporting
            for row_idx, row in enumerate(reader, start=2):  # Start from 2 to account for header row
                if not any(row):  # Skip empty rows
                    continue

                row_data = {'employment_status': 'Active'}  # Default status

                # Validate and extract fields from the row
                for col_idx, value in enumerate(row):
                    if col_idx in field_indices:
                        field_name = field_indices[col_idx]
                        value = value.strip()

                        # Handle empty required fields
                        if not value and field_name in required_fields:
                            errors.append(f"Row {row_idx}: Column '{field_name}' is required")
                            continue

                        # Special handling for staff numbers
                        if field_name == 'staff_number':
                            # Remove any spaces
                            staff_num = value.replace(" ", "")

                            # Check for uniqueness in database
                            if staff_num in existing_staff_numbers:
                                errors.append(f"Row {row_idx}: Staff number '{staff_num}' already exists in database")
                                continue

                            # Check for uniqueness within CSV
                            if staff_num in csv_staff_numbers:
                                errors.append(f"Row {row_idx}: Staff number '{staff_num}' appears multiple times in CSV")
                                continue

                            csv_staff_numbers.add(staff_num)
                            row_data[field_name] = staff_num

                        # Employment status validation with mapping
                        elif field_name == 'employment_status':
                            # Map common variations to accepted values
                            status_mapping = {
                                'active': 'Active',
                                'inactive': 'Inactive',
                                'terminated': 'Terminated',
                                'retired': 'Retired',
                                'on leave': 'On Leave',
                                'on_leave': 'On Leave'
                            }

                            normalized_status = value.lower().replace(' ', '_')
                            if normalized_status in status_mapping:
                                row_data[field_name] = status_mapping[normalized_status]
                            else:
                                valid_choices = [choice[0] for choice in Staff.EMPLOYMENT_STATUS_CHOICES]
                                errors.append(f"Row {row_idx}: Invalid employment_status: '{value}'. Valid choices: {valid_choices}")
                                continue
                        else:
                            # For all other fields
                            row_data[field_name] = value

                # If no errors in this row, add to valid rows
                if not any(f"Row {row_idx}:" in error for error in errors):
                    valid_rows.append(row_data)

            # If there are any errors, raise validation error
            if errors:
                raise serializers.ValidationError({
                    'csv_errors': errors,
                    'total_rows': row_idx - 1,  # Exclude header row
                    'valid_rows': len(valid_rows),
                    'error_rows': len(errors)
                })

            return valid_rows

        except UnicodeDecodeError:
            raise serializers.ValidationError("File encoding error. Please ensure the file is UTF-8 encoded.")
        except Exception as e:
            raise serializers.ValidationError(f"Error processing CSV file: {str(e)}")


class StaffBulkCreateSerializer(serializers.Serializer):
    staff_data = serializers.ListField(child=StaffSerializer())

    def create(self, validated_data):
        staff_data = validated_data['staff_data']
        staff_members = []

        for staff_member_data in staff_data:
            staff_members.append(Staff(**staff_member_data))

        # Bulk create all staff members
        created_staff = Staff.objects.bulk_create(staff_members)
        return created_staff
