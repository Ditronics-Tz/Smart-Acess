import uuid
from django.db import models
from rest_framework import serializers, viewsets, routers


class Student(models.Model):

    ACADEMIC_YEAR_STATUS_CHOICES = [
            ('Continuing', 'Continuing'),
        ('Retake', 'Retake'),
        ('Deferred', 'Deferred'),
        ('Probation', 'Probation'),
        ('Completed', 'Completed'),
    ]
    STUDENT_STATUS_CHOICES = [
        ('Enrolled', 'Enrolled'),
        ('Withdrawn', 'Withdrawn'),
        ('Suspended', 'Suspended'),
    ]


    student_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # Personal Information
    surname = models.CharField(max_length=100, help_text="Your Surname")
    first_name = models.CharField(max_length=100, help_text="Your First Name")
    middle_name = models.CharField(max_length=100, blank=True, null=True, help_text="Your Middle Name")
    mobile_phone = models.CharField(max_length=15, blank=True, null=True, help_text="Your Active Mobile Phone number")
    
    # Academic Information
    registration_number = models.CharField(max_length=20, unique=True, help_text="Your Registration Number")
    department = models.CharField(max_length=255, help_text="Your Department")
    soma_class_code = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        help_text="Your SOMA Class (e.g., OD24CE, BENG24EE, ME24SE etc)"
    )
    
    # Status Fields
    academic_year_status = models.CharField(
        max_length=20,
        choices=ACADEMIC_YEAR_STATUS_CHOICES,
        default='Continuing',
        help_text="Your Status in Academic Year 2024/25"
    )
    student_status = models.CharField(
        max_length=20,
        default='Enrolled',
        choices=STUDENT_STATUS_CHOICES,
    )

    # Other Important Fields
    
    # System and Auditing Fields
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.surname} ({self.registration_number})"

    class Meta:
        # This improves performance by telling the database how to index these fields.
        indexes = [
            models.Index(fields=['registration_number']),
            models.Index(fields=['surname', 'first_name']),
            models.Index(fields=['mobile_phone']),
            models.Index(fields=['department']),
        ]


class StudentPhoto(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='photo')
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.student}"

