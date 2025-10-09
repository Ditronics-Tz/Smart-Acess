from django.db import models
import uuid

class Staff(models.Model):
    EMPLOYMENT_STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Terminated', 'Terminated'),
        ('Retired', 'Retired'),
        ('On Leave', 'On Leave'),
    ]

    staff_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    surname = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    mobile_phone = models.CharField(max_length=15, blank=True, null=True)
    staff_number = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=255)
    position = models.CharField(max_length=100)
    employment_status = models.CharField(max_length=50, choices=EMPLOYMENT_STATUS_CHOICES, default='Active')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.surname} ({self.staff_number})"

    class Meta:
        indexes = [
            models.Index(fields=['staff_number']),
            models.Index(fields=['surname', 'first_name']),
            models.Index(fields=['mobile_phone']),
            models.Index(fields=['department']),
        ]


class StaffPhoto(models.Model):
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE, related_name='photo')
    photo = models.ImageField(upload_to='staff_photos/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.staff}"
