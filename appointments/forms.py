# appointments/forms.py
from django import forms
from .models import Appointment

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
