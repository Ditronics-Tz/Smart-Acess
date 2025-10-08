from django.db import models
import uuid
from students.models import Student
import random
import string

# Create your models here.


class Card(models.Model):
    

    card_uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique identifier for the card"
    )

    rfid_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="RFID number of the physical card",
        db_index=True  # Keep this for fast lookups
    )

    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name='card',
        help_text="Student associated with this card"
    )

    # Card status and lifecycle
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the card is currently active"
    )

    issued_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date when the card was issued"
    )

    expiry_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date when the card expires (optional)"
    )

    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Card {self.card_uuid} - {self.student.first_name} {self.student.surname}"
    
    def generate_doi_code(self):
        """Generate unique DOI code for the card"""
        prefix = "DGBC"
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"{prefix} {code}"
    
    def save(self, *args, **kwargs):
        """Override save to generate DOI if not exists"""
        if not hasattr(self, 'doi_code') or not self.doi_code:
            # This will be used when we add doi_code field
            pass
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['rfid_number']),  # Primary lookup index
            models.Index(fields=['card_uuid']),
            models.Index(fields=['is_active']),
            models.Index(fields=['student']),
        ]


class IDCardPrintLog(models.Model):
    """Track ID card printing activities"""
    id = models.AutoField(primary_key=True)
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='print_logs')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='card_print_logs')
    
    # Print details
    printed_at = models.DateTimeField(auto_now_add=True)
    printed_by = models.CharField(max_length=255, help_text="Username of who printed the card")
    user_type = models.CharField(max_length=50, help_text="User type (administrator/registration_officer)")
    
    # PDF tracking
    pdf_generated = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Print: {self.student.registration_number} at {self.printed_at}"
    
    class Meta:
        ordering = ['-printed_at']
        indexes = [
            models.Index(fields=['card']),
            models.Index(fields=['student']),
            models.Index(fields=['printed_at']),
        ]


class IDCardVerificationLog(models.Model):
    """Track QR code scans/verifications"""
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='verification_logs')
    
    # Verification details
    verified_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True, help_text="Browser/device information")
    
    # Location if available
    verification_source = models.CharField(
        max_length=50, 
        default='qr_scan',
        help_text="How verification was initiated (qr_scan, direct_link, etc)"
    )
    
    def __str__(self):
        return f"Verification: {self.student.registration_number} at {self.verified_at}"
    
    class Meta:
        ordering = ['-verified_at']
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['verified_at']),
        ]
