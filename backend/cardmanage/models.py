from django.db import models
import uuid
from students.models import Student

# Create your models here.


class Card(models.Model):
    """
    Card model representing RFID access cards for students.
    Each student can have only one active card.
    """

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

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['rfid_number']),  # Primary lookup index
            models.Index(fields=['card_uuid']),
            models.Index(fields=['is_active']),
            models.Index(fields=['student']),
        ]
