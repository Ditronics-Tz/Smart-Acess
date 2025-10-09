from django.contrib import admin
from .models import Staff, StaffPhoto

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


@admin.register(StaffPhoto)
class StaffPhotoAdmin(admin.ModelAdmin):
    list_display = ['staff', 'uploaded_at', 'get_photo_preview']
    list_filter = ['uploaded_at']
    search_fields = ['staff__staff_number', 'staff__first_name', 'staff__surname']
    readonly_fields = ['uploaded_at']
    ordering = ['-uploaded_at']

    fieldsets = (
        ('Staff Information', {
            'fields': ('staff',)
        }),
        ('Photo', {
            'fields': ('photo',)
        }),
        ('Upload Information', {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )

    def get_photo_preview(self, obj):
        if obj.photo:
            return f'<img src="{obj.photo.url}" style="max-height: 50px; max-width: 50px;" />'
        return "No photo"
    get_photo_preview.short_description = "Photo Preview"
    get_photo_preview.allow_tags = True
