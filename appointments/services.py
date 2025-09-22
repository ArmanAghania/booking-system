from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse


class AppointmentEmailService:
    """Service for sending appointment-related emails."""

    @staticmethod
    def send_reservation_confirmation(appointment):
        """Send appointment reservation confirmation email."""

        # Get payment URL
        payment_url = f"{settings.SITE_URL}{reverse('payments:process_payment', args=[appointment.id])}"

        subject = f"Appointment Reserved - Dr. {appointment.doctor.user.get_full_name()} - {appointment.time_slot.date}"

        html_message = render_to_string(
            "appointments/emails/appointment_reservation.html",
            {
                "appointment": appointment,
                "payment_url": payment_url,
            },
        )

        # Build notes section
        notes_section = ""
        if appointment.notes:
            notes_section = f"\nNotes: {appointment.notes}"

        # Build next steps section
        next_steps = ""
        if appointment.status == "PENDING":
            next_steps = f"""
NEXT STEPS:
===========
1. Complete your payment to confirm the appointment
2. You will receive a confirmation email once payment is processed
3. Keep this email as your appointment reference

Payment Link: {payment_url}"""

        plain_message = f"""Hello {appointment.patient.first_name},

Your appointment has been successfully reserved!

APPOINTMENT DETAILS:
===================
Doctor: Dr. {appointment.doctor.user.get_full_name()}
Specialty: {appointment.doctor.specialty.name}
Date: {appointment.time_slot.date.strftime('%A, %B %d, %Y')}
Time: {appointment.time_slot.start_time.strftime('%I:%M %p')} - {appointment.time_slot.end_time.strftime('%I:%M %p')}
Consultation Fee: ${appointment.consultation_fee}
Status: {appointment.status}{notes_section}{next_steps}

IMPORTANT REMINDERS:
===================
- Please arrive 10 minutes before your scheduled appointment time
- If you need to cancel or reschedule, contact us at least 24 hours in advance
- Bring a valid ID and insurance information (if applicable)

If you have any questions, please contact our support team.

Best regards,
Booking System Team"""

        # Print to terminal (since we're using console email backend)
        print("\n" + "=" * 80)
        print("📧 APPOINTMENT RESERVATION EMAIL")
        print("=" * 80)
        print(f"To: {appointment.patient.email}")
        print(f"Subject: {subject}")
        print("-" * 80)
        print(plain_message)
        print("=" * 80 + "\n")

        # Send email (will be printed to console due to EMAIL_BACKEND setting)
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[appointment.patient.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"❌ Error sending appointment email: {str(e)}")
            return False

    @staticmethod
    def send_payment_confirmation(appointment):
        """Send payment confirmation email."""

        subject = f"Payment Confirmed - Appointment with Dr. {appointment.doctor.user.get_full_name()}"

        plain_message = f"""
        Hello {appointment.patient.first_name},
        
        Great news! Your payment has been confirmed and your appointment is now confirmed.
        
        APPOINTMENT CONFIRMED:
        =====================
        Doctor: Dr. {appointment.doctor.user.get_full_name()}
        Specialty: {appointment.doctor.specialty.name}
        Date: {appointment.time_slot.date.strftime('%A, %B %d, %Y')}
        Time: {appointment.time_slot.start_time.strftime('%I:%M %p')} - {appointment.time_slot.end_time.strftime('%I:%M %p')}
        Amount Paid: ${appointment.consultation_fee}
        Status: CONFIRMED
        
        Your appointment is now confirmed! Please arrive 10 minutes before your scheduled time.
        
        If you need to cancel or reschedule, please contact us at least 24 hours in advance.
        
        Best regards,
        Booking System Team
        """

        # Print to terminal
        print("\n" + "=" * 80)
        print("📧 PAYMENT CONFIRMATION EMAIL")
        print("=" * 80)
        print(f"To: {appointment.patient.email}")
        print(f"Subject: {subject}")
        print("-" * 80)
        print(plain_message)
        print("=" * 80 + "\n")

        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[appointment.patient.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"❌ Error sending payment confirmation email: {str(e)}")
            return False

    @staticmethod
    def send_cancellation_notification(appointment):
        """Send appointment cancellation notification."""

        subject = (
            f"Appointment Cancelled - Dr. {appointment.doctor.user.get_full_name()}"
        )

        plain_message = f"""
        Hello {appointment.patient.first_name},
        
        Your appointment has been cancelled as requested.
        
        CANCELLED APPOINTMENT:
        =====================
        Doctor: Dr. {appointment.doctor.user.get_full_name()}
        Specialty: {appointment.doctor.specialty.name}
        Date: {appointment.time_slot.date.strftime('%A, %B %d, %Y')}
        Time: {appointment.time_slot.start_time.strftime('%I:%M %p')} - {appointment.time_slot.end_time.strftime('%I:%M %p')}
        Status: CANCELLED
        
        If you need to book a new appointment, please visit our website or contact us.
        
        Best regards,
        Booking System Team
        """

        # Print to terminal
        print("\n" + "=" * 80)
        print("📧 APPOINTMENT CANCELLATION EMAIL")
        print("=" * 80)
        print(f"To: {appointment.patient.email}")
        print(f"Subject: {subject}")
        print("-" * 80)
        print(plain_message)
        print("=" * 80 + "\n")

        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[appointment.patient.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"❌ Error sending cancellation email: {str(e)}")
            return False
