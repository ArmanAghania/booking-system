# appointments/forms.py
from datetime import time
from django import forms
from .models import Appointment, TimeSlot

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["notes"]
        widgets = {
            "notes": forms.Textarea(attrs={
                "class": "w-full border rounded px-3 py-2",
                "rows": 4,
                "placeholder": "Enter any notes for the doctor..."
            }),
        }


TIME_CHOICES = [
    (time(17, 0), "17:00 - 17:15"),
    (time(17, 15), "17:15 - 17:30"),
    (time(17, 30), "17:30 - 17:45"),
    (time(17, 45), "17:45 - 18:00"),
    (time(18, 0), "18:00 - 18:15"),
    (time(18, 15), "18:15 - 18:30"),
    (time(18, 30), "18:30 - 18:45"),
    (time(18, 45), "18:45 - 19:00"),

]

class AdminAddTimeSlot(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control",
            "placeholder": "Select date"
        })
    )
    start_time = forms.MultipleChoiceField(
        choices=TIME_CHOICES,
        widget=forms.CheckboxSelectMultiple(),
        label="Time Slots"
    )