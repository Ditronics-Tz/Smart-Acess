from django.db import models
import uuid
from django.utils import timezone
from cardmanage.models import Card

# Create your models here.


class AccessLog(models.Model):
    """
    Access log model to track all RFID card access attempts.
    Records both successful and failed access attempts for security auditing.
    """

    ACCESS_STATUS_CHOICES = [
        ('granted', 'Access Granted'),
        ('denied', 'Access Denied'),
    ]

    DENIAL_REASONS = [
        ('invalid_rfid', 'Invalid RFID Number'),
        ('card_inactive', 'Card is Inactive'),
        ('card_expired', 'Card has Expired'),
        ('student_inactive', 'Student is Inactive'),
        ('system_error', 'System Error'),
    ]

    log_uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique identifier for the access log entry"
    )

    rfid_number = models.CharField(
        max_length=50,
        help_text="RFID number that was scanned",
        db_index=True
    )

    card = models.ForeignKey(
        Card,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='access_logs',
        help_text="Card associated with the RFID (if found)"
    )

    access_status = models.CharField(
        max_length=20,
        choices=ACCESS_STATUS_CHOICES,
        help_text="Whether access was granted or denied"
    )

    denial_reason = models.CharField(
        max_length=30,
        choices=DENIAL_REASONS,
        null=True,
        blank=True,
        help_text="Reason for access denial (if applicable)"
    )

    access_location = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Location where access was attempted (optional)"
    )

    device_identifier = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Identifier of the device that made the request (optional)"
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the requesting device"
    )

    # Timing information
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp when access was attempted",
        db_index=True
    )

    response_time_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Response time in milliseconds (optional)"
    )

    # System fields
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status_display = "✓" if self.access_status == 'granted' else "✗"
        card_info = f" - {self.card.student.first_name} {self.card.student.surname}" if self.card else ""
        return f"{status_display} {self.rfid_number} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}{card_info}"

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['rfid_number']),
            models.Index(fields=['access_status']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['card']),
            # Optimized composite indexes for common queries
            models.Index(fields=['rfid_number', 'timestamp']),  # For RFID history
            models.Index(fields=['access_status', 'timestamp']),  # For status reports
        ]
        verbose_name = "Access Log"
        verbose_name_plural = "Access Logs"
