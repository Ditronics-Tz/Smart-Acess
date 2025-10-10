from rest_framework import serializers
from .models import Card
from students.models import Student
from staff.models import Staff
from adminstrator.models import SecurityPersonnel
from students.serializers import StudentSerializer
from staff.serializers import StaffSerializer
import uuid


class SecurityPersonnelSerializer(serializers.ModelSerializer):
    """Basic serializer for security personnel info in cards"""
    class Meta:
        model = SecurityPersonnel
        fields = ['security_id', 'employee_id', 'badge_number', 'full_name', 'phone_number', 'is_active']


class CardSerializer(serializers.ModelSerializer):
    # Card holder information based on card type
    student_info = StudentSerializer(source='student', read_only=True)
    staff_info = StaffSerializer(source='staff', read_only=True)
    security_info = SecurityPersonnelSerializer(source='security_personnel', read_only=True)
    
    # Generic card holder info
    card_holder_name = serializers.ReadOnlyField()
    card_holder_number = serializers.ReadOnlyField()
    
    # Legacy fields for backward compatibility (student cards)
    student_name = serializers.CharField(
        source='student.first_name', 
        read_only=True
    )
    student_surname = serializers.CharField(
        source='student.surname', 
        read_only=True
    )
    registration_number = serializers.CharField(
        source='student.registration_number', 
        read_only=True
    )
    department = serializers.SerializerMethodField()

    class Meta:
        model = Card
        fields = '__all__'
        read_only_fields = ['card_uuid', 'issued_date', 'created_at', 'updated_at']

    def get_department(self, obj):
        """Get department based on card type"""
        if obj.card_type == 'student' and obj.student:
            return obj.student.department
        elif obj.card_type == 'staff' and obj.staff:
            return obj.staff.department
        elif obj.card_type == 'security':
            return 'Security'
        return None

    def validate_student(self, value):
        """Ensure student doesn't already have a card"""
        if value and hasattr(value, 'card'):
            raise serializers.ValidationError(
                f"Student {value.first_name} {value.surname} already has a card assigned."
            )
        return value

    def validate_staff(self, value):
        """Ensure staff doesn't already have a card"""
        if value and hasattr(value, 'card'):
            raise serializers.ValidationError(
                f"Staff {value.first_name} {value.surname} already has a card assigned."
            )
        return value

    def validate_security_personnel(self, value):
        """Ensure security personnel doesn't already have a card"""
        if value and hasattr(value, 'card'):
            raise serializers.ValidationError(
                f"Security personnel {value.full_name} already has a card assigned."
            )
        return value

    def validate_rfid_number(self, value):
        """Ensure RFID number is unique"""
        if self.instance:
            # For updates, exclude current instance
            if Card.objects.filter(rfid_number=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("This RFID number is already in use.")
        else:
            # For creation
            if Card.objects.filter(rfid_number=value).exists():
                raise serializers.ValidationError("This RFID number is already in use.")
        return value


class CardCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating cards with flexible card holder selection"""
    card_type = serializers.ChoiceField(choices=Card.CARD_TYPE_CHOICES, write_only=True)
    student_uuid = serializers.UUIDField(write_only=True, required=False)
    staff_uuid = serializers.UUIDField(write_only=True, required=False)
    security_uuid = serializers.UUIDField(write_only=True, required=False)
    generate_rfid = serializers.BooleanField(write_only=True, default=False)
    
    class Meta:
        model = Card
        fields = ['card_type', 'student_uuid', 'staff_uuid', 'security_uuid', 'rfid_number', 'expiry_date', 'generate_rfid']
        extra_kwargs = {
            'rfid_number': {'required': False}
        }

    def validate(self, data):
        """Validate card creation data based on card type"""
        card_type = data.get('card_type')
        
        # Validate that correct UUID is provided for card type
        if card_type == 'student' and not data.get('student_uuid'):
            raise serializers.ValidationError("student_uuid is required for student cards.")
        elif card_type == 'staff' and not data.get('staff_uuid'):
            raise serializers.ValidationError("staff_uuid is required for staff cards.")
        elif card_type == 'security' and not data.get('security_uuid'):
            raise serializers.ValidationError("security_uuid is required for security cards.")
        
        # Validate RFID generation/provision
        if not data.get('generate_rfid') and not data.get('rfid_number'):
            raise serializers.ValidationError(
                "Either provide an RFID number or set generate_rfid to true."
            )
        
        if data.get('generate_rfid') and data.get('rfid_number'):
            raise serializers.ValidationError(
                "Cannot both generate RFID and provide custom RFID number."
            )
        
        return data

    def validate_student_uuid(self, value):
        """Validate student exists and doesn't have a card"""
        if not value:
            return value
        try:
            student = Student.objects.get(student_uuid=value, is_active=True)
        except Student.DoesNotExist:
            raise serializers.ValidationError("Student not found or inactive.")
        
        if hasattr(student, 'card'):
            raise serializers.ValidationError(
                f"Student {student.first_name} {student.surname} already has a card assigned."
            )
        return value

    def validate_staff_uuid(self, value):
        """Validate staff exists and doesn't have a card"""
        if not value:
            return value
        try:
            staff = Staff.objects.get(staff_uuid=value, is_active=True)
        except Staff.DoesNotExist:
            raise serializers.ValidationError("Staff member not found or inactive.")
        
        if hasattr(staff, 'card'):
            raise serializers.ValidationError(
                f"Staff {staff.first_name} {staff.surname} already has a card assigned."
            )
        return value

    def validate_security_uuid(self, value):
        """Validate security personnel exists and doesn't have a card"""
        if not value:
            return value
        try:
            security = SecurityPersonnel.objects.get(security_id=value, is_active=True)
        except SecurityPersonnel.DoesNotExist:
            raise serializers.ValidationError("Security personnel not found or inactive.")
        
        if hasattr(security, 'card'):
            raise serializers.ValidationError(
                f"Security personnel {security.full_name} already has a card assigned."
            )
        return value

    def create(self, validated_data):
        card_type = validated_data.pop('card_type')
        student_uuid = validated_data.pop('student_uuid', None)
        staff_uuid = validated_data.pop('staff_uuid', None)
        security_uuid = validated_data.pop('security_uuid', None)
        generate_rfid = validated_data.pop('generate_rfid', False)
        
        # Set card type
        validated_data['card_type'] = card_type
        
        # Get the appropriate card holder
        if card_type == 'student' and student_uuid:
            student = Student.objects.get(student_uuid=student_uuid)
            validated_data['student'] = student
        elif card_type == 'staff' and staff_uuid:
            staff = Staff.objects.get(staff_uuid=staff_uuid)
            validated_data['staff'] = staff
        elif card_type == 'security' and security_uuid:
            security = SecurityPersonnel.objects.get(security_id=security_uuid)
            validated_data['security_personnel'] = security
        
        # Generate RFID if requested
        if generate_rfid:
            # Generate a unique RFID number (you can customize this logic)
            import random
            import string
            while True:
                rfid_number = ''.join(random.choices(string.digits, k=10))
                if not Card.objects.filter(rfid_number=rfid_number).exists():
                    break
            validated_data['rfid_number'] = rfid_number
        
        # Create the card
        return super().create(validated_data)


class CardUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating cards"""
    
    class Meta:
        model = Card
        fields = ['rfid_number', 'is_active', 'expiry_date']

    def validate_rfid_number(self, value):
        """Ensure RFID number is unique when updating"""
        if Card.objects.filter(rfid_number=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("This RFID number is already in use.")
        return value


class CardListSerializer(serializers.ModelSerializer):
    """Serializer for listing cards with minimal card holder info"""
    card_holder_name = serializers.ReadOnlyField()
    card_holder_number = serializers.ReadOnlyField()
    department = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Card
        fields = [
            'card_uuid', 'rfid_number', 'card_type', 'card_holder_name', 'card_holder_number', 
            'department', 'status', 'is_active', 'issued_date', 
            'expiry_date', 'created_at'
        ]

    def get_department(self, obj):
        """Get department based on card type"""
        if obj.card_type == 'student' and obj.student:
            return obj.student.department
        elif obj.card_type == 'staff' and obj.staff:
            return obj.staff.department
        elif obj.card_type == 'security':
            return 'Security'
        return None

    def get_status(self, obj):
        """Get status based on card type"""
        if obj.card_type == 'student' and obj.student:
            return obj.student.student_status
        elif obj.card_type == 'staff' and obj.staff:
            return obj.staff.employment_status
        elif obj.card_type == 'security' and obj.security_personnel:
            return 'Active' if obj.security_personnel.is_active else 'Inactive'
        return None


class StudentWithoutCardSerializer(serializers.ModelSerializer):
    """Serializer for students who don't have cards yet"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'student_uuid', 'registration_number', 'full_name', 
            'department', 'student_status', 'created_at'
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.surname}"


class StaffWithoutCardSerializer(serializers.ModelSerializer):
    """Serializer for staff who don't have cards yet"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Staff
        fields = [
            'staff_uuid', 'staff_number', 'full_name', 
            'department', 'position', 'employment_status', 'created_at'
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.surname}"


class SecurityWithoutCardSerializer(serializers.ModelSerializer):
    """Serializer for security personnel who don't have cards yet"""

    class Meta:
        model = SecurityPersonnel
        fields = [
            'security_id', 'employee_id', 'badge_number', 'full_name', 
            'phone_number', 'hire_date', 'created_at'
        ]