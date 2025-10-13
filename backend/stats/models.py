from django.db import models
import uuid
from django.utils import timezone

# Create your models here.

class AnalyticsSnapshot(models.Model):
    """
    Store periodic snapshots of system analytics for historical tracking
    """
    REPORT_TYPES = [
        ('daily', 'Daily Report'),
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('comprehensive', 'Comprehensive Report'),
    ]
    
    snapshot_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    snapshot_date = models.DateTimeField(default=timezone.now)
    
    # Metrics data (stored as JSON)
    total_users = models.IntegerField(default=0)
    total_students = models.IntegerField(default=0)
    total_staff = models.IntegerField(default=0)
    total_security = models.IntegerField(default=0)
    total_cards = models.IntegerField(default=0)
    active_cards = models.IntegerField(default=0)
    
    # Activity metrics
    daily_verifications = models.IntegerField(default=0)
    daily_card_prints = models.IntegerField(default=0)
    
    # System health metrics
    active_gates = models.IntegerField(default=0)
    total_gates = models.IntegerField(default=0)
    
    # Photo completion rates
    student_photo_completion_rate = models.FloatField(default=0.0)
    staff_photo_completion_rate = models.FloatField(default=0.0)
    
    # Raw JSON data for detailed analytics
    raw_data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-snapshot_date']
        indexes = [
            models.Index(fields=['report_type', 'snapshot_date']),
            models.Index(fields=['snapshot_date']),
        ]
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.snapshot_date.date()}"


class SystemAlert(models.Model):
    """
    Store system alerts and notifications based on analytics
    """
    ALERT_TYPES = [
        ('low_photo_completion', 'Low Photo Completion Rate'),
        ('high_verification_failure', 'High Verification Failure Rate'),
        ('gate_offline', 'Gate Offline'),
        ('unusual_activity', 'Unusual Activity Pattern'),
        ('data_integrity', 'Data Integrity Issue'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    alert_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Alert data
    metric_value = models.FloatField(null=True, blank=True)
    threshold_value = models.FloatField(null=True, blank=True)
    
    # Status tracking
    is_active = models.BooleanField(default=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.CharField(max_length=255, null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['alert_type', 'is_active']),
            models.Index(fields=['severity', 'is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        status = "Active" if self.is_active else "Resolved"
        return f"{self.title} ({self.get_severity_display()}) - {status}"


class ReportCache(models.Model):
    """
    Cache frequently requested reports to improve performance
    """
    cache_key = models.CharField(max_length=255, unique=True)
    report_data = models.JSONField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['cache_key']),
            models.Index(fields=['expires_at']),
        ]
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"Cache: {self.cache_key} (expires: {self.expires_at})"
