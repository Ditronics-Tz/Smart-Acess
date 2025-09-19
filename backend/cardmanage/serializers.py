from rest_framework import serializers
from .models import Card
from students.models import Student
from students.serializers import StudentSerializer
import uuid


class CardSerializer(serializers.ModelSerializer):
    student_info = StudentSerializer(source='student', read_only=True)
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
    department = serializers.CharField(
        source='student.department', 
        read_only=True
    )

    class Meta:
        model = Card
        fields = '__all__'
        read_only_fields = ['card_uuid', 'issued_date', 'created_at', 'updated_at']

    def validate_student(self, value):
        """Ensure student doesn't already have a card"""
        if hasattr(value, 'card'):
            raise serializers.ValidationError(
                f"Student {value.first_name} {value.surname} already has a card assigned."
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
    """Serializer for creating cards with student selection"""
    student_uuid = serializers.UUIDField(write_only=True)
    generate_rfid = serializers.BooleanField(write_only=True, default=False)
    
    class Meta:
        model = Card
        fields = ['student_uuid', 'rfid_number', 'expiry_date', 'generate_rfid']
        extra_kwargs = {
            'rfid_number': {'required': False}
        }

    def validate_student_uuid(self, value):
        """Validate student exists and doesn't have a card"""
        try:
            student = Student.objects.get(student_uuid=value, is_active=True)
        except Student.DoesNotExist:
            raise serializers.ValidationError("Student not found or inactive.")
        
        if hasattr(student, 'card'):
            raise serializers.ValidationError(
                f"Student {student.first_name} {student.surname} already has a card assigned."
            )
        return value

    def validate(self, data):
        """Validate RFID number is provided or should be generated"""
        if not data.get('generate_rfid') and not data.get('rfid_number'):
            raise serializers.ValidationError(
                "Either provide an RFID number or set generate_rfid to true."
            )
        
        if data.get('generate_rfid') and data.get('rfid_number'):
            raise serializers.ValidationError(
                "Cannot both generate RFID and provide custom RFID number."
            )
        
        return data

    def create(self, validated_data):
        student_uuid = validated_data.pop('student_uuid')
        generate_rfid = validated_data.pop('generate_rfid', False)
        
        # Get the student
        student = Student.objects.get(student_uuid=student_uuid)
        
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
        validated_data['student'] = student
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
    """Serializer for listing cards with minimal student info"""
    student_name = serializers.SerializerMethodField()
    registration_number = serializers.CharField(
        source='student.registration_number', 
        read_only=True
    )
    department = serializers.CharField(
        source='student.department', 
        read_only=True
    )
    student_status = serializers.CharField(
        source='student.student_status', 
        read_only=True
    )

    class Meta:
        model = Card
        fields = [
            'card_uuid', 'rfid_number', 'student_name', 'registration_number', 
            'department', 'student_status', 'is_active', 'issued_date', 
            'expiry_date', 'created_at'
        ]

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.surname}"


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