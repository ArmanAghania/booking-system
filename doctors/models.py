from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()


class Specialty(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Specialty"
        verbose_name_plural = "Specialties"
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
    average_rating = models.DecimalField(max_digits=10, decimal_places=2)
    total_reviews = models.IntegerField(default=0)
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="admin_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

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
