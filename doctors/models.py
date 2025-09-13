from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

# Create your models here.
User = get_user_model()


class Specialty(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the medical specialty (e.g., Cardiology, Neurology)",
    )
    description = models.TextField(help_text="Detailed description of the specialty")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def clean(self):
        """Validate specialty data."""
        super().clean()

        # Ensure name is not empty or just whitespace
        if not self.name or not self.name.strip():
            raise ValidationError("Specialty name cannot be empty.")

        # Ensure description is not empty
        if not self.description or not self.description.strip():
            raise ValidationError("Specialty description cannot be empty.")

        # Check for duplicate names (case-insensitive)
        if self.name:
            existing = Specialty.objects.filter(name__iexact=self.name.strip())
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError("A specialty with this name already exists.")

    def save(self, *args, **kwargs):
        """Override save to run validation and clean data."""
        # Clean and strip whitespace
        self.name = self.name.strip() if self.name else ""
        self.description = self.description.strip() if self.description else ""

        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Specialty"
        verbose_name_plural = "Specialties"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
        ]


class Doctor(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.PROTECT, related_name="doctor_profile"
    )
    specialty = models.ForeignKey(Specialty, on_delete=models.PROTECT)
    license_number = models.CharField(max_length=255, unique=True)
    experience_years = models.IntegerField()
    bio = models.TextField()
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    average_rating = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_reviews = models.IntegerField(default=0)
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="admin_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

    def clean(self):
        """Validate doctor model data."""
        super().clean()

        # Validate experience years
        if self.experience_years is not None and self.experience_years < 0:
            raise ValidationError("Experience years cannot be negative.")

        # Validate consultation fee
        if self.consultation_fee < 0:
            raise ValidationError("Consultation fee cannot be negative.")

        # Validate license number uniqueness
        if self.license_number:
            existing = Doctor.objects.filter(license_number=self.license_number)
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError(
                    "A doctor with this license number already exists."
                )

    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.clean()
        super().save(*args, **kwargs)

    @classmethod
    def create_doctor(cls, user_data, doctor_data, created_by):
        """
        Class method to create a doctor with proper validation.
        This ensures business logic is centralized and reusable.
        """
        # Validate that created_by has admin permissions
        if not created_by.is_authenticated:
            raise ValidationError("User must be authenticated.")

        # Check if user is either a superuser OR has admin user type
        is_superuser = created_by.is_superuser
        is_admin_type = getattr(created_by, "user_type", None) == "admin"

        if not (is_superuser or is_admin_type):
            raise ValidationError(
                "Only superusers or users with admin type can create doctor accounts."
            )

        # Create user account
        user = User.objects.create_user(
            username=user_data["username"],
            email=user_data["email"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            phone_number=user_data["phone_number"],
            wallet_balance=user_data.get("wallet_balance", 0.00),
            user_type="doctor",
            is_staff=True,
            is_active=True,
        )

        # Create doctor profile
        doctor_data["user"] = user
        doctor_data["created_by"] = created_by
        doctor = cls(**doctor_data)
        doctor.save()

        return doctor

    class Meta:
        verbose_name = "Doctor"
        verbose_name_plural = "Doctors"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["specialty"]),
            models.Index(fields=["license_number"]),
            models.Index(fields=["experience_years"]),
            models.Index(fields=["consultation_fee"]),
        ]
