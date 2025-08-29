import uuid
from django.db import models

class SecurityPersonnel(models.Model):
    security_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.CharField(max_length=50, unique=True)
    badge_number = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    hire_date = models.DateField(null=True, blank=True)
    termination_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['employee_id'], name='idx_security_employee_id'),
            models.Index(fields=['badge_number'], name='idx_security_badge'),
            models.Index(fields=['is_active'], name='idx_security_active'),
            models.Index(fields=['deleted_at'], name='idx_security_deleted'),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(termination_date__isnull=True) |
                    models.Q(hire_date__isnull=True) |
                    models.Q(termination_date__gte=models.F('hire_date'))
                ),
                name='check_security_termination_after_hire'
            )
        ]

class PhysicalLocations(models.Model):
    LOCATION_TYPE_CHOICES = [
        ('campus', 'Campus'),
        ('building', 'Building'),
        ('floor', 'Floor'),
        ('room', 'Room'),
        ('gate', 'Gate'),
        ('area', 'Area'),
    ]

    location_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    location_name = models.CharField(max_length=255)
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    is_restricted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['location_name'], name='idx_physical_locations_name'),
            models.Index(fields=['location_type'], name='idx_physical_locations_type'),
            models.Index(fields=['deleted_at'], name='idx_physical_locations_deleted'),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(location_type__in=['campus', 'building', 'floor', 'room', 'gate', 'area'])
                ),
                name='check_physical_locations_type'
            )
        ]



