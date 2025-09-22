from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.utils.dateparse import parse_date
from datetime import date, timedelta
from doctors.models import Doctor
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import TimeSlot, Appointment
from .forms import AppointmentForm


@login_required
def appointment_list(request):
    """Show appointments for the logged-in patient."""
    appointments = Appointment.objects.filter(patient=request.user).order_by(
        "-created_at"
    )
    return render(
        request, "appointments/appointment_list.html", {"appointments": appointments}
    )


@login_required
def my_appointments_view(request):
    """Redirect to the appointment list for the logged-in user."""
    return redirect("appointments:appointment_list")


@login_required
def book_view(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    slots = TimeSlot.objects.filter(
        doctor=doctor, is_available=True, date__gte=date.today()
    ).order_by("date", "start_time")

    start_date = request.GET.get("start")
    end_date = request.GET.get("end")

    if start_date:
        slots = slots.filter(date__gte=parse_date(start_date))
    if end_date:
        slots = slots.filter(date__lte=parse_date(end_date))

    context = {
        "doctor": doctor,
        "slots": slots,
    }
    return render(request, "appointments/book.html", context)


@login_required
def reserve_slot_view(request, slot_id):
    slot = get_object_or_404(TimeSlot, id=slot_id)

    if not slot.is_available:
        messages.error(request, " This time slot is no longer available.")
        return redirect("appointments:book", doctor_id=slot.doctor.id)

    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    slot = TimeSlot.objects.select_for_update().get(id=slot_id)
                    if not slot.is_available:
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

                    messages.success(
                        request,
                        " Appointment created! Please complete payment to confirm your booking.",
                    )
                    return redirect(
                        "payments:process_payment",
                        appointment_id=appointment.id,
                    )

            except Exception as e:
                messages.error(request, f" An error occurred: {str(e)}")
                return redirect("appointments:book", doctor_id=slot.doctor.id)
    else:
        form = AppointmentForm()

    return render(
        request,
        "appointments/reserve_slot.html",
        {
            "slot": slot,
            "form": form,
        },
    )


@login_required
def booking_confirmation_view(request, appointment_id):
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

                messages.success(request, "Appointment cancelled successfully.")
                return redirect("appointments:appointment_list")
        else:
            messages.error(request, "This appointment cannot be cancelled.")
            return redirect("appointments:appointment_list")

    return render(
        request, "appointments/cancel_appointment.html", {"appointment": appointment}
    )


@login_required
def pay_appointment_view(request, appointment_id):
    """Redirect to payment for a pending appointment."""
    appointment = get_object_or_404(
        Appointment, id=appointment_id, patient=request.user
    )

    if appointment.status != "PENDING":
        messages.error(request, "This appointment is not pending payment.")
        return redirect("appointments:appointment_list")

    return redirect("payments:process_payment", appointment_id=appointment.id)


def calendar_book_view(request, doctor_id):
    """Calendar-based booking view with modern UX."""
    doctor = get_object_or_404(Doctor, id=doctor_id)

    # Get the selected date from query params
    selected_date = request.GET.get("date")
    if selected_date:
        try:
            selected_date = parse_date(selected_date)
        except:
            selected_date = date.today()
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
