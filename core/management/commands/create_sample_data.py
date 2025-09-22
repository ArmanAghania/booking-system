from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta, date, time
from decimal import Decimal
import random

from doctors.models import Specialty, Doctor
from appointments.models import TimeSlot, Appointment
from payments.models import Payment, WalletTransaction
from reviews.models import Review

User = get_user_model()


class Command(BaseCommand):
    help = "Create comprehensive sample data for complete demo"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Creating comprehensive sample data for complete demo...")

        with transaction.atomic():
            # Create all sample data
            self.create_specialties()
            self.create_admin_users()
            self.create_doctors()
            self.create_patients()
            self.create_time_slots()
            self.create_appointments()
            self.create_payments()
            self.create_wallet_transactions()
            self.create_reviews()

        self.stdout.write(
            self.style.SUCCESS("✅ Successfully created comprehensive sample data!")
        )
        self.print_demo_instructions()

    def create_specialties(self):
        """Create medical specialties."""
        self.stdout.write("📋 Creating medical specialties...")

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
            {
                "name": "Psychiatry",
                "description": "Mental health and behavioral disorders specialist",
            },
            {
                "name": "Gynecology",
                "description": "Women's reproductive health specialist",
            },
            {"name": "Ophthalmology", "description": "Eye and vision care specialist"},
            {"name": "ENT", "description": "Ear, nose, and throat specialist"},
        ]

        self.specialties = []
        for spec_data in specialties_data:
            specialty, created = Specialty.objects.get_or_create(
                name=spec_data["name"],
                defaults={"description": spec_data["description"]},
            )
            self.specialties.append(specialty)
            if created:
                self.stdout.write(f"  ✅ Created specialty: {specialty.name}")

    def create_admin_users(self):
        """Create admin users."""
        self.stdout.write("👑 Creating admin users...")

        # Super admin
        self.admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@bookingsystem.com",
                "first_name": "System",
                "last_name": "Administrator",
                "user_type": "admin",
                "is_staff": True,
                "is_superuser": True,
                "is_verified": True,
                "phone_number": "+1-555-0100",
            },
        )
        if created:
            self.admin_user.set_password("admin123")
            self.admin_user.save()
            self.stdout.write("  ✅ Created super admin: admin/admin123")

        # Regular admin
        self.regular_admin, created = User.objects.get_or_create(
            username="admin2",
            defaults={
                "email": "admin2@bookingsystem.com",
                "first_name": "Jane",
                "last_name": "Manager",
                "user_type": "admin",
                "is_staff": True,
                "is_verified": True,
                "phone_number": "+1-555-0101",
            },
        )
        if created:
            self.regular_admin.set_password("admin123")
            self.regular_admin.save()
            self.stdout.write("  ✅ Created regular admin: admin2/admin123")

    def create_doctors(self):
        """Create diverse doctors with different specialties."""
        self.stdout.write("👨‍⚕️ Creating doctors...")

        doctors_data = [
            {
                "username": "dr_smith",
                "email": "dr.smith@bookingsystem.com",
                "first_name": "John",
                "last_name": "Smith",
                "specialty": "Cardiology",
                "license": "CARD001",
                "experience": 15,
                "bio": "Dr. Smith is a board-certified cardiologist with over 15 years of experience in treating heart conditions. He specializes in interventional cardiology and preventive care.",
                "fee": 150.00,
                "phone": "+1-555-0200",
            },
            {
                "username": "dr_johnson",
                "email": "dr.johnson@bookingsystem.com",
                "first_name": "Sarah",
                "last_name": "Johnson",
                "specialty": "Dermatology",
                "license": "DERM001",
                "experience": 12,
                "bio": "Dr. Johnson is a renowned dermatologist specializing in cosmetic dermatology and skin cancer treatment. She has published numerous research papers.",
                "fee": 120.00,
                "phone": "+1-555-0201",
            },
            {
                "username": "dr_williams",
                "email": "dr.williams@bookingsystem.com",
                "first_name": "Michael",
                "last_name": "Williams",
                "specialty": "Neurology",
                "license": "NEURO001",
                "experience": 20,
                "bio": "Dr. Williams is a leading neurologist with expertise in treating complex neurological disorders. He has been practicing for over 20 years.",
                "fee": 180.00,
                "phone": "+1-555-0202",
            },
            {
                "username": "dr_brown",
                "email": "dr.brown@bookingsystem.com",
                "first_name": "Emily",
                "last_name": "Brown",
                "specialty": "Pediatrics",
                "license": "PED001",
                "experience": 10,
                "bio": "Dr. Brown is a compassionate pediatrician who loves working with children. She specializes in developmental pediatrics and preventive care.",
                "fee": 100.00,
                "phone": "+1-555-0203",
            },
            {
                "username": "dr_davis",
                "email": "dr.davis@bookingsystem.com",
                "first_name": "Robert",
                "last_name": "Davis",
                "specialty": "Orthopedics",
                "license": "ORTHO001",
                "experience": 18,
                "bio": "Dr. Davis is an orthopedic surgeon specializing in sports medicine and joint replacement. He has helped many athletes return to their peak performance.",
                "fee": 200.00,
                "phone": "+1-555-0204",
            },
            {
                "username": "dr_wilson",
                "email": "dr.wilson@bookingsystem.com",
                "first_name": "Lisa",
                "last_name": "Wilson",
                "specialty": "General Medicine",
                "license": "GEN001",
                "experience": 8,
                "bio": "Dr. Wilson is a family medicine physician who provides comprehensive healthcare for patients of all ages. She focuses on preventive care and wellness.",
                "fee": 80.00,
                "phone": "+1-555-0205",
            },
            {
                "username": "dr_martinez",
                "email": "dr.martinez@bookingsystem.com",
                "first_name": "Maria",
                "last_name": "Martinez",
                "specialty": "Psychiatry",
                "license": "PSYCH001",
                "experience": 14,
                "bio": "Dr. Martinez is a board-certified psychiatrist specializing in mood disorders and anxiety. She combines medication management with therapy approaches.",
                "fee": 160.00,
                "phone": "+1-555-0206",
            },
            {
                "username": "dr_taylor",
                "email": "dr.taylor@bookingsystem.com",
                "first_name": "Jennifer",
                "last_name": "Taylor",
                "specialty": "Gynecology",
                "license": "GYN001",
                "experience": 16,
                "bio": "Dr. Taylor is a gynecologist with expertise in women's reproductive health, family planning, and minimally invasive procedures.",
                "fee": 140.00,
                "phone": "+1-555-0207",
            },
        ]

        self.doctors = []
        for doc_data in doctors_data:
            # Create user
            user, created = User.objects.get_or_create(
                username=doc_data["username"],
                defaults={
                    "email": doc_data["email"],
                    "first_name": doc_data["first_name"],
                    "last_name": doc_data["last_name"],
                    "user_type": "doctor",
                    "phone_number": doc_data["phone"],
                    "is_verified": True,
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
                    "created_by": self.admin_user,
                },
            )
            self.doctors.append(doctor)
            if created:
                self.stdout.write(
                    f"  ✅ Created doctor: Dr. {user.first_name} {user.last_name}"
                )

    def create_patients(self):
        """Create diverse patient users."""
        self.stdout.write("👥 Creating patient users...")

        patients_data = [
            {
                "username": "patient1",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1-555-1000",
                "wallet_balance": 500.00,
            },
            {
                "username": "patient2",
                "email": "jane.smith@example.com",
                "first_name": "Jane",
                "last_name": "Smith",
                "phone": "+1-555-1001",
                "wallet_balance": 300.00,
            },
            {
                "username": "patient3",
                "email": "mike.wilson@example.com",
                "first_name": "Mike",
                "last_name": "Wilson",
                "phone": "+1-555-1002",
                "wallet_balance": 750.00,
            },
            {
                "username": "patient4",
                "email": "sarah.johnson@example.com",
                "first_name": "Sarah",
                "last_name": "Johnson",
                "phone": "+1-555-1003",
                "wallet_balance": 200.00,
            },
            {
                "username": "patient5",
                "email": "david.brown@example.com",
                "first_name": "David",
                "last_name": "Brown",
                "phone": "+1-555-1004",
                "wallet_balance": 1000.00,
            },
            {
                "username": "patient6",
                "email": "lisa.garcia@example.com",
                "first_name": "Lisa",
                "last_name": "Garcia",
                "phone": "+1-555-1005",
                "wallet_balance": 150.00,
            },
            {
                "username": "patient7",
                "email": "robert.miller@example.com",
                "first_name": "Robert",
                "last_name": "Miller",
                "phone": "+1-555-1006",
                "wallet_balance": 400.00,
            },
            {
                "username": "patient8",
                "email": "emily.davis@example.com",
                "first_name": "Emily",
                "last_name": "Davis",
                "phone": "+1-555-1007",
                "wallet_balance": 600.00,
            },
        ]

        self.patients = []
        for patient_data in patients_data:
            user, created = User.objects.get_or_create(
                username=patient_data["username"],
                defaults={
                    "email": patient_data["email"],
                    "first_name": patient_data["first_name"],
                    "last_name": patient_data["last_name"],
                    "user_type": "patient",
                    "phone_number": patient_data["phone"],
                    "wallet_balance": Decimal(str(patient_data["wallet_balance"])),
                    "is_verified": True,
                },
            )
            if created:
                user.set_password("patient123")
                user.save()
            self.patients.append(user)
            if created:
                self.stdout.write(
                    f"  ✅ Created patient: {user.first_name} {user.last_name}"
                )

    def create_time_slots(self):
        """Create time slots for all doctors."""
        self.stdout.write("📅 Creating time slots...")

        # Generate time slots for the next 30 days
        start_date = date.today()
        time_slots_created = 0

        for doctor in self.doctors:
            for day_offset in range(30):
                current_date = start_date + timedelta(days=day_offset)

                # Skip weekends for some doctors
                if current_date.weekday() >= 5 and doctor.user.username in [
                    "dr_davis",
                    "dr_wilson",
                ]:
                    continue

                # Create 3-5 time slots per day with proper spacing
                num_slots = random.randint(3, 5)
                for slot_num in range(num_slots):
                    start_hour = 9 + (slot_num * 2)  # 9 AM, 11 AM, 1 PM, 3 PM, 5 PM
                    start_time = time(start_hour, 0)
                    end_time = time(start_hour + 1, 0)

                    # Check if this slot already exists to avoid duplicates
                    existing_slot = TimeSlot.objects.filter(
                        doctor=doctor,
                        date=current_date,
                        start_time=start_time,
                        end_time=end_time,
                    ).exists()

                    if not existing_slot:
                        # Randomly make some slots unavailable (already booked)
                        is_available = random.choice(
                            [True, True, True, False]
                        )  # 75% available

                        try:
                            TimeSlot.objects.create(
                                doctor=doctor,
                                date=current_date,
                                start_time=start_time,
                                end_time=end_time,
                                is_available=is_available,
                                created_by=self.admin_user,
                            )
                            time_slots_created += 1
                        except Exception as e:
                            # Skip if there's still an overlap issue
                            continue

        self.stdout.write(f"  ✅ Created {time_slots_created} time slots")

    def create_appointments(self):
        """Create appointments in various states."""
        self.stdout.write("📋 Creating appointments...")

        # Get available time slots that don't already have appointments
        # Use only slots from the future to avoid conflicts with live booking
        available_slots = TimeSlot.objects.filter(
            is_available=True,
            appointment__isnull=True,
            date__gte=timezone.now().date() + timedelta(days=1),  # Only future dates
        )[:20]

        appointment_notes = [
            "Regular checkup appointment",
            "Follow-up visit",
            "Annual physical examination",
            "Consultation for new symptoms",
            "Medication review",
            "Preventive care visit",
            "Specialist referral consultation",
            "Emergency consultation",
        ]

        self.appointments = []
        for i, slot in enumerate(available_slots):
            patient = random.choice(self.patients)
            status = random.choice(["PENDING", "CONFIRMED", "CANCELLED", "COMPLETED"])

            try:
                appointment = Appointment.objects.create(
                    patient=patient,
                    doctor=slot.doctor,
                    time_slot=slot,
                    status=status,
                    consultation_fee=slot.doctor.consultation_fee,
                    notes=random.choice(appointment_notes),
                )

                # Mark slot as unavailable if appointment is not cancelled
                if status != "CANCELLED":
                    slot.is_available = False
                    slot.save()

                self.appointments.append(appointment)
            except Exception as e:
                # Skip if there's a constraint violation
                self.stdout.write(
                    f"    ⚠️  Skipped slot {slot.id} due to constraint: {str(e)}"
                )
                continue

        self.stdout.write(f"  ✅ Created {len(self.appointments)} appointments")

    def create_payments(self):
        """Create payment records for confirmed appointments."""
        self.stdout.write("💳 Creating payments...")

        confirmed_appointments = [
            apt for apt in self.appointments if apt.status == "CONFIRMED"
        ]
        payments_created = 0

        for appointment in confirmed_appointments:
            Payment.objects.get_or_create(
                appointment_id=appointment,
                defaults={
                    "amount": appointment.consultation_fee,
                    "status": Payment.SUCCESS,
                },
            )
            payments_created += 1

        self.stdout.write(f"  ✅ Created {payments_created} payment records")

    def create_wallet_transactions(self):
        """Create wallet transactions for patients."""
        self.stdout.write("💰 Creating wallet transactions...")

        transactions_created = 0

        for patient in self.patients:
            # Create some deposit transactions
            for _ in range(random.randint(1, 3)):
                amount = Decimal(str(random.randint(50, 500)))
                WalletTransaction.objects.create(
                    user_id=patient,
                    transaction_type=WalletTransaction.DEPOSIT,
                    amount=amount,
                    description=f"Wallet deposit of ${amount}",
                    balance_after=patient.wallet_balance,
                )
                transactions_created += 1

            # Create withdrawal transactions for appointments
            patient_appointments = [
                apt
                for apt in self.appointments
                if apt.patient == patient and apt.status == "CONFIRMED"
            ]
            for appointment in patient_appointments:
                WalletTransaction.objects.create(
                    user_id=patient,
                    transaction_type=WalletTransaction.WITHDRAW,
                    amount=appointment.consultation_fee,
                    description=f"Payment for appointment with Dr. {appointment.doctor.user.get_full_name()}",
                    balance_after=patient.wallet_balance,
                    appointment_id=appointment,
                )
                transactions_created += 1

        self.stdout.write(f"  ✅ Created {transactions_created} wallet transactions")

    def create_reviews(self):
        """Create reviews for completed appointments."""
        self.stdout.write("⭐ Creating reviews...")

        completed_appointments = [
            apt for apt in self.appointments if apt.status == "COMPLETED"
        ]
        reviews_created = 0

        review_comments = [
            "Excellent doctor, very professional and caring.",
            "Great experience, would definitely recommend.",
            "Very knowledgeable and took time to explain everything.",
            "Friendly staff and comfortable environment.",
            "Doctor was thorough and addressed all my concerns.",
            "Quick service and effective treatment.",
            "Highly recommend this doctor to others.",
            "Professional and compassionate care.",
            "Great bedside manner and expertise.",
            "Very satisfied with the service provided.",
        ]

        for appointment in completed_appointments:
            Review.objects.get_or_create(
                appointment=appointment,
                defaults={
                    "patient": appointment.patient,
                    "doctor": appointment.doctor,
                    "rating": random.randint(3, 5),
                    "comment": random.choice(review_comments),
                    "is_anonymous": random.choice([True, False]),
                },
            )
            reviews_created += 1

        self.stdout.write(f"  ✅ Created {reviews_created} reviews")

    def print_demo_instructions(self):
        """Print demo instructions for users."""
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("🎉 COMPREHENSIVE SAMPLE DATA CREATED SUCCESSFULLY!")
        self.stdout.write("=" * 80)
        self.stdout.write("\n📋 DEMO ACCOUNTS CREATED:")
        self.stdout.write("  👑 Admin Users:")
        self.stdout.write("     • admin/admin123 (Super Admin)")
        self.stdout.write("     • admin2/admin123 (Regular Admin)")
        self.stdout.write("\n  👨‍⚕️ Doctor Users:")
        self.stdout.write("     • dr_smith/doctor123 (Cardiology)")
        self.stdout.write("     • dr_johnson/doctor123 (Dermatology)")
        self.stdout.write("     • dr_williams/doctor123 (Neurology)")
        self.stdout.write("     • dr_brown/doctor123 (Pediatrics)")
        self.stdout.write("     • dr_davis/doctor123 (Orthopedics)")
        self.stdout.write("     • dr_wilson/doctor123 (General Medicine)")
        self.stdout.write("     • dr_martinez/doctor123 (Psychiatry)")
        self.stdout.write("     • dr_taylor/doctor123 (Gynecology)")
        self.stdout.write("\n  👥 Patient Users:")
        self.stdout.write("     • patient1/patient123 (John Doe)")
        self.stdout.write("     • patient2/patient123 (Jane Smith)")
        self.stdout.write("     • patient3/patient123 (Mike Wilson)")
        self.stdout.write("     • patient4/patient123 (Sarah Johnson)")
        self.stdout.write("     • patient5/patient123 (David Brown)")
        self.stdout.write("     • patient6/patient123 (Lisa Garcia)")
        self.stdout.write("     • patient7/patient123 (Robert Miller)")
        self.stdout.write("     • patient8/patient123 (Emily Davis)")

        self.stdout.write("\n🎯 DEMO SCENARIOS TO TEST:")
        self.stdout.write("  1. 🔍 Browse doctors and specialties")
        self.stdout.write("  2. 📅 Book appointments (calendar view)")
        self.stdout.write("  3. 💳 Process payments (wallet & card)")
        self.stdout.write("  4. ⭐ Leave reviews for completed appointments")
        self.stdout.write("  5. 👑 Admin view all appointments")
        self.stdout.write("  6. 📧 Email notifications (check terminal)")
        self.stdout.write("  7. 💰 Wallet transactions and balances")
        self.stdout.write("  8. 🔄 Cancel and reschedule appointments")

        self.stdout.write("\n🚀 START THE SERVER:")
        self.stdout.write("  python manage.py runserver")
        self.stdout.write("  Then visit: http://localhost:8000")
        self.stdout.write("\n" + "=" * 80)
