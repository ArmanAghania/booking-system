from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings
import random
import string


class User(AbstractUser):

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
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Account creation timestamp"
    )
    updated_at = models.DateTimeField(auto_now=True, help_text="Last update timestamp")
    is_verified = models.BooleanField(
        default=False, help_text="Whether the user's email is verified"
    )
    profile_picture_url = models.URLField(
        blank=True, null=True, help_text="URL to user's profile picture"
    )

    class Meta:
        db_table = "auth_user"


class OTP(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otps"
    )
    code = models.CharField(max_length=10, help_text="OTP code")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    purpose = models.CharField(
        max_length=20,
        default="verification",
        help_text="Purpose of the OTP (verification, password_reset, etc.)",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_used"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"OTP for {self.user.email} - {self.code}"

    @classmethod
    def generate_otp(cls, user, purpose="verification"):
        """Generate a new OTP for the user."""
        cls.objects.filter(user=user, is_used=False).update(is_used=True)

        code = "".join(random.choices(string.digits, k=settings.OTP_LENGTH))

        expires_at = timezone.now() + timezone.timedelta(
            minutes=settings.OTP_EXPIRY_MINUTES
        )

        otp = cls.objects.create(
            user=user, code=code, expires_at=expires_at, purpose=purpose
        )

        return otp

    def is_valid(self):
        return not self.is_used and timezone.now() <= self.expires_at

    def mark_as_used(self):
        self.is_used = True
        self.save()
