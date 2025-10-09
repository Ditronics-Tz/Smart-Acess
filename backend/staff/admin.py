from django.contrib import admin
from .models import Staff

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = [
        'staff_number', 'get_full_name', 'department', 'position',
        'employment_status', 'is_active', 'created_at'
    ]
    list_filter = [
        'department', 'position', 'employment_status', 'is_active', 'created_at'
    ]
    search_fields = [
        'staff_number', 'first_name', 'surname', 'department', 'position'
    ]
    ordering = ['-created_at']
    readonly_fields = ['staff_uuid', 'created_at', 'updated_at']

    fieldsets = (
        ('Personal Information', {
            'fields': ('staff_uuid', 'surname', 'first_name', 'middle_name', 'mobile_phone')
        }),
        ('Employment Information', {
            'fields': ('staff_number', 'department', 'position', 'employment_status')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.surname}"
    get_full_name.short_description = "Full Name"
