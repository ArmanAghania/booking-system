from django.shortcuts import render
from django.db.models import Q
from doctors.models import Doctor, Specialty


def home(request):
    """Home page with search functionality"""
    query = request.GET.get("q", "")
    specialty_filter = request.GET.get("specialty", "")

    doctors = Doctor.objects.filter(is_active=True)
    specialties = Specialty.objects.all()

    if query:
        doctors = doctors.filter(
            Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(specialty__name__icontains=query)
            | Q(bio__icontains=query)
        )

    if specialty_filter:
        doctors = doctors.filter(specialty_id=specialty_filter)

    context = {
        "doctors": doctors[:6],  # Show only first 6 for preview
        "specialties": specialties,
        "query": query,
        "specialty_filter": specialty_filter,
        "total_doctors": Doctor.objects.filter(is_active=True).count(),
    }

    return render(request, "core/home.html", context)
