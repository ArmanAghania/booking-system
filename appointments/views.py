from django.shortcuts import render
from django.http import HttpResponse


# Placeholder views - to be implemented
def list_view(request):
    return HttpResponse("Appointments list - Coming soon!")


def my_appointments_view(request):
    return HttpResponse("My appointments - Coming soon!")


def book_view(request, doctor_id):
    return HttpResponse(f"Book appointment with doctor {doctor_id} - Coming soon!")
