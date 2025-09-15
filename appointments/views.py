
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.dateparse import parse_date
from datetime import date
from .models import TimeSlot
from doctors.models import Doctor


# Placeholder views - to be implemented
def list_view(request):
    return HttpResponse("Appointments list - Coming soon!")


def my_appointments_view(request):
    return HttpResponse("My appointments - Coming soon!")



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
