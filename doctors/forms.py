from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Doctor, Specialty
from .services import DoctorService

User = get_user_model()


class DoctorCreationForm(forms.ModelForm):
    """Custom form for creating doctors with user account creation."""

    # User fields
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    username = forms.CharField(max_length=150, required=True)
    phone_number = forms.CharField(max_length=20, required=True)
    wallet_balance = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        initial=0.00,
        help_text="Initial wallet balance (default: 0.00)",
    )

    class Meta:
        model = Doctor
        fields = [
            "first_name",
            "last_name",
            "email",
            "username",
            "phone_number",
            "wallet_balance",
            "specialty",
            "license_number",
            "experience_years",
            "bio",
            "consultation_fee",
            "is_active",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add help text for better UX
        self.fields["license_number"].help_text = (
            "Enter the doctor's medical license number"
        )
        self.fields["experience_years"].help_text = "Years of professional experience"
        self.fields["consultation_fee"].help_text = (
            "Fee per consultation in your currency"
        )
        self.fields["bio"].help_text = "Brief professional biography"
        self.fields["phone_number"].help_text = "Contact phone number"

        # If editing existing doctor, populate user fields
        if self.instance and self.instance.pk:
            user = self.instance.user
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email
            self.fields["username"].initial = user.username
            self.fields["phone_number"].initial = getattr(user, "phone_number", "")
            self.fields["wallet_balance"].initial = getattr(
                user, "wallet_balance", 0.00
            )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            # Check if email already exists (excluding current user if editing)
            existing_user = User.objects.filter(email=email)
            if self.instance and self.instance.pk:
                existing_user = existing_user.exclude(pk=self.instance.user.pk)

            if existing_user.exists():
                raise ValidationError("A user with this email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username:
            # Check if username already exists (excluding current user if editing)
            existing_user = User.objects.filter(username=username)
            if self.instance and self.instance.pk:
                existing_user = existing_user.exclude(pk=self.instance.user.pk)

            if existing_user.exists():
                raise ValidationError("A user with this username already exists.")
        return username

    def clean_license_number(self):
        license_number = self.cleaned_data.get("license_number")
        if license_number:
            # Check if license number already exists (excluding current doctor if editing)
            existing_doctor = Doctor.objects.filter(license_number=license_number)
            if self.instance and self.instance.pk:
                existing_doctor = existing_doctor.exclude(pk=self.instance.pk)

            if existing_doctor.exists():
                raise ValidationError(
                    "A doctor with this license number already exists."
                )
        return license_number

    def clean_experience_years(self):
        experience_years = self.cleaned_data.get("experience_years")
        if experience_years is not None and experience_years < 0:
            raise ValidationError("Experience years cannot be negative.")
        return experience_years

    def clean_consultation_fee(self):
        consultation_fee = self.cleaned_data.get("consultation_fee")
        if consultation_fee is not None and consultation_fee < 0:
            raise ValidationError("Consultation fee cannot be negative.")
        return consultation_fee

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number:
            # Basic phone number validation - you can enhance this based on your requirements
            import re

            # Remove all non-digit characters for validation
            digits_only = re.sub(r"\D", "", phone_number)
            if len(digits_only) < 10:
                raise ValidationError("Phone number must contain at least 10 digits.")
        return phone_number

    def clean_wallet_balance(self):
        wallet_balance = self.cleaned_data.get("wallet_balance")
        if wallet_balance is None:
            wallet_balance = 0.00
        if wallet_balance < 0:
            raise ValidationError("Wallet balance cannot be negative.")
        return wallet_balance

    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()

        # Additional validation can be added here if needed
        # Admin permission validation is handled in the admin class

        return cleaned_data

    def validate_admin_permission(self, user):
        """Validate that the user has admin permissions to create doctors."""
        DoctorService.validate_admin_permissions(user)
        return True

    def save(self, commit=True, created_by=None):
        """
        Save the form. For new doctors, use the model's create_doctor method.
        For updates, use the standard save process.
        """
        if not self.instance.pk and created_by:  # Creating new doctor
            # Use the service layer for proper validation
            user_data = {
                "first_name": self.cleaned_data["first_name"],
                "last_name": self.cleaned_data["last_name"],
                "email": self.cleaned_data["email"],
                "username": self.cleaned_data["username"],
                "phone_number": self.cleaned_data["phone_number"],
                "wallet_balance": self.cleaned_data["wallet_balance"],
            }

            doctor_data = {
                "specialty": self.cleaned_data["specialty"],
                "license_number": self.cleaned_data["license_number"],
                "experience_years": self.cleaned_data["experience_years"],
                "bio": self.cleaned_data["bio"],
                "consultation_fee": self.cleaned_data["consultation_fee"],
                "is_active": self.cleaned_data["is_active"],
            }

            return DoctorService.create_doctor(user_data, doctor_data, created_by)

        else:  # Updating existing doctor
            doctor = super().save(commit=False)

            user_data = {
                "first_name": self.cleaned_data["first_name"],
                "last_name": self.cleaned_data["last_name"],
                "email": self.cleaned_data["email"],
                "username": self.cleaned_data["username"],
                "phone_number": self.cleaned_data["phone_number"],
                "wallet_balance": self.cleaned_data["wallet_balance"],
            }

            doctor_data = {
                "specialty": self.cleaned_data["specialty"],
                "license_number": self.cleaned_data["license_number"],
                "experience_years": self.cleaned_data["experience_years"],
                "bio": self.cleaned_data["bio"],
                "consultation_fee": self.cleaned_data["consultation_fee"],
                "is_active": self.cleaned_data["is_active"],
            }
            return DoctorService.update_doctor(doctor, user_data, doctor_data)


class SpecialtyForm(forms.ModelForm):
    """Form for creating and updating specialties."""

    class Meta:
        model = Specialty
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter specialty name (e.g., Cardiology, Neurology)",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Enter detailed description of the specialty",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].help_text = "Name of the medical specialty"
        self.fields["description"].help_text = (
            "Detailed description of what this specialty covers"
        )

    def clean_name(self):
        """Validate specialty name."""
        name = self.cleaned_data.get("name")
        if name:
            name = name.strip()
            # Check for case-insensitive duplicates
            existing = Specialty.objects.filter(name__iexact=name)
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError("A specialty with this name already exists.")
        return name

    def clean_description(self):
        """Validate specialty description."""
        description = self.cleaned_data.get("description")
        if description:
            description = description.strip()
        return description
