from calendar import weekday

from django.db import transaction
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.dateparse import parse_date
from datetime import date, timedelta, datetime
from doctors.models import Doctor
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from .models import TimeSlot, Appointment
from .forms import (
    AppointmentForm,
    AdminAddTimeSlot,
    BulkTimeSlotForm,
    DeleteTimeSlotForm,
    DeleteDayForm,
)

# Imports needed for sending email
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


@login_required
def appointment_list(request):
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
    appointments = Appointment.objects.filter(patient=request.user).order_by(
        "-time_slot__date", "-time_slot__start_time"
    )
    context = {"appointments": appointments}
    return render(request, "appointments/my_appointments.html", context)


@login_required
def book_view(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    slots = TimeSlot.objects.filter(
        doctor=doctor, is_available=True, date__gte=date.today()
    ).order_by("date", "start_time")
    context = {"doctor": doctor, "slots": slots}
    return render(request, "appointments/book.html", context)


@login_required
def calendar_book_view(request, doctor_id):
    """Calendar-based booking view for selecting appointment dates and times."""
    doctor = get_object_or_404(Doctor, id=doctor_id)

    # Get selected date from query parameter or default to today
    selected_date_str = request.GET.get("date")
    if selected_date_str:
        try:
            selected_date = parse_date(selected_date_str)
        except (ValueError, TypeError):
            selected_date = date.today()
    else:
        selected_date = date.today()

    # Get all available slots for the doctor
    all_slots = TimeSlot.objects.filter(
        doctor=doctor, is_available=True, date__gte=date.today()
    ).order_by("date", "start_time")

    # Get slots for the selected date
    available_slots = all_slots.filter(date=selected_date)

    # Get all dates that have available slots
    dates_with_slots = (
        all_slots.values_list("date", flat=True).distinct().order_by("date")
    )

    context = {
        "doctor": doctor,
        "selected_date": selected_date,
        "available_slots": available_slots,
        "dates_with_slots": dates_with_slots,
    }
    return render(request, "appointments/calendar_book.html", context)


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
                        messages.error(
                            request,
                            "Sorry, this time slot has just been booked by someone else.",
                        )
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
                    from_email = "no-reply@bookingsystem.com"
                    to_email = [request.user.email]
                    email_context = {
                        "patient_name": request.user.get_full_name(),
                        "doctor_name": appointment.doctor.user.get_full_name(),
                        "doctor_specialty": appointment.doctor.specialty.name,
                        "appointment_date": appointment.time_slot.date.strftime(
                            "%B %d, %Y"
                        ),
                        "appointment_time": appointment.time_slot.start_time.strftime(
                            "%I:%M %p"
                        ),
                    }
                    html_content = render_to_string(
                        "appointments/email/booking_confirmation.html", email_context
                    )
                    text_content = render_to_string(
                        "appointments/email/booking_confirmation.txt", email_context
                    )
                    email = EmailMultiAlternatives(
                        subject, text_content, from_email, to_email
                    )
                    email.attach_alternative(html_content, "text/html")
                    email.send()

                    messages.success(
                        request,
                        "Your appointment has been submitted successfully! A confirmation has been sent to your email.",
                    )
                    return redirect(
                        "appointments:booking_confirmation",
                        appointment_id=appointment.id,
                    )
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

    return render(
        request, "appointments/reserve_slot.html", {"slot": slot, "form": form}
    )


@login_required
def booking_confirmation_view(request, appointment_id):

    appointment = get_object_or_404(
        Appointment, id=appointment_id, patient=request.user
    )
    return render(
        request, "appointments/confirmation.html", {"appointment": appointment}
    )

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
def mark_completed(request, appointment_id):
    """Mark an appointment as completed by the patient."""
    appointment = get_object_or_404(
        Appointment, id=appointment_id, patient=request.user
    )

    if appointment.status != "CONFIRMED":
        messages.error(
            request, "Only confirmed appointments can be marked as completed."
        )
        return redirect("appointments:appointment_list")

    if request.method == "POST":
        appointment.status = "COMPLETED"
        appointment.save()
        messages.success(
            request, "Appointment marked as completed! You can now leave a review."
        )
        return redirect("appointments:appointment_list")

    return redirect("appointments:appointment_list")


@login_required
def update_appointment_status(request, appointment_id):
    if request.method != "POST":
        return HttpResponseForbidden("Invalid request method.")
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    if (
        not hasattr(request.user, "doctor_profile")
        or request.user.doctor_profile != appointment.doctor
    ):
        if not request.user.is_superuser:
            return HttpResponseForbidden("You do not have permission to change this.")
    new_status = request.POST.get("status")
    valid_statuses = [choice[0] for choice in Appointment.STATUS_CHOICES]
    if new_status in valid_statuses:
        appointment.status = new_status
        appointment.save()
        messages.success(
            request,
            f"Appointment status updated to {appointment.get_status_display()}.",
        )
    else:
        messages.error(request, "Invalid status selected.")
    return redirect("appointments:appointment_list")


def admin_add_time_slot_view(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.method == "POST":
        form = AdminAddTimeSlot(request.POST)
        if form.is_valid():
            date = form.cleaned_data["date"]
            start_times = form.cleaned_data["start_time"]

            start_date = date
            end_date = datetime(date.year, 12, 31).date()
            weekday = start_date.weekday()

            current_date = start_date
            while current_date <= end_date:
                if current_date.weekday() == weekday:
                    for start in start_times:
                        start = datetime.strptime(start, "%H:%M:%S").time()
                        end = (
                            datetime.combine(current_date, start)
                            + timedelta(minutes=15)
                        ).time()
                        TimeSlot.objects.get_or_create(
                            doctor=doctor,
                            date=current_date,
                            start_time=start,
                            end_time=end,
                        )
                current_date += timedelta(days=1)

            return redirect("doctors:doctor_detail", doctor_id=doctor.id)
    else:
        form = AdminAddTimeSlot()

    return render(
        request,
        "appointments/admin_add_time_slot.html",
        {"form": form, "doctor": doctor},
    )


@login_required
def time_slot_management_view(request, doctor_id):
    """Enhanced time slot management with calendar preview and bulk operations"""
    doctor = get_object_or_404(Doctor, id=doctor_id)

    # Get existing time slots for the next 3 months
    from datetime import date, timedelta

    start_date = date.today()
    end_date = start_date + timedelta(days=90)

    time_slots = TimeSlot.objects.filter(
        doctor=doctor, date__range=[start_date, end_date]
    ).order_by("date", "start_time")

    # Paginate time slots
    paginator = Paginator(time_slots, 20)  # 20 slots per page
    page_number = request.GET.get("page")
    time_slots_page = paginator.get_page(page_number)

    # Group time slots by date for calendar display
    slots_by_date = {}
    for slot in time_slots:
        date_str = slot.date.strftime("%Y-%m-%d")
        if date_str not in slots_by_date:
            slots_by_date[date_str] = []
        slots_by_date[date_str].append(slot)

    # Generate calendar grid for the current month
    from calendar import monthcalendar
    import calendar as cal

    # Get calendar month (from URL parameters or current month)
    current_date = date.today()
    year = request.GET.get("year", current_date.year)
    month = request.GET.get("month", current_date.month)

    # Convert to integers and validate
    try:
        year = int(year)
        month = int(month)
        # Validate month range
        if month < 1 or month > 12:
            month = current_date.month
        # Validate year range (reasonable bounds)
        if year < 2020 or year > 2030:
            year = current_date.year
    except (ValueError, TypeError):
        year = current_date.year
        month = current_date.month

    # Generate calendar grid (list of weeks, each week is a list of days)
    calendar_grid = monthcalendar(year, month)

    # Create a list of all days in the month with their slots
    calendar_days = []
    for week in calendar_grid:
        week_days = []
        for day in week:
            if day == 0:  # Empty day (not in current month)
                week_days.append({"day": None, "date": None, "slots": []})
            else:
                day_date = date(year, month, day)
                date_str = day_date.strftime("%Y-%m-%d")
                day_slots = slots_by_date.get(date_str, [])
                week_days.append(
                    {
                        "day": day,
                        "date": day_date,
                        "slots": day_slots,
                        "is_today": day_date == current_date,
                    }
                )
        calendar_days.append(week_days)

    # Calculate statistics
    total_slots = time_slots.count()
    available_slots = time_slots.filter(appointment__isnull=True).count()
    booked_slots = time_slots.filter(appointment__isnull=False).count()

    # Initialize forms
    bulk_form = BulkTimeSlotForm()
    delete_day_form = DeleteDayForm()

    # Calculate navigation URLs
    prev_month = month - 1
    prev_year = year
    if prev_month < 1:
        prev_month = 12
        prev_year = year - 1

    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year = year + 1

    # Generate month/year options for dropdown
    month_options = [(i, cal.month_name[i]) for i in range(1, 13)]
    year_options = [
        (i, str(i)) for i in range(current_date.year - 1, current_date.year + 3)
    ]

    context = {
        "doctor": doctor,
        "time_slots": time_slots_page,
        "slots_by_date": slots_by_date,
        "bulk_form": bulk_form,
        "delete_day_form": delete_day_form,
        "start_date": start_date,
        "end_date": end_date,
        "total_slots": total_slots,
        "available_slots": available_slots,
        "booked_slots": booked_slots,
        "calendar_days": calendar_days,
        "current_year": year,
        "current_month": month,
        "current_month_name": cal.month_name[month],
        "prev_year": prev_year,
        "prev_month": prev_month,
        "next_year": next_year,
        "next_month": next_month,
        "month_options": month_options,
        "year_options": year_options,
        "is_current_month": year == current_date.year and month == current_date.month,
    }

    return render(request, "appointments/time_slot_management.html", context)


@login_required
def bulk_create_time_slots_view(request, doctor_id):
    """Create time slots in bulk for selected days and times"""
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.method == "POST":
        form = BulkTimeSlotForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]
            weekdays = [int(day) for day in form.cleaned_data["weekdays"]]
            start_times = form.cleaned_data["start_time"]

            created_count = 0
            skipped_count = 0
            current_date = start_date

            while current_date <= end_date:
                if current_date.weekday() in weekdays:
                    for start_time_str in start_times:
                        start_time = datetime.strptime(
                            start_time_str, "%H:%M:%S"
                        ).time()
                        end_time = (
                            datetime.combine(current_date, start_time)
                            + timedelta(minutes=15)
                        ).time()

                        # Use get_or_create to avoid duplicates and handle validation errors
                        try:
                            slot, created = TimeSlot.objects.get_or_create(
                                doctor=doctor,
                                date=current_date,
                                start_time=start_time,
                                end_time=end_time,
                                defaults={"created_by": request.user},
                            )
                            if created:
                                created_count += 1
                        except Exception as e:
                            # Skip slots that can't be created due to validation errors
                            print(f"Skipping slot due to validation error: {e}")
                            skipped_count += 1
                            continue

                current_date += timedelta(days=1)

            if created_count > 0:
                if skipped_count > 0:
                    messages.success(
                        request,
                        f"Successfully created {created_count} time slots. {skipped_count} slots were skipped due to conflicts.",
                    )
                else:
                    messages.success(
                        request, f"Successfully created {created_count} time slots."
                    )
            else:
                messages.warning(
                    request,
                    f"No new time slots were created. {skipped_count} slots were skipped due to conflicts.",
                )
            return redirect("appointments:time_slot_management", doctor_id=doctor.id)

    return redirect("appointments:time_slot_management", doctor_id=doctor.id)


@login_required
def delete_time_slot_view(request, time_slot_id):
    """Delete a specific time slot"""
    time_slot = get_object_or_404(TimeSlot, id=time_slot_id)
    doctor_id = time_slot.doctor.id

    # Check if time slot has an appointment
    if hasattr(time_slot, "appointment"):
        messages.error(request, "Cannot delete time slot that has an appointment.")
    else:
        time_slot.delete()
        messages.success(request, "Time slot deleted successfully.")

    return redirect("appointments:time_slot_management", doctor_id=doctor_id)


@login_required
def delete_day_slots_view(request, doctor_id):
    """Delete all time slots for a specific day"""
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.method == "POST":
        form = DeleteDayForm(request.POST)
        if form.is_valid():
            date_to_clear = form.cleaned_data["date"]

            # Get all time slots for this date
            slots_to_delete = TimeSlot.objects.filter(doctor=doctor, date=date_to_clear)

            # Check if any slots have appointments
            slots_with_appointments = slots_to_delete.filter(appointment__isnull=False)

            if slots_with_appointments.exists():
                messages.error(
                    request,
                    f"Cannot delete time slots for {date_to_clear} because some have appointments.",
                )
            else:
                deleted_count = slots_to_delete.count()
                slots_to_delete.delete()
                messages.success(
                    request, f"Deleted {deleted_count} time slots for {date_to_clear}."
                )

    return redirect("appointments:time_slot_management", doctor_id=doctor_id)
