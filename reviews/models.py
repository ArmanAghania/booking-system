# reviews/models.py

from django.db import models
from django.db.models import Avg
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from appointments.models import Appointment
from doctors.models import Doctor

class Review(models.Model):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name="review"
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_given"
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="reviews_received"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review for Dr. {self.doctor.user.get_full_name()} by {self.patient.get_full_name()}"

    def save(self, *args, **kwargs):
        # Automatically set the patient and doctor from the appointment
        self.patient = self.appointment.patient
        self.doctor = self.appointment.doctor
        super().save(*args, **kwargs)
        # After saving, update the doctor's average rating
        self._update_doctor_rating()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        # Also update the rating after a review is deleted
        self._update_doctor_rating()

    def _update_doctor_rating(self):
        # This function calculates and saves the new average rating for the doctor
        reviews = Review.objects.filter(doctor=self.doctor)
        aggregation = reviews.aggregate(average_rating=Avg('rating'))
        self.doctor.total_reviews = reviews.count()
        self.doctor.average_rating = aggregation['average_rating'] or 0.00
        self.doctor.save(update_fields=['average_rating', 'total_reviews'])