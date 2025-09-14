from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from doctors.models import Specialty, Doctor
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = "Create sample data for testing"

    def handle(self, *args, **options):
        # Create specialties
        specialties_data = [
            {
                "name": "Cardiology",
                "description": "Heart and cardiovascular system specialist",
            },
            {"name": "Dermatology", "description": "Skin, hair, and nail specialist"},
            {"name": "Neurology", "description": "Brain and nervous system specialist"},
            {"name": "Pediatrics", "description": "Children's health specialist"},
            {"name": "Orthopedics", "description": "Bone and joint specialist"},
            {"name": "General Medicine", "description": "General health and wellness"},
        ]

        specialties = []
        for spec_data in specialties_data:
            specialty, created = Specialty.objects.get_or_create(
                name=spec_data["name"],
                defaults={"description": spec_data["description"]},
            )
            specialties.append(specialty)
            if created:
                self.stdout.write(f"Created specialty: {specialty.name}")

        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "first_name": "Admin",
                "last_name": "User",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin_user.set_password("admin123")
            admin_user.save()
            self.stdout.write("Created admin user: admin/admin123")

        # Create sample doctors
        doctors_data = [
            {
                "username": "dr_smith",
                "email": "dr.smith@example.com",
                "first_name": "John",
                "last_name": "Smith",
                "specialty": "Cardiology",
                "license": "CARD001",
                "experience": 15,
                "bio": "Dr. Smith is a board-certified cardiologist with over 15 years of experience in treating heart conditions. He specializes in interventional cardiology and preventive care.",
                "fee": 150.00,
                "rating": 4.8,
                "reviews": 127,
            },
            {
                "username": "dr_johnson",
                "email": "dr.johnson@example.com",
                "first_name": "Sarah",
                "last_name": "Johnson",
                "specialty": "Dermatology",
                "license": "DERM001",
                "experience": 12,
                "bio": "Dr. Johnson is a renowned dermatologist specializing in cosmetic dermatology and skin cancer treatment. She has published numerous research papers.",
                "fee": 120.00,
                "rating": 4.9,
                "reviews": 89,
            },
            {
                "username": "dr_williams",
                "email": "dr.williams@example.com",
                "first_name": "Michael",
                "last_name": "Williams",
                "specialty": "Neurology",
                "license": "NEURO001",
                "experience": 20,
                "bio": "Dr. Williams is a leading neurologist with expertise in treating complex neurological disorders. He has been practicing for over 20 years.",
                "fee": 180.00,
                "rating": 4.7,
                "reviews": 156,
            },
            {
                "username": "dr_brown",
                "email": "dr.brown@example.com",
                "first_name": "Emily",
                "last_name": "Brown",
                "specialty": "Pediatrics",
                "license": "PED001",
                "experience": 10,
                "bio": "Dr. Brown is a compassionate pediatrician who loves working with children. She specializes in developmental pediatrics and preventive care.",
                "fee": 100.00,
                "rating": 4.9,
                "reviews": 203,
            },
            {
                "username": "dr_davis",
                "email": "dr.davis@example.com",
                "first_name": "Robert",
                "last_name": "Davis",
                "specialty": "Orthopedics",
                "license": "ORTHO001",
                "experience": 18,
                "bio": "Dr. Davis is an orthopedic surgeon specializing in sports medicine and joint replacement. He has helped many athletes return to their peak performance.",
                "fee": 200.00,
                "rating": 4.6,
                "reviews": 98,
            },
            {
                "username": "dr_wilson",
                "email": "dr.wilson@example.com",
                "first_name": "Lisa",
                "last_name": "Wilson",
                "specialty": "General Medicine",
                "license": "GEN001",
                "experience": 8,
                "bio": "Dr. Wilson is a family medicine physician who provides comprehensive healthcare for patients of all ages. She focuses on preventive care and wellness.",
                "fee": 80.00,
                "rating": 4.8,
                "reviews": 145,
            },
        ]

        for doc_data in doctors_data:
            # Create user
            user, created = User.objects.get_or_create(
                username=doc_data["username"],
                defaults={
                    "email": doc_data["email"],
                    "first_name": doc_data["first_name"],
                    "last_name": doc_data["last_name"],
                },
            )
            if created:
                user.set_password("doctor123")
                user.save()

            # Create doctor profile
            specialty = Specialty.objects.get(name=doc_data["specialty"])
            doctor, created = Doctor.objects.get_or_create(
                user=user,
                defaults={
                    "specialty": specialty,
                    "license_number": doc_data["license"],
                    "experience_years": doc_data["experience"],
                    "bio": doc_data["bio"],
                    "consultation_fee": Decimal(str(doc_data["fee"])),
                    "average_rating": Decimal(str(doc_data["rating"])),
                    "total_reviews": doc_data["reviews"],
                    "created_by": admin_user,
                },
            )
            if created:
                self.stdout.write(
                    f"Created doctor: Dr. {user.first_name} {user.last_name}"
                )

        self.stdout.write(self.style.SUCCESS("Successfully created sample data!"))
