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
    surname = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)

    # Academic Information
    registration_number = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=255)
    program = models.CharField(max_length=255)
    soma_class_code = models.CharField(max_length=20, blank=True, null=True)
    
    # Status Fields
    academic_year_status = models.CharField(
        max_length=20,
        choices=ACADEMIC_YEAR_STATUS_CHOICES,
        default='Continuing'
    )
    student_status = models.CharField(
        max_length=20,
        default='Enrolled',
        choices=STUDENT_STATUS_CHOICES,
    )

    # Other Important Fields
    year_of_study = models.IntegerField(null=True, blank=True)
    admission_date = models.DateField(null=True, blank=True)
    expected_graduation_date = models.DateField(null=True, blank=True)
    
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
        ]

