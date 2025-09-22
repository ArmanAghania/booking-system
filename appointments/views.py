from calendar import weekday

from django.db import transaction
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.dateparse import parse_date
from datetime import date, timedelta, datetime
from doctors.models import Doctor
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import TimeSlot, Appointment
from .forms import AppointmentForm, AdminAddTimeSlot

# Imports needed for sending email
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


# --- THIS FUNCTION WAS MISSING ---
def appointment_list(request):
    """
    A simple view to display all appointments in the system.
    """
    appointments = Appointment.objects.all()
    return render(request, "appointments/appointment_list.html", {"appointments": appointments})
    """Show appointments for the logged-in patient, or all appointments for admin users."""
    from doctors.mixins import is_admin_user

    if is_admin_user(request.user):
        # Admin users see all appointments
        appointments = Appointment.objects.select_related(
            "patient", "doctor", "doctor__user", "time_slot"
        ).order_by("-created_at")
        is_admin_view = True
    else:
        # Regular users see only their own appointments
        appointments = Appointment.objects.filter(patient=request.user).order_by(
            "-created_at"
        )
        is_admin_view = False

    return render(
        request,
        "appointments/appointment_list.html",
        {"appointments": appointments, "is_admin_view": is_admin_view},
    )


@login_required
def my_appointments_view(request):
    """
    Shows a list of appointments for the currently logged-in patient.
    """
    appointments = Appointment.objects.filter(patient=request.user).order_by('-time_slot__date',
                                                                             '-time_slot__start_time')
    context = {'appointments': appointments}
    return render(request, "appointments/my_appointments.html", context)


@login_required
def book_view(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    slots = TimeSlot.objects.filter(doctor=doctor, is_available=True, date__gte=date.today()).order_by("date",
                                                                                                       "start_time")
    context = {"doctor": doctor, "slots": slots}
    return render(request, "appointments/book.html", context)


# appointments/views.py

@login_required
def reserve_slot_view(request, slot_id):
    slot = get_object_or_404(TimeSlot, id=slot_id)

    if not slot.is_available:
        messages.error(request, "This time slot is no longer available.")
        # CORRECTED THIS REDIRECT
        return redirect("appointments:book", doctor_id=slot.doctor.id)

    # Check if slot already has an appointment
    if hasattr(slot, "appointment"):
        messages.error(request, " This time slot is already booked.")
        return redirect("appointments:book", doctor_id=slot.doctor.id)

    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    slot = TimeSlot.objects.select_for_update().get(id=slot_id)
                    if not slot.is_available:
                        messages.error(request, "Sorry, this time slot has just been booked by someone else.")
                        # CORRECTED THIS REDIRECT
                        return redirect("appointments:book", doctor_id=slot.doctor.id)

                    # Double-check that slot doesn't have an appointment
                    if hasattr(slot, "appointment"):
                        messages.error(
                            request,
                            " Sorry, this time slot has just been booked by someone else.",
                        )
                        return redirect("appointments:book", doctor_id=slot.doctor.id)

                    appointment = form.save(commit=False)
                    appointment.time_slot = slot
                    appointment.doctor = slot.doctor
                    appointment.patient = request.user
                    appointment.consultation_fee = slot.doctor.consultation_fee
                    appointment.status = "PENDING"
                    appointment.save()
                    slot.is_available = False
                    slot.save()

                    # Email Sending Logic
                    subject = "Your Appointment Confirmation"
                    from_email = 'no-reply@bookingsystem.com'
                    to_email = [request.user.email]
                    email_context = {
                        'patient_name': request.user.get_full_name(),
                        'doctor_name': appointment.doctor.user.get_full_name(),
                        'doctor_specialty': appointment.doctor.specialty.name,
                        'appointment_date': appointment.time_slot.date.strftime('%B %d, %Y'),
                        'appointment_time': appointment.time_slot.start_time.strftime('%I:%M %p'),
                    }
                    html_content = render_to_string('appointments/email/booking_confirmation.html', email_context)
                    text_content = render_to_string('appointments/email/booking_confirmation.txt', email_context)
                    email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
                    email.attach_alternative(html_content, "text/html")
                    email.send()

                    messages.success(request,
                                     "Your appointment has been submitted successfully! A confirmation has been sent to your email.")
                    return redirect("appointments:booking_confirmation", appointment_id=appointment.id)
                    # Send appointment reservation email
                    from .services import AppointmentEmailService

                    try:
                        AppointmentEmailService.send_reservation_confirmation(
                            appointment
                        )
                    except Exception as e:
                        # Don't fail the appointment creation if email fails
                        print(f"Warning: Could not send appointment email: {str(e)}")

                    messages.success(
                        request,
                        " Appointment created! Please complete payment to confirm your booking.",
                    )
                    return redirect(
                        "payments:process_payment",
                        appointment_id=appointment.id,
                    )

            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
                # CORRECTED THIS REDIRECT
                return redirect("appointments:book", doctor_id=slot.doctor.id)
    else:
        form = AppointmentForm()

    return render(request, "appointments/reserve_slot.html", {"slot": slot, "form": form})

@login_required
def booking_confirmation_view(request, appointment_id):

    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    return render(request, "appointments/confirmation.html", {"appointment": appointment})

    appointment = get_object_or_404(
        Appointment, id=appointment_id, patient=request.user
    )
    return render(
        request, "appointments/confirmation.html", {"appointment": appointment}
    )


@login_required
def cancel_appointment_view(request, appointment_id):
    """Cancel an appointment."""
    appointment = get_object_or_404(
        Appointment, id=appointment_id, patient=request.user
    )

    if request.method == "POST":
        # Only allow cancellation of pending or confirmed appointments
        if appointment.status in ["PENDING", "CONFIRMED"]:
            with transaction.atomic():
                # Update appointment status
                appointment.status = "CANCELLED"
                appointment.save()

                # Make the time slot available again
                appointment.time_slot.is_available = True
                appointment.time_slot.save()

                # Send cancellation email
                from .services import AppointmentEmailService

                try:
                    AppointmentEmailService.send_cancellation_notification(appointment)
                except Exception as e:
                    # Don't fail the cancellation if email fails
                    print(f"Warning: Could not send cancellation email: {str(e)}")

                messages.success(request, "Appointment cancelled successfully.")
                return redirect("appointments:appointment_list")
        else:
            messages.error(request, "This appointment cannot be cancelled.")
            return redirect("appointments:appointment_list")

    return render(
        request, "appointments/cancel_appointment.html", {"appointment": appointment}
    )



@login_required
def update_appointment_status(request, appointment_id):
    if request.method != 'POST': return HttpResponseForbidden("Invalid request method.")
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    if not hasattr(request.user, 'doctor_profile') or request.user.doctor_profile != appointment.doctor:
        if not request.user.is_superuser: return HttpResponseForbidden("You do not have permission to change this.")
    new_status = request.POST.get('status')
    valid_statuses = [choice[0] for choice in Appointment.STATUS_CHOICES]
    if new_status in valid_statuses:
        appointment.status = new_status
        appointment.save()
        messages.success(request, f"Appointment status updated to {appointment.get_status_display()}.")
    else:
        selected_date = date.today()

    # Get available slots for the selected date
    available_slots = TimeSlot.objects.filter(
        doctor=doctor, is_available=True, date=selected_date
    ).order_by("start_time")

    # Get dates with available slots for the calendar
    start_date = date.today()
    end_date = start_date + timedelta(days=30)  # Show next 30 days

    dates_with_slots = (
        TimeSlot.objects.filter(
            doctor=doctor, is_available=True, date__gte=start_date, date__lte=end_date
        )
        .values_list("date", flat=True)
        .distinct()
        .order_by("date")
    )

    context = {
        "doctor": doctor,
        "selected_date": selected_date,
        "available_slots": available_slots,
        "dates_with_slots": dates_with_slots,
        "start_date": start_date,
        "end_date": end_date,
    }
    return render(request, "appointments/calendar_book.html", context)


def admin_add_time_slot_view(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.method == "POST":
        form = AdminAddTimeSlot(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            start_times = form.cleaned_data['start_time']

            start_date = date
            end_date = datetime(date.year, 12, 31).date()
            weekday = start_date.weekday()

            current_date = start_date
            while current_date <= end_date:
                if current_date.weekday() == weekday:
                    for start in start_times:
                        start = datetime.strptime(start, "%H:%M:%S").time()
                        end = (datetime.combine(current_date, start) + timedelta(minutes=15)).time()
                        TimeSlot.objects.get_or_create(
                            doctor=doctor,
                            date=current_date,
                            start_time=start,
                            end_time=end
                        )
                current_date += timedelta(days=1)

            return redirect("appointments:appointment_list")
    else:
        form = AdminAddTimeSlot()

    return render(request, "appointments/admin_add_time_slot.html", {"form": form, "doctor": doctor})
        messages.error(request, "Invalid status selected.")
    return redirect('appointments:appointment_list')
