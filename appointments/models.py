from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class TimeSlot(models.Model):
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='time_slots')

    date = models.DateField(verbose_name="TimeSlot Date")

    start_time = models.TimeField(verbose_name="Start Time")
    end_time = models.TimeField(verbose_name="End Time")

    is_available = models.BooleanField(default=True, verbose_name="Available")

    created_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,
                                   related_name='created_timeslots'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Time Slot"
        verbose_name_plural = "Time Slots"
        unique_together = [['doctor', 'date', 'start_time', 'end_time']]
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"Dr.{self.doctor} - {self.date} ({self.start_time} - {self.end_time})"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")

        from django.utils import timezone
        if self.date and self.date < timezone.now().date():
            raise ValidationError("Cannot create time slots for past dates.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Appointment(models.Model):
    STATUS_CHOICES = [("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
        ("COMPLETED", "Completed"),
    ]

    patient = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="appointments"
    )

    doctor = models.ForeignKey(
        "doctors.Doctor",
        on_delete=models.CASCADE,
        related_name="appointments"
    )
    time_slot = models.OneToOneField(
        "appointments.TimeSlot",
        on_delete=models.CASCADE,
        related_name="appointment"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )
    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    notes = models.TextField(blank=True, null=True)
    confirmation_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Appointment: {self.patient} with {self.doctor} on {self.time_slot}"
