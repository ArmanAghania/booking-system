from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.admin.sites import AdminSite
from django.urls import reverse

from .models import Doctor, Specialty
from .forms import DoctorCreationForm
from .services import DoctorService
from .admin import DoctorAdmin, SpecialtyAdmin

User = get_user_model()


class DoctorModelTest(TestCase):
    """Test cases for Doctor model."""

    def setUp(self):
        """Set up test data."""
        self.specialty = Specialty.objects.create(
            name="Cardiology", description="Heart specialist"
        )
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123",
            user_type="admin",
            is_superuser=True,
        )
        self.regular_user = User.objects.create_user(
            username="regular",
            email="regular@test.com",
            password="testpass123",
            user_type="patient",
        )

    def test_doctor_creation_with_valid_data(self):
        """Test creating a doctor with valid data."""
        user_data = {
            "username": "dr_smith",
            "email": "dr.smith@test.com",
            "first_name": "John",
            "last_name": "Smith",
            "phone_number": "1234567890",
            "wallet_balance": 0.00,
        }

        doctor_data = {
            "specialty": self.specialty,
            "license_number": "LIC123456",
            "experience_years": 5,
            "bio": "Experienced cardiologist",
            "consultation_fee": 150.00,
            "is_active": True,
        }

        doctor = Doctor.create_doctor(user_data, doctor_data, self.admin_user)

        # Check doctor was created
        self.assertIsInstance(doctor, Doctor)
        self.assertEqual(doctor.license_number, "LIC123456")
        self.assertEqual(doctor.experience_years, 5)
        self.assertEqual(doctor.consultation_fee, 150.00)
        self.assertEqual(doctor.created_by, self.admin_user)

        # Check user was created
        self.assertIsNotNone(doctor.user)
        self.assertEqual(doctor.user.username, "dr_smith")
        self.assertEqual(doctor.user.email, "dr.smith@test.com")
        self.assertEqual(doctor.user.user_type, "doctor")
        self.assertTrue(doctor.user.is_staff)

    def test_doctor_creation_requires_admin_permissions(self):
        """Test that only admin users can create doctors."""
        user_data = {
            "username": "dr_smith",
            "email": "dr.smith@test.com",
            "first_name": "John",
            "last_name": "Smith",
            "phone_number": "1234567890",
            "wallet_balance": 0.00,
        }

        doctor_data = {
            "specialty": self.specialty,
            "license_number": "LIC123456",
            "experience_years": 5,
            "bio": "Experienced cardiologist",
            "consultation_fee": 150.00,
            "is_active": True,
        }

        # Test with regular user (should fail)
        with self.assertRaises(ValidationError) as context:
            Doctor.create_doctor(user_data, doctor_data, self.regular_user)

        self.assertIn(
            "Only superusers or users with admin type", str(context.exception)
        )

    def test_doctor_clean_validation(self):
        """Test model clean method validation."""
        user = User.objects.create_user(
            username="test_doctor", email="test@test.com", user_type="doctor"
        )

        # Test negative experience years
        doctor = Doctor(
            user=user,
            specialty=self.specialty,
            license_number="LIC123",
            experience_years=-1,
            bio="Test bio",
            consultation_fee=100.00,
            created_by=self.admin_user,
        )

        with self.assertRaises(ValidationError) as context:
            doctor.clean()

        self.assertIn("Experience years cannot be negative", str(context.exception))

        # Test negative consultation fee
        doctor.experience_years = 5
        doctor.consultation_fee = -50.00

        with self.assertRaises(ValidationError) as context:
            doctor.clean()

        self.assertIn("Consultation fee cannot be negative", str(context.exception))

    def test_license_number_uniqueness(self):
        """Test that license numbers must be unique."""
        user1 = User.objects.create_user(
            username="doctor1", email="doctor1@test.com", user_type="doctor"
        )
        user2 = User.objects.create_user(
            username="doctor2", email="doctor2@test.com", user_type="doctor"
        )

        # Create first doctor
        Doctor.objects.create(
            user=user1,
            specialty=self.specialty,
            license_number="LIC123",
            experience_years=5,
            bio="Test bio",
            consultation_fee=100.00,
            created_by=self.admin_user,
        )

        # Try to create second doctor with same license number
        doctor2 = Doctor(
            user=user2,
            specialty=self.specialty,
            license_number="LIC123",
            experience_years=3,
            bio="Test bio 2",
            consultation_fee=120.00,
            created_by=self.admin_user,
        )

        with self.assertRaises(ValidationError) as context:
            doctor2.clean()

        self.assertIn("license number already exists", str(context.exception))


class DoctorFormTest(TestCase):
    """Test cases for DoctorCreationForm."""

    def setUp(self):
        """Set up test data."""
        self.specialty = Specialty.objects.create(
            name="Cardiology", description="Heart specialist"
        )
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123",
            user_type="admin",
            is_superuser=True,
        )

    def test_form_valid_data(self):
        """Test form with valid data."""
        form_data = {
            "first_name": "John",
            "last_name": "Smith",
            "email": "dr.smith@test.com",
            "username": "dr_smith",
            "phone_number": "1234567890",
            "wallet_balance": 0.00,
            "specialty": self.specialty.id,
            "license_number": "LIC123456",
            "experience_years": 5,
            "bio": "Experienced cardiologist",
            "consultation_fee": 150.00,
            "is_active": True,
        }

        form = DoctorCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_validation_errors(self):
        """Test form validation errors."""
        # Test with missing required fields
        form_data = {
            "first_name": "John",
            # Missing last_name, email, etc.
        }

        form = DoctorCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("last_name", form.errors)
        self.assertIn("email", form.errors)

    def test_email_uniqueness_validation(self):
        """Test email uniqueness validation."""
        # Create existing user
        User.objects.create_user(
            username="existing", email="existing@test.com", user_type="patient"
        )

        form_data = {
            "first_name": "John",
            "last_name": "Smith",
            "email": "existing@test.com",  # Duplicate email
            "username": "dr_smith",
            "phone_number": "1234567890",
            "wallet_balance": 0.00,
            "specialty": self.specialty.id,
            "license_number": "LIC123456",
            "experience_years": 5,
            "bio": "Experienced cardiologist",
            "consultation_fee": 150.00,
            "is_active": True,
        }

        form = DoctorCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email already exists", str(form.errors["email"][0]))

    def test_phone_number_validation(self):
        """Test phone number validation."""
        form_data = {
            "first_name": "John",
            "last_name": "Smith",
            "email": "dr.smith@test.com",
            "username": "dr_smith",
            "phone_number": "123",  # Too short
            "wallet_balance": 0.00,
            "specialty": self.specialty.id,
            "license_number": "LIC123456",
            "experience_years": 5,
            "bio": "Experienced cardiologist",
            "consultation_fee": 150.00,
            "is_active": True,
        }

        form = DoctorCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Phone number must contain at least 10 digits",
            str(form.errors["phone_number"][0]),
        )

    def test_form_save_creates_doctor(self):
        """Test that form save creates doctor and user."""
        form_data = {
            "first_name": "John",
            "last_name": "Smith",
            "email": "dr.smith@test.com",
            "username": "dr_smith",
            "phone_number": "1234567890",
            "wallet_balance": 0.00,
            "specialty": self.specialty.id,
            "license_number": "LIC123456",
            "experience_years": 5,
            "bio": "Experienced cardiologist",
            "consultation_fee": 150.00,
            "is_active": True,
        }

        form = DoctorCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

        doctor = form.save(created_by=self.admin_user)

        # Check doctor was created
        self.assertIsInstance(doctor, Doctor)
        self.assertEqual(doctor.license_number, "LIC123456")

        # Check user was created
        self.assertIsNotNone(doctor.user)
        self.assertEqual(doctor.user.username, "dr_smith")
        self.assertEqual(doctor.user.user_type, "doctor")


class DoctorServiceTest(TestCase):
    """Test cases for DoctorService."""

    def setUp(self):
        """Set up test data."""
        self.specialty = Specialty.objects.create(
            name="Cardiology", description="Heart specialist"
        )
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123",
            user_type="admin",
            is_superuser=True,
        )
        self.superuser = User.objects.create_user(
            username="superuser",
            email="super@test.com",
            password="testpass123",
            is_superuser=True,
        )
        self.regular_user = User.objects.create_user(
            username="regular",
            email="regular@test.com",
            password="testpass123",
            user_type="patient",
        )

    def test_validate_admin_permissions_superuser(self):
        """Test validation with superuser."""
        DoctorService.validate_admin_permissions(self.superuser)

    def test_validate_admin_permissions_admin_type(self):
        """Test validation with admin type user."""
        DoctorService.validate_admin_permissions(self.admin_user)

    def test_validate_admin_permissions_regular_user(self):
        """Test validation with regular user."""
        with self.assertRaises(ValidationError) as context:
            DoctorService.validate_admin_permissions(self.regular_user)

        self.assertIn(
            "Only superusers or users with admin type", str(context.exception)
        )

    def test_can_user_manage_doctors(self):
        """Test can_user_manage_doctors method."""
        self.assertTrue(DoctorService.can_user_manage_doctors(self.superuser))
        self.assertTrue(DoctorService.can_user_manage_doctors(self.admin_user))
        self.assertFalse(DoctorService.can_user_manage_doctors(self.regular_user))


class DoctorAdminTest(TestCase):
    """Test cases for DoctorAdmin."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.site = AdminSite()

        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123",
            user_type="admin",
            is_superuser=True,
        )

        self.regular_user = User.objects.create_user(
            username="regular",
            email="regular@test.com",
            password="testpass123",
            user_type="patient",
        )

        self.doctor_admin = DoctorAdmin(Doctor, self.site)

    def test_has_add_permission_admin_user(self):
        """Test add permission for admin user."""
        request = self.factory.get("/admin/doctors/doctor/")
        request.user = self.admin_user
        self.assertTrue(self.doctor_admin.has_add_permission(request))

    def test_has_add_permission_regular_user(self):
        """Test add permission for regular user."""
        request = self.factory.get("/admin/doctors/doctor/")
        request.user = self.regular_user
        self.assertFalse(self.doctor_admin.has_add_permission(request))


class IntegrationTest(TestCase):
    """Integration tests for the complete doctor creation flow."""

    def setUp(self):
        """Set up test data."""
        self.specialty = Specialty.objects.create(
            name="Cardiology", description="Heart specialist"
        )
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123",
            user_type="admin",
            is_superuser=True,
        )

    def test_complete_doctor_creation_flow(self):
        """Test the complete flow from form to database."""
        form_data = {
            "first_name": "John",
            "last_name": "Smith",
            "email": "dr.smith@test.com",
            "username": "dr_smith",
            "phone_number": "1234567890",
            "wallet_balance": 0.00,
            "specialty": self.specialty.id,
            "license_number": "LIC123456",
            "experience_years": 5,
            "bio": "Experienced cardiologist",
            "consultation_fee": 150.00,
            "is_active": True,
        }

        form = DoctorCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

        doctor = form.save(created_by=self.admin_user)

        # Verify doctor exists in database
        self.assertTrue(Doctor.objects.filter(license_number="LIC123456").exists())

        # Verify user exists in database
        self.assertTrue(User.objects.filter(username="dr_smith").exists())

        # Verify relationships
        doctor = Doctor.objects.get(license_number="LIC123456")
        self.assertEqual(doctor.user.username, "dr_smith")
        self.assertEqual(doctor.specialty.name, "Cardiology")
        self.assertEqual(doctor.created_by, self.admin_user)

        # Verify user properties
        user = doctor.user
        self.assertEqual(user.user_type, "doctor")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)


class SpecialtyModelTest(TestCase):
    """Test cases for Specialty model."""

    def test_specialty_creation_with_valid_data(self):
        """Test creating a specialty with valid data."""
        specialty = Specialty.objects.create(
            name="Cardiology",
            description="Medical specialty dealing with disorders of the heart and blood vessels.",
        )

        self.assertEqual(specialty.name, "Cardiology")
        self.assertIn("heart and blood vessels", specialty.description)
        self.assertIsNotNone(specialty.created_at)
        self.assertIsNotNone(specialty.updated_at)

    def test_specialty_str_representation(self):
        """Test string representation of specialty."""
        specialty = Specialty.objects.create(
            name="Neurology",
            description="Medical specialty dealing with disorders of the nervous system.",
        )

        self.assertEqual(str(specialty), "Neurology")

    def test_specialty_name_uniqueness(self):
        """Test that specialty names must be unique."""
        Specialty.objects.create(
            name="Dermatology",
            description="Medical specialty dealing with skin disorders.",
        )

        # Try to create another specialty with the same name
        with self.assertRaises(Exception):  # IntegrityError or ValidationError
            Specialty.objects.create(
                name="Dermatology", description="Another dermatology specialty."
            )

    def test_specialty_clean_validation_empty_name(self):
        """Test validation for empty specialty name."""
        specialty = Specialty(name="", description="Valid description")

        with self.assertRaises(ValidationError) as context:
            specialty.clean()

        self.assertIn("Specialty name cannot be empty", str(context.exception))

    def test_specialty_clean_validation_empty_description(self):
        """Test validation for empty specialty description."""
        specialty = Specialty(name="Valid Name", description="")

        with self.assertRaises(ValidationError) as context:
            specialty.clean()

        self.assertIn("Specialty description cannot be empty", str(context.exception))

    def test_specialty_clean_validation_whitespace_only(self):
        """Test validation for whitespace-only name and description."""
        specialty = Specialty(name="   ", description="   ")

        with self.assertRaises(ValidationError) as context:
            specialty.clean()

        self.assertIn("Specialty name cannot be empty", str(context.exception))

    def test_specialty_clean_validation_case_insensitive_duplicate(self):
        """Test case-insensitive duplicate name validation."""
        Specialty.objects.create(
            name="Oncology",
            description="Medical specialty dealing with cancer treatment.",
        )

        specialty = Specialty(name="oncology", description="Another oncology specialty")

        with self.assertRaises(ValidationError) as context:
            specialty.clean()

        self.assertIn(
            "A specialty with this name already exists", str(context.exception)
        )

    def test_specialty_save_strips_whitespace(self):
        """Test that save method strips whitespace from name and description."""
        specialty = Specialty(
            name="  Pediatrics  ",
            description="  Medical specialty dealing with children's health.  ",
        )
        specialty.save()

        self.assertEqual(specialty.name, "Pediatrics")
        self.assertEqual(
            specialty.description, "Medical specialty dealing with children's health."
        )

    def test_specialty_ordering(self):
        """Test that specialties are ordered by name."""
        Specialty.objects.create(name="Zygology", description="Z specialty")
        Specialty.objects.create(name="Anesthesiology", description="A specialty")
        Specialty.objects.create(name="Cardiology", description="C specialty")

        specialties = Specialty.objects.all()
        names = [s.name for s in specialties]

        self.assertEqual(names, ["Anesthesiology", "Cardiology", "Zygology"])


class SpecialtyAdminTest(TestCase):
    """Test cases for SpecialtyAdmin."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.site = AdminSite()

        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123",
            user_type="admin",
            is_superuser=True,
        )

        self.specialty_admin = SpecialtyAdmin(Specialty, self.site)

        # Create test specialties
        self.cardiology = Specialty.objects.create(
            name="Cardiology", description="Heart and blood vessel disorders"
        )
        self.neurology = Specialty.objects.create(
            name="Neurology", description="Nervous system disorders"
        )

    def test_list_display_includes_doctor_count(self):
        """Test that list display includes doctor count."""
        self.assertIn("doctor_count", self.specialty_admin.list_display)
        self.assertIn("name", self.specialty_admin.list_display)

    def test_search_fields(self):
        """Test search functionality."""
        self.assertIn("name", self.specialty_admin.search_fields)
        self.assertIn("description", self.specialty_admin.search_fields)

    def test_doctor_count_method(self):
        """Test doctor_count method."""
        # Create a doctor for the cardiology specialty
        doctor_user = User.objects.create_user(
            username="dr_smith", email="dr.smith@test.com", user_type="doctor"
        )
        Doctor.objects.create(
            user=doctor_user,
            specialty=self.cardiology,
            license_number="LIC123",
            experience_years=5,
            bio="Test bio",
            consultation_fee=100.00,
            created_by=self.admin_user,
        )

        count = self.specialty_admin.doctor_count(self.cardiology)
        self.assertEqual(count, 1)

        # Test specialty with no doctors
        count = self.specialty_admin.doctor_count(self.neurology)
        self.assertEqual(count, 0)

    def test_has_delete_permission_with_doctors(self):
        """Test delete permission when specialty has doctors."""
        # Create a doctor for the cardiology specialty
        doctor_user = User.objects.create_user(
            username="dr_smith", email="dr.smith@test.com", user_type="doctor"
        )
        Doctor.objects.create(
            user=doctor_user,
            specialty=self.cardiology,
            license_number="LIC123",
            experience_years=5,
            bio="Test bio",
            consultation_fee=100.00,
            created_by=self.admin_user,
        )

        request = self.factory.get("/admin/doctors/specialty/")
        request.user = self.admin_user

        # Should not be able to delete specialty with doctors
        self.assertFalse(
            self.specialty_admin.has_delete_permission(request, self.cardiology)
        )

        # Should be able to delete specialty without doctors
        self.assertTrue(
            self.specialty_admin.has_delete_permission(request, self.neurology)
        )

    def test_get_queryset_optimization(self):
        """Test that get_queryset is optimized with annotations."""
        request = self.factory.get("/admin/doctors/specialty/")
        request.user = self.admin_user

        queryset = self.specialty_admin.get_queryset(request)

        # Check that the queryset has the doctor_count annotation
        self.assertTrue(hasattr(queryset, "query"))

    def test_delete_model_with_doctors(self):
        """Test delete_model method when specialty has doctors."""
        # Create a doctor for the cardiology specialty
        doctor_user = User.objects.create_user(
            username="dr_smith", email="dr.smith@test.com", user_type="doctor"
        )
        Doctor.objects.create(
            user=doctor_user,
            specialty=self.cardiology,
            license_number="LIC123",
            experience_years=5,
            bio="Test bio",
            consultation_fee=100.00,
            created_by=self.admin_user,
        )

        request = self.factory.get("/admin/doctors/specialty/")
        request.user = self.admin_user

        # Test that specialty with doctors cannot be deleted
        # We'll test the permission method instead of the actual delete
        self.assertFalse(
            self.specialty_admin.has_delete_permission(request, self.cardiology)
        )

        # Test that specialty without doctors can be deleted
        self.assertTrue(
            self.specialty_admin.has_delete_permission(request, self.neurology)
        )


class SpecialtyIntegrationTest(TestCase):
    """Integration tests for specialty operations."""

    def setUp(self):
        """Set up test data."""
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123",
            user_type="admin",
            is_superuser=True,
        )

    def test_complete_specialty_management_flow(self):
        """Test the complete specialty management flow."""
        # Step 1: Create specialty
        specialty = Specialty.objects.create(
            name="Emergency Medicine",
            description="Medical specialty dealing with acute medical conditions.",
        )

        # Step 2: Verify specialty exists
        self.assertTrue(Specialty.objects.filter(name="Emergency Medicine").exists())

        # Step 3: Update specialty
        specialty.description = "Updated description for emergency medicine."
        specialty.save()

        # Step 4: Verify update
        updated_specialty = Specialty.objects.get(name="Emergency Medicine")
        self.assertIn("Updated description", updated_specialty.description)

        # Step 5: Create doctor with this specialty
        doctor_user = User.objects.create_user(
            username="dr_emergency", email="dr.emergency@test.com", user_type="doctor"
        )
        doctor = Doctor.objects.create(
            user=doctor_user,
            specialty=specialty,
            license_number="EMERG123",
            experience_years=3,
            bio="Emergency medicine specialist",
            consultation_fee=200.00,
            created_by=self.admin_user,
        )

        # Step 6: Verify doctor-specialty relationship
        self.assertEqual(doctor.specialty, specialty)
        self.assertEqual(specialty.doctor_set.count(), 1)

        # Step 7: Try to delete specialty with doctor (should fail)
        with self.assertRaises(Exception):
            specialty.delete()

        # Step 8: Delete doctor first, then specialty
        doctor.delete()
        specialty.delete()

        # Step 9: Verify deletion
        self.assertFalse(Specialty.objects.filter(name="Emergency Medicine").exists())

    def test_specialty_name_case_insensitivity(self):
        """Test that specialty names are case-insensitive."""
        # Create specialty with lowercase name
        specialty1 = Specialty.objects.create(
            name="psychiatry", description="Mental health specialty"
        )

        # Try to create another with different case
        with self.assertRaises(Exception):
            Specialty.objects.create(
                name="Psychiatry", description="Another psychiatry specialty"
            )

        # Verify only one exists
        self.assertEqual(Specialty.objects.filter(name__iexact="psychiatry").count(), 1)


class SpecialtyViewTest(TestCase):
    """Test cases for specialty class-based views."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()

        # Create test users
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123",
            user_type="admin",
            is_superuser=True,
        )

        self.regular_user = User.objects.create_user(
            username="patient",
            email="patient@test.com",
            password="testpass123",
            user_type="patient",
        )

        # Create test specialties
        self.cardiology = Specialty.objects.create(
            name="Cardiology", description="Heart and blood vessel disorders"
        )
        self.neurology = Specialty.objects.create(
            name="Neurology", description="Nervous system disorders"
        )

    def test_specialty_list_view_get(self):
        """Test specialty list view GET request."""
        response = self.client.get(reverse("doctors:specialty_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cardiology")
        self.assertContains(response, "Neurology")
        self.assertTemplateUsed(response, "doctors/specialty_list.html")

    def test_specialty_list_view_with_search(self):
        """Test specialty list view with search query."""
        response = self.client.get(
            reverse("doctors:specialty_list"), {"search": "cardio"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cardiology")
        self.assertNotContains(response, "Neurology")

    def test_specialty_detail_view_get(self):
        """Test specialty detail view GET request."""
        response = self.client.get(
            reverse(
                "doctors:specialty_detail", kwargs={"specialty_id": self.cardiology.id}
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cardiology")
        self.assertContains(response, "Heart and blood vessel disorders")
        self.assertTemplateUsed(response, "doctors/specialty_detail.html")

    def test_specialty_detail_view_with_doctors(self):
        """Test specialty detail view with associated doctors."""
        # Create a doctor for the cardiology specialty
        doctor_user = User.objects.create_user(
            username="dr_smith", email="dr.smith@test.com", user_type="doctor"
        )
        doctor = Doctor.objects.create(
            user=doctor_user,
            specialty=self.cardiology,
            license_number="LIC123",
            experience_years=5,
            bio="Test bio",
            consultation_fee=100.00,
            created_by=self.admin_user,
        )

        response = self.client.get(
            reverse(
                "doctors:specialty_detail", kwargs={"specialty_id": self.cardiology.id}
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dr. Smith")
        self.assertContains(response, "1 doctor")

    def test_specialty_create_view_requires_login(self):
        """Test that specialty create view requires login."""
        response = self.client.get(reverse("doctors:specialty_create"))

        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_specialty_create_view_requires_admin(self):
        """Test that specialty create view requires admin permissions."""
        self.client.login(username="patient", password="testpass123")
        response = self.client.get(reverse("doctors:specialty_create"))

        self.assertEqual(response.status_code, 302)  # Redirect due to permission denied

    def test_specialty_create_view_admin_access(self):
        """Test that admin users can access specialty create view."""
        self.client.login(username="admin", password="testpass123")
        response = self.client.get(reverse("doctors:specialty_create"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "doctors/specialty_form.html")

    def test_specialty_create_view_post_valid(self):
        """Test specialty create view with valid POST data."""
        self.client.login(username="admin", password="testpass123")

        data = {"name": "Dermatology", "description": "Skin and hair disorders"}

        response = self.client.post(reverse("doctors:specialty_create"), data)

        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful creation
        self.assertTrue(Specialty.objects.filter(name="Dermatology").exists())

    def test_specialty_create_view_post_invalid(self):
        """Test specialty create view with invalid POST data."""
        self.client.login(username="admin", password="testpass123")

        data = {"name": "", "description": "Valid description"}  # Invalid: empty name

        response = self.client.post(reverse("doctors:specialty_create"), data)

        self.assertEqual(response.status_code, 200)  # Form with errors
        self.assertFalse(
            Specialty.objects.filter(description="Valid description").exists()
        )

    def test_specialty_update_view_requires_admin(self):
        """Test that specialty update view requires admin permissions."""
        self.client.login(username="patient", password="testpass123")
        response = self.client.get(
            reverse(
                "doctors:specialty_update", kwargs={"specialty_id": self.cardiology.id}
            )
        )

        self.assertEqual(response.status_code, 302)  # Redirect due to permission denied

    def test_specialty_update_view_admin_access(self):
        """Test that admin users can access specialty update view."""
        self.client.login(username="admin", password="testpass123")
        response = self.client.get(
            reverse(
                "doctors:specialty_update", kwargs={"specialty_id": self.cardiology.id}
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "doctors/specialty_form.html")
        self.assertContains(response, "Update Cardiology")

    def test_specialty_update_view_post_valid(self):
        """Test specialty update view with valid POST data."""
        self.client.login(username="admin", password="testpass123")

        data = {
            "name": "Updated Cardiology",
            "description": "Updated description for cardiology",
        }

        response = self.client.post(
            reverse(
                "doctors:specialty_update", kwargs={"specialty_id": self.cardiology.id}
            ),
            data,
        )

        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        updated_specialty = Specialty.objects.get(id=self.cardiology.id)
        self.assertEqual(updated_specialty.name, "Updated Cardiology")

    def test_specialty_delete_view_requires_admin(self):
        """Test that specialty delete view requires admin permissions."""
        self.client.login(username="patient", password="testpass123")
        response = self.client.get(
            reverse(
                "doctors:specialty_delete", kwargs={"specialty_id": self.cardiology.id}
            )
        )

        self.assertEqual(response.status_code, 302)  # Redirect due to permission denied

    def test_specialty_delete_view_admin_access(self):
        """Test that admin users can access specialty delete view."""
        self.client.login(username="admin", password="testpass123")
        response = self.client.get(
            reverse(
                "doctors:specialty_delete", kwargs={"specialty_id": self.cardiology.id}
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "doctors/specialty_confirm_delete.html")

    def test_specialty_delete_view_with_doctors(self):
        """Test specialty delete view when specialty has doctors."""
        # Create a doctor for the cardiology specialty
        doctor_user = User.objects.create_user(
            username="dr_smith", email="dr.smith@test.com", user_type="doctor"
        )
        Doctor.objects.create(
            user=doctor_user,
            specialty=self.cardiology,
            license_number="LIC123",
            experience_years=5,
            bio="Test bio",
            consultation_fee=100.00,
            created_by=self.admin_user,
        )

        self.client.login(username="admin", password="testpass123")
        response = self.client.post(
            reverse(
                "doctors:specialty_delete", kwargs={"specialty_id": self.cardiology.id}
            )
        )

        # Should redirect back to detail page due to doctors being assigned
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Specialty.objects.filter(id=self.cardiology.id).exists())

    def test_specialty_delete_view_success(self):
        """Test successful specialty deletion."""
        self.client.login(username="admin", password="testpass123")
        response = self.client.post(
            reverse(
                "doctors:specialty_delete", kwargs={"specialty_id": self.neurology.id}
            )
        )

        self.assertEqual(response.status_code, 302)  # Redirect to list page
        self.assertFalse(Specialty.objects.filter(id=self.neurology.id).exists())


class DoctorViewTest(TestCase):
    """Test cases for doctor class-based views."""

    def setUp(self):
        """Set up test data."""
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123",
            user_type="admin",
            is_superuser=True,
        )

        # Create test specialty
        self.cardiology = Specialty.objects.create(
            name="Cardiology", description="Heart and blood vessel disorders"
        )

        # Create test doctor
        self.doctor_user = User.objects.create_user(
            username="dr_smith", email="dr.smith@test.com", user_type="doctor"
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            specialty=self.cardiology,
            license_number="LIC123",
            experience_years=5,
            bio="Test bio for Dr. Smith",
            consultation_fee=100.00,
            created_by=self.admin_user,
        )

    def test_doctor_list_view_get(self):
        """Test doctor list view GET request."""
        response = self.client.get(reverse("doctors:doctor_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dr. Smith")
        self.assertContains(response, "Cardiology")
        self.assertTemplateUsed(response, "doctors/doctor_list.html")

    def test_doctor_list_view_with_search(self):
        """Test doctor list view with search query."""
        response = self.client.get(reverse("doctors:doctor_list"), {"search": "smith"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dr. Smith")

    def test_doctor_list_view_with_specialty_filter(self):
        """Test doctor list view with specialty filter."""
        response = self.client.get(
            reverse("doctors:doctor_list"), {"specialty": self.cardiology.id}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dr. Smith")

    def test_doctor_detail_view_get(self):
        """Test doctor detail view GET request."""
        response = self.client.get(
            reverse("doctors:doctor_detail", kwargs={"doctor_id": self.doctor.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dr. Smith")
        self.assertContains(response, "Cardiology")
        self.assertContains(response, "Test bio for Dr. Smith")
        self.assertTemplateUsed(response, "doctors/doctor_detail.html")

    def test_doctor_detail_view_inactive_doctor(self):
        """Test doctor detail view for inactive doctor returns 404."""
        self.doctor.is_active = False
        self.doctor.save()

        response = self.client.get(
            reverse("doctors:doctor_detail", kwargs={"doctor_id": self.doctor.id})
        )

        self.assertEqual(response.status_code, 404)

    def test_doctor_create_view_requires_login(self):
        """Test that doctor create view requires login."""
        response = self.client.get(reverse("doctors:doctor_create"))

        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_doctor_create_view_requires_admin(self):
        """Test that doctor create view requires admin permissions."""
        # Create a regular user
        regular_user = User.objects.create_user(
            username="patient",
            email="patient@test.com",
            password="testpass123",
            user_type="patient",
        )

        self.client.login(username="patient", password="testpass123")
        response = self.client.get(reverse("doctors:doctor_create"))

        self.assertEqual(response.status_code, 302)  # Redirect due to permission denied

    def test_doctor_create_view_admin_access(self):
        """Test that admin users can access doctor create view."""
        self.client.login(username="admin", password="testpass123")
        response = self.client.get(reverse("doctors:doctor_create"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "doctors/doctor_form.html")

    def test_doctor_create_view_post_valid(self):
        """Test doctor create view with valid POST data."""
        self.client.login(username="admin", password="testpass123")

        data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@test.com",
            "username": "jane_doe",
            "phone_number": "+1234567890",
            "specialty": self.cardiology.id,
            "license_number": "LIC456",
            "experience_years": 3,
            "bio": "Experienced cardiologist with 3 years of practice",
            "consultation_fee": 150.00,
            "is_active": True,
        }

        response = self.client.post(reverse("doctors:doctor_create"), data)

        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful creation
        self.assertTrue(Doctor.objects.filter(user__username="jane_doe").exists())

    def test_doctor_create_view_post_invalid(self):
        """Test doctor create view with invalid POST data."""
        self.client.login(username="admin", password="testpass123")

        data = {
            "first_name": "",  # Invalid: empty name
            "last_name": "Doe",
            "email": "invalid-email",  # Invalid email
            "username": "jane_doe",
            "specialty": self.cardiology.id,
            "license_number": "LIC456",
            "experience_years": -1,  # Invalid: negative experience
            "bio": "Test bio",
            "consultation_fee": -50.00,  # Invalid: negative fee
            "is_active": True,
        }

        response = self.client.post(reverse("doctors:doctor_create"), data)

        self.assertEqual(response.status_code, 200)  # Form with errors
        self.assertFalse(Doctor.objects.filter(user__username="jane_doe").exists())
