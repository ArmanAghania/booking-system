from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re

User = get_user_model()


class CustomLoginForm(AuthenticationForm):

    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            }
        ),
        label="Remember me",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "class": "appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm",
                "placeholder": "Email or Username",
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": "appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm",
                "placeholder": "Password",
            }
        )

        self.fields["username"].label = "Email or Username"

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username:
            if "@" in username:
                try:
                    user = User.objects.get(email=username)
                    return user.username
                except User.DoesNotExist:
                    pass
        return username


class UserRegistrationForm(forms.Form):

    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm",
                "placeholder": "First Name",
            }
        ),
        label="First Name",
    )

    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm",
                "placeholder": "Last Name",
            }
        ),
        label="Last Name",
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm",
                "placeholder": "Email Address",
            }
        ),
        label="Email Address",
    )

    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm",
                "placeholder": "Phone Number",
            }
        ),
        label="Phone Number",
        help_text="Enter your contact phone number",
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm",
                "placeholder": "Password",
            }
        ),
        label="Password",
        help_text="Password must be at least 8 characters long and contain letters and numbers",
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm",
                "placeholder": "Confirm Password",
            }
        ),
        label="Confirm Password",
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            if User.objects.filter(email=email).exists():
                raise ValidationError("A user with this email already exists.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number:
            digits_only = re.sub(r"\D", "", phone_number)
            if len(digits_only) < 10:
                raise ValidationError("Phone number must contain at least 10 digits.")
        return phone_number

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if password:
            if len(password) < 8:
                raise ValidationError("Password must be at least 8 characters long.")

            if not re.search(r"[a-zA-Z]", password):
                raise ValidationError("Password must contain at least one letter.")

            if not re.search(r"\d", password):
                raise ValidationError("Password must contain at least one number.")

            common_passwords = [
                "password",
                "password123",
                "123456",
                "12345678",
                "qwerty",
                "abc123",
            ]
            if password.lower() in common_passwords:
                raise ValidationError(
                    "This password is too common. Please choose a stronger password."
                )

        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data["email"],
            email=self.cleaned_data["email"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            phone_number=self.cleaned_data["phone_number"],
            user_type="patient",
            password=self.cleaned_data["password1"],
        )
        return user


class OTPVerificationForm(forms.Form):

    otp_code = forms.CharField(
        max_length=10,
        min_length=6,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter 6-digit code",
                "maxlength": "6",
                "pattern": "[0-9]{6}",
                "autocomplete": "one-time-code",
            }
        ),
        help_text="Enter the 6-digit code sent to your email",
    )

    def clean_otp_code(self):
        code = self.cleaned_data.get("otp_code")
        if not code or not code.isdigit():
            raise forms.ValidationError("OTP code must contain only numbers")
        if len(code) != 6:
            raise forms.ValidationError("OTP code must be exactly 6 digits")
        return code


class PasswordResetRequestForm(forms.Form):

    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your email address",
                "autocomplete": "email",
            }
        ),
        help_text="Enter the email address associated with your account",
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            try:
                user = User.objects.get(email=email)
                if not user.is_verified:
                    raise forms.ValidationError(
                        "This email address is not verified. Please verify your email first."
                    )
            except User.DoesNotExist:
                raise forms.ValidationError("No account found with this email address.")
        return email


class PasswordResetForm(forms.Form):

    otp_code = forms.CharField(
        max_length=10,
        min_length=6,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter 6-digit code",
                "maxlength": "6",
                "pattern": "[0-9]{6}",
                "autocomplete": "one-time-code",
            }
        ),
        help_text="Enter the 6-digit code sent to your email",
    )

    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter new password",
                "autocomplete": "new-password",
            }
        ),
        help_text="Enter your new password",
    )

    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm new password",
                "autocomplete": "new-password",
            }
        ),
        help_text="Confirm your new password",
    )

    def clean_otp_code(self):
        code = self.cleaned_data.get("otp_code")
        if not code or not code.isdigit():
            raise forms.ValidationError("OTP code must contain only numbers")
        if len(code) != 6:
            raise forms.ValidationError("OTP code must be exactly 6 digits")
        return code

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Passwords do not match.")

            if len(password1) < 8:
                raise forms.ValidationError(
                    "Password must be at least 8 characters long."
                )

        return cleaned_data
