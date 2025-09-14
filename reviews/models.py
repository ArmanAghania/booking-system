# reviews/models.py

from django.db import models
from django.db.models import Avg
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from doctors.models import Doctor


class Review(models.Model):

    appointment = models.OneToOneField(
        'appointments.Appointment',
        on_delete=models.CASCADE,
        related_name='review'
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_given'
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='reviews_received'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(
        blank=True,
        default='',
        help_text="Optional detailed feedback from the patient."
    )
    is_anonymous = models.BooleanField(
        default=False,
        help_text="If true, the patient's name will be hidden in the review."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Review for Dr. {self.doctor} by {self.patient} (Rating: {self.rating})"

    def _update_doctor_rating(self):
        reviews = Review.objects.filter(doctor=self.doctor)
        aggregation = reviews.aggregate(average_rating=Avg('rating'))
        self.doctor.total_reviews = reviews.count()
        self.doctor.average_rating = aggregation['average_rating'] or 0.00
        self.doctor.save(update_fields=['average_rating', 'total_reviews'])

    def clean(self):
        super().clean()
        if self.appointment and self.patient != self.appointment.patient:
            raise ValidationError("You can only review your own appointments.")

    def save(self, *args, **kwargs):
        if self.appointment:
            self.patient = self.appointment.patient
            self.doctor = self.appointment.doctor
        self.full_clean()
        super().save(*args, **kwargs)
        self._update_doctor_rating()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self._update_doctor_rating()

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["doctor"]),
            models.Index(fields=["patient"]),
        ]