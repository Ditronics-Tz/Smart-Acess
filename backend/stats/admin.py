from django.contrib import admin
from .models import AnalyticsSnapshot, SystemAlert, ReportCache

# Register your models here.

@admin.register(AnalyticsSnapshot)
class AnalyticsSnapshotAdmin(admin.ModelAdmin):
    list_display = [
        'snapshot_id', 'report_type', 'snapshot_date', 
        'total_users', 'total_cards', 'daily_verifications'
    ]
    list_filter = ['report_type', 'snapshot_date']
    search_fields = ['snapshot_id']
    readonly_fields = ['snapshot_id', 'created_at']
    date_hierarchy = 'snapshot_date'
    ordering = ['-snapshot_date']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('snapshot_id', 'report_type', 'snapshot_date')
        }),
        ('User Metrics', {
            'fields': ('total_users', 'total_students', 'total_staff', 'total_security')
        }),
        ('Card Metrics', {
            'fields': ('total_cards', 'active_cards')
        }),
        ('Activity Metrics', {
            'fields': ('daily_verifications', 'daily_card_prints')
        }),
        ('System Health', {
            'fields': ('active_gates', 'total_gates')
        }),
        ('Photo Completion', {
            'fields': ('student_photo_completion_rate', 'staff_photo_completion_rate')
        }),
        ('Raw Data', {
            'fields': ('raw_data',),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )


@admin.register(SystemAlert)
class SystemAlertAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'alert_type', 'severity', 'is_active', 
        'created_at', 'acknowledged_by', 'resolved_at'
    ]
    list_filter = ['alert_type', 'severity', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'acknowledged_by']
    readonly_fields = ['alert_id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    actions = ['mark_acknowledged', 'mark_resolved']
    
    fieldsets = (
        ('Alert Info', {
            'fields': ('alert_id', 'alert_type', 'severity', 'title', 'description')
        }),
        ('Metrics', {
            'fields': ('metric_value', 'threshold_value')
        }),
        ('Status', {
            'fields': ('is_active', 'acknowledged_at', 'acknowledged_by', 'resolved_at')
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def mark_acknowledged(self, request, queryset):
        from django.utils import timezone
        queryset.update(
            acknowledged_at=timezone.now(),
            acknowledged_by=request.user.username
        )
        self.message_user(request, f"Marked {queryset.count()} alerts as acknowledged.")
    mark_acknowledged.short_description = "Mark selected alerts as acknowledged"
    
    def mark_resolved(self, request, queryset):
        from django.utils import timezone
        queryset.update(
            is_active=False,
            resolved_at=timezone.now()
        )
        self.message_user(request, f"Marked {queryset.count()} alerts as resolved.")
    mark_resolved.short_description = "Mark selected alerts as resolved"


@admin.register(ReportCache)
class ReportCacheAdmin(admin.ModelAdmin):
    list_display = ['cache_key', 'expires_at', 'is_expired', 'created_at']
    list_filter = ['expires_at', 'created_at']
    search_fields = ['cache_key']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    actions = ['clear_expired_cache']
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'
    
    def clear_expired_cache(self, request, queryset):
        from django.utils import timezone
        expired_count = queryset.filter(expires_at__lt=timezone.now()).count()
        queryset.filter(expires_at__lt=timezone.now()).delete()
        self.message_user(request, f"Cleared {expired_count} expired cache entries.")
    clear_expired_cache.short_description = "Clear expired cache entries"
