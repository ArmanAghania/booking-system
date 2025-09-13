from django.shortcuts import render
from django.http import HttpResponse


# Placeholder views - to be implemented
def list_view(request):
    return HttpResponse("Doctors list - Coming soon!")


def detail_view(request, doctor_id):
    return HttpResponse(f"Doctor detail for ID {doctor_id} - Coming soon!")
