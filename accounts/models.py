from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with additional fields."""

    USER_TYPE_CHOICES = [
        ("admin", "Admin"),
        ("doctor", "Doctor"),
        ("patient", "Patient"),
    ]

    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default="patient",
        help_text="Type of user account",
    )
    phone_number = models.CharField(
        max_length=20, blank=True, help_text="Contact phone number"
    )
    wallet_balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, help_text="User's wallet balance"
    )

    class Meta:
        db_table = "auth_user"
