from rest_framework import serializers
from .models import AccessLog
from cardmanage.models import Card
from students.models import Student


class AccessRequestSerializer(serializers.Serializer):
    """
    Serializer for RFID access requests.
    """
    rfid_number = serializers.CharField(
        max_length=50,
        required=True,
        help_text="RFID number to check for access"
    )
    
    access_location = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="Optional location identifier"
    )
    
    device_identifier = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="Optional device identifier"
    )

    def validate_rfid_number(self, value):
        """
        Validate RFID number format.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("RFID number cannot be empty.")
        
        # Remove any whitespace
        value = value.strip()
        
        # Basic validation - adjust based on your RFID format requirements
        if len(value) < 3:
            raise serializers.ValidationError("RFID number is too short.")
        
        return value


class AccessResponseSerializer(serializers.Serializer):
    """
    Serializer for RFID access responses.
    """
    success = serializers.BooleanField(help_text="Whether the request was processed successfully")
    access_granted = serializers.BooleanField(help_text="Whether access was granted")
    message = serializers.CharField(help_text="Human-readable message")
    rfid_number = serializers.CharField(help_text="The RFID number that was checked")
    timestamp = serializers.DateTimeField(help_text="Timestamp of the access attempt")
    log_uuid = serializers.UUIDField(help_text="Unique identifier for this access log entry")
    
    # Optional student information (only included if access is granted)
    student_info = serializers.DictField(required=False, help_text="Student information if access granted")
    
    # Additional information
    denial_reason = serializers.CharField(required=False, help_text="Reason for denial if access was denied")
    card_status = serializers.CharField(required=False, help_text="Status of the card")


class StudentInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for basic student information in access responses.
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = [
            'student_uuid', 'registration_number', 'first_name', 
            'surname', 'full_name', 'department', 'student_status'
        ]
        read_only_fields = fields
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.surname}"


class CardInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for basic card information in access responses.
    """
    student = StudentInfoSerializer(read_only=True)
    
    class Meta:
        model = Card
        fields = [
            'card_uuid', 'rfid_number', 'is_active', 
            'issued_date', 'expiry_date', 'student'
        ]
        read_only_fields = fields


class AccessLogSerializer(serializers.ModelSerializer):
    """
    Serializer for access log entries.
    """
    card = CardInfoSerializer(read_only=True)
    access_status_display = serializers.CharField(source='get_access_status_display', read_only=True)
    denial_reason_display = serializers.CharField(source='get_denial_reason_display', read_only=True)
    
    class Meta:
        model = AccessLog
        fields = [
            'log_uuid', 'rfid_number', 'card', 'access_status', 
            'access_status_display', 'denial_reason', 'denial_reason_display',
            'access_location', 'device_identifier', 'ip_address', 
            'timestamp', 'response_time_ms', 'created_at'
        ]
        read_only_fields = fields


class AccessLogListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for access log list views.
    """
    student_name = serializers.SerializerMethodField()
    access_status_display = serializers.CharField(source='get_access_status_display', read_only=True)
    
    class Meta:
        model = AccessLog
        fields = [
            'log_uuid', 'rfid_number', 'student_name', 'access_status', 
            'access_status_display', 'denial_reason', 'access_location',
            'timestamp'
        ]
        read_only_fields = fields
    
    def get_student_name(self, obj):
        if obj.card and obj.card.student:
            return f"{obj.card.student.first_name} {obj.card.student.surname}"
        return "Unknown"


class AccessStatisticsSerializer(serializers.Serializer):
    """
    Serializer for access statistics.
    """
    total_attempts = serializers.IntegerField()
    granted_access = serializers.IntegerField()
    denied_access = serializers.IntegerField()
    success_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Time-based statistics
    attempts_today = serializers.IntegerField()
    attempts_this_week = serializers.IntegerField()
    attempts_this_month = serializers.IntegerField()
    
    # Denial reasons breakdown
    denial_reasons = serializers.DictField()
    
    # Top locations
    top_locations = serializers.ListField()
    
    # Recent activity
    recent_activity = AccessLogListSerializer(many=True)
    
    # Generated information
    generated_at = serializers.DateTimeField()
    generated_by = serializers.CharField()