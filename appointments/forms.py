# appointments/forms.py
from datetime import time
from django import forms
from .models import Appointment, TimeSlot


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["notes"]
        widgets = {
            "notes": forms.Textarea(
                attrs={
                    "class": "w-full border rounded px-3 py-2",
                    "rows": 4,
                    "placeholder": "Enter any notes for the doctor...",
                }
            ),
        }


TIME_CHOICES = [
    # Morning slots
    (time(9, 0), "09:00 - 09:15"),
    (time(9, 15), "09:15 - 09:30"),
    (time(9, 30), "09:30 - 09:45"),
    (time(9, 45), "09:45 - 10:00"),
    (time(10, 0), "10:00 - 10:15"),
    (time(10, 15), "10:15 - 10:30"),
    (time(10, 30), "10:30 - 10:45"),
    (time(10, 45), "10:45 - 11:00"),
    (time(11, 0), "11:00 - 11:15"),
    (time(11, 15), "11:15 - 11:30"),
    (time(11, 30), "11:30 - 11:45"),
    (time(11, 45), "11:45 - 12:00"),
    # Afternoon slots
    (time(14, 0), "14:00 - 14:15"),
    (time(14, 15), "14:15 - 14:30"),
    (time(14, 30), "14:30 - 14:45"),
    (time(14, 45), "14:45 - 15:00"),
    (time(15, 0), "15:00 - 15:15"),
    (time(15, 15), "15:15 - 15:30"),
    (time(15, 30), "15:30 - 15:45"),
    (time(15, 45), "15:45 - 16:00"),
    # Evening slots
    (time(17, 0), "17:00 - 17:15"),
    (time(17, 15), "17:15 - 17:30"),
    (time(17, 30), "17:30 - 17:45"),
    (time(17, 45), "17:45 - 18:00"),
    (time(18, 0), "18:00 - 18:15"),
    (time(18, 15), "18:15 - 18:30"),
    (time(18, 30), "18:30 - 18:45"),
    (time(18, 45), "18:45 - 19:00"),
]

WEEKDAY_CHOICES = [
    (0, "Monday"),
    (1, "Tuesday"),
    (2, "Wednesday"),
    (3, "Thursday"),
    (4, "Friday"),
    (5, "Saturday"),
    (6, "Sunday"),
]


class AdminAddTimeSlot(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
                "placeholder": "Select date",
            }
        )
    )
    start_time = forms.MultipleChoiceField(
        choices=TIME_CHOICES, widget=forms.CheckboxSelectMultiple(), label="Time Slots"
    )


class BulkTimeSlotForm(forms.Form):
    """Enhanced form for bulk time slot creation"""

    start_date = forms.DateField(
        label="Start Date",
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
                "placeholder": "Select start date",
            }
        ),
    )
    end_date = forms.DateField(
        label="End Date",
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
                "placeholder": "Select end date",
            }
        ),
    )
    weekdays = forms.MultipleChoiceField(
        choices=WEEKDAY_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        label="Days of Week",
        help_text="Select which days of the week to create slots for",
    )
    start_time = forms.MultipleChoiceField(
        choices=TIME_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        label="Time Slots",
        help_text="Select which time slots to create",
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date must be after start date.")

        return cleaned_data


class DeleteTimeSlotForm(forms.Form):
    """Form for deleting time slots"""

    time_slot_id = forms.IntegerField(widget=forms.HiddenInput())


class DeleteDayForm(forms.Form):
    """Form for deleting all time slots for a specific day"""

    date = forms.DateField(
        label="Date to Clear",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
