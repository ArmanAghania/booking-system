"""
Service layer for doctor-related business logic.
This separates business logic from views, forms, and models.
"""

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import Doctor

User = get_user_model()


class DoctorService:
    """Service class for doctor-related operations."""

    @staticmethod
    def validate_admin_permissions(user):
        """
        Validate that a user has admin permissions to create doctors.
        User must be either a superuser OR have user_type='admin'.

        Args:
            user: The user to validate

        Raises:
            ValidationError: If user doesn't have admin permissions
        """
        if not user.is_authenticated:
            raise ValidationError("User must be authenticated.")

        # Check if user is either a superuser OR has admin user type
        is_superuser = user.is_superuser
        is_admin_type = getattr(user, "user_type", None) == "admin"

        if not (is_superuser or is_admin_type):
            raise ValidationError(
                "Only superusers or users with admin type can create doctor accounts."
            )

    @staticmethod
    def create_doctor(user_data, doctor_data, created_by):
        """
        Create a new doctor with proper validation and business logic.

        Args:
            user_data: Dictionary containing user information
            doctor_data: Dictionary containing doctor-specific information
            created_by: The admin user creating the doctor

        Returns:
            Doctor: The created doctor instance

        Raises:
            ValidationError: If validation fails
        """
        # Validate admin permissions
        DoctorService.validate_admin_permissions(created_by)

        # Use the model's class method for creation
        return Doctor.create_doctor(user_data, doctor_data, created_by)

    @staticmethod
    def update_doctor(doctor, user_data, doctor_data):
        """
        Update an existing doctor's information.

        Args:
            doctor: The doctor instance to update
            user_data: Dictionary containing updated user information
            doctor_data: Dictionary containing updated doctor information

        Returns:
            Doctor: The updated doctor instance
        """
        # Update user account
        user = doctor.user
        user.first_name = user_data["first_name"]
        user.last_name = user_data["last_name"]
        user.email = user_data["email"]
        user.username = user_data["username"]
        user.phone_number = user_data["phone_number"]
        user.wallet_balance = user_data["wallet_balance"]
        user.user_type = "doctor"
        user.save()

        # Update doctor profile
        for field, value in doctor_data.items():
            setattr(doctor, field, value)
        doctor.save()

        return doctor

    @staticmethod
    def can_user_manage_doctors(user):
        """
        Check if a user can manage doctors (create, edit, delete).

        Args:
            user: The user to check

        Returns:
            bool: True if user can manage doctors
        """
        try:
            DoctorService.validate_admin_permissions(user)
            return True
        except ValidationError:
            return False
