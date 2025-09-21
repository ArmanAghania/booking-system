from django.db import transaction
from django.http import HttpResponse
from django.utils.dateparse import parse_date
from datetime import date
from doctors.models import Doctor
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import TimeSlot, Appointment
from .forms import AppointmentForm


def appointment_list(request):
    appointments = Appointment.objects.all()
    return render(request, "appointments/appointment_list.html", {"appointments": appointments})


def my_appointments_view(request):
    return HttpResponse("My appointments - Coming soon!")


@login_required
def book_view(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    slots = TimeSlot.objects.filter(
        doctor=doctor,
        is_available=True,
        date__gte=date.today()
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
        return redirect("appointments:book_view", doctor_id=slot.doctor.id)

    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    slot = TimeSlot.objects.select_for_update().get(id=slot_id)
                    if not slot.is_available:
                        messages.error(request, " Sorry, this time slot has just been booked by someone else.")
                        return redirect("appointments:book_view", doctor_id=slot.doctor.id)

                    appointment = form.save(commit=False)
                    appointment.time_slot = slot
                    appointment.doctor = slot.doctor
                    appointment.patient = request.user
                    appointment.consultation_fee = slot.doctor.consultation_fee
                    appointment.status = "PENDING"
                    appointment.save()
                    slot.is_available = False
                    slot.save()

                    messages.success(request, " Your appointment has been submitted successfully!")
                    return redirect("appointments:booking_confirmation", appointment_id=appointment.id)

            except Exception as e:
                messages.error(request, f" An error occurred: {str(e)}")
                return redirect("appointments:book_view", doctor_id=slot.doctor.id)
    else:
        form = AppointmentForm()

    return render(request, "appointments/reserve_slot.html", {
        "slot": slot,
        "form": form,
    })


@login_required
def booking_confirmation_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    return render(request, "appointments/confirmation.html", {
        "appointment": appointment
    })
