from django.db import models
import uuid
from students.models import Student
from staff.models import Staff
from adminstrator.models import SecurityPersonnel
import random
import string

# Create your models here.


class Card(models.Model):
    CARD_TYPE_CHOICES = [
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('security', 'Security Personnel'),
    ]

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

    # Card type to identify what kind of card this is
    card_type = models.CharField(
        max_length=20,
        choices=CARD_TYPE_CHOICES,
        help_text="Type of card (student, staff, security)"
    )

    # Relationships - only one should be filled based on card_type
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name='card',
        null=True,
        blank=True,
        help_text="Student associated with this card"
    )

    staff = models.OneToOneField(
        Staff,
        on_delete=models.CASCADE,
        related_name='card',
        null=True,
        blank=True,
        help_text="Staff member associated with this card"
    )

    security_personnel = models.OneToOneField(
        SecurityPersonnel,
        on_delete=models.CASCADE,
        related_name='card',
        null=True,
        blank=True,
        help_text="Security personnel associated with this card"
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
        if self.card_type == 'student' and self.student:
            return f"Card {self.card_uuid} - {self.student.first_name} {self.student.surname}"
        elif self.card_type == 'staff' and self.staff:
            return f"Card {self.card_uuid} - {self.staff.first_name} {self.staff.surname} (Staff)"
        elif self.card_type == 'security' and self.security_personnel:
            return f"Card {self.card_uuid} - {self.security_personnel.full_name} (Security)"
        else:
            return f"Card {self.card_uuid} - {self.card_type}"
    
    @property
    def card_holder(self):
        """Return the card holder object based on card type"""
        if self.card_type == 'student':
            return self.student
        elif self.card_type == 'staff':
            return self.staff
        elif self.card_type == 'security':
            return self.security_personnel
        return None
    
    @property
    def card_holder_name(self):
        """Return the full name of the card holder"""
        holder = self.card_holder
        if holder:
            if self.card_type == 'security':
                return holder.full_name
            else:
                return f"{holder.first_name} {holder.surname}"
        return "Unknown"
    
    @property
    def card_holder_number(self):
        """Return the identification number of the card holder"""
        holder = self.card_holder
        if holder:
            if self.card_type == 'student':
                return holder.registration_number
            elif self.card_type == 'staff':
                return holder.staff_number
            elif self.card_type == 'security':
                return holder.employee_id
        return None
    
    def generate_doi_code(self):
        """Generate unique DOI code for the card"""
        prefix = "DGBC"
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"{prefix} {code}"
    
    def clean(self):
        """Validate that only one relationship is set based on card_type"""
        from django.core.exceptions import ValidationError
        
        if self.card_type == 'student' and not self.student:
            raise ValidationError("Student must be specified for student cards")
        elif self.card_type == 'staff' and not self.staff:
            raise ValidationError("Staff must be specified for staff cards")
        elif self.card_type == 'security' and not self.security_personnel:
            raise ValidationError("Security personnel must be specified for security cards")
        
        # Ensure only the correct relationship is set
        if self.card_type == 'student':
            self.staff = None
            self.security_personnel = None
        elif self.card_type == 'staff':
            self.student = None
            self.security_personnel = None
        elif self.card_type == 'security':
            self.student = None
            self.staff = None

    def save(self, *args, **kwargs):
        """Override save to validate and generate DOI if not exists"""
        self.clean()
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
            models.Index(fields=['card_type']),
            models.Index(fields=['student']),
            models.Index(fields=['staff']),
            models.Index(fields=['security_personnel']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(card_type__in=['student', 'staff', 'security']),
                name='check_card_type_valid'
            ),
        ]


class IDCardPrintLog(models.Model):
    """Track ID card printing activities"""
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='print_logs')
    
    # Optional relationships based on card type
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='card_print_logs', null=True, blank=True)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='card_print_logs', null=True, blank=True)
    security_personnel = models.ForeignKey(SecurityPersonnel, on_delete=models.CASCADE, related_name='card_print_logs', null=True, blank=True)
    
    # Print details
    printed_at = models.DateTimeField(auto_now_add=True)
    printed_by = models.CharField(max_length=255, help_text="Username of who printed the card")
    user_type = models.CharField(max_length=50, help_text="User type (administrator/registration_officer)")
    
    # PDF tracking
    pdf_generated = models.BooleanField(default=True)
    
    def __str__(self):
        if self.student:
            return f"Print: {self.student.registration_number} at {self.printed_at}"
        elif self.staff:
            return f"Print: {self.staff.staff_number} at {self.printed_at}"
        elif self.security_personnel:
            return f"Print: {self.security_personnel.employee_id} at {self.printed_at}"
        else:
            return f"Print: Card {self.card.card_uuid} at {self.printed_at}"
    
    class Meta:
        ordering = ['-printed_at']
        indexes = [
            models.Index(fields=['card']),
            models.Index(fields=['student']),
            models.Index(fields=['printed_at']),
        ]


class IDCardVerificationLog(models.Model):
    """Track QR code scans/verifications"""
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    
    # Optional relationships based on card type
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='verification_logs', null=True, blank=True)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='verification_logs', null=True, blank=True)
    security_personnel = models.ForeignKey(SecurityPersonnel, on_delete=models.CASCADE, related_name='verification_logs', null=True, blank=True)
    
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
        if self.student:
            return f"Verification: {self.student.registration_number} at {self.verified_at}"
        elif self.staff:
            return f"Verification: {self.staff.staff_number} at {self.verified_at}"
        elif self.security_personnel:
            return f"Verification: {self.security_personnel.employee_id} at {self.verified_at}"
        else:
            return f"Verification at {self.verified_at}"
    
    class Meta:
        ordering = ['-verified_at']
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['verified_at']),
        ]
