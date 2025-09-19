from django.contrib import admin
from .models import AccessLog

# Register your models here.


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    """
    Admin interface for AccessLog model.
    """
    list_display = [
        'log_uuid', 'rfid_number', 'get_student_name', 'access_status',
        'denial_reason', 'access_location', 'timestamp'
    ]
    list_filter = [
        'access_status', 'denial_reason', 'access_location', 
        'device_identifier', 'timestamp'
    ]
    search_fields = [
        'rfid_number', 'card__student__first_name', 'card__student__surname',
        'card__student__registration_number', 'access_location'
    ]
    readonly_fields = [
        'log_uuid', 'rfid_number', 'card', 'access_status', 'denial_reason',
        'access_location', 'device_identifier', 'ip_address', 'timestamp',
        'response_time_ms', 'created_at'
    ]
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    def get_student_name(self, obj):
        """Get the student name from the associated card."""
        if obj.card and obj.card.student:
            return f"{obj.card.student.first_name} {obj.card.student.surname}"
        return "Unknown"
    get_student_name.short_description = "Student Name"
    get_student_name.admin_order_field = 'card__student__surname'
    
    def has_add_permission(self, request):
        """Disable adding access logs through admin (should only be created via API)."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable changing access logs (they should be immutable)."""
        return False
