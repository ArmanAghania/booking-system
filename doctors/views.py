from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy, reverse

from .models import Specialty, Doctor
from .forms import SpecialtyForm, DoctorCreationForm
from .mixins import AdminRequiredMixin, is_admin_user


class SpecialtyListView(ListView):

    model = Specialty
    template_name = "doctors/specialty_list.html"
    context_object_name = "specialties"
    paginate_by = 10
    ordering = ["name"]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["total_specialties"] = self.get_queryset().count()
        return context


class SpecialtyDetailView(DetailView):

    model = Specialty
    template_name = "doctors/specialty_detail.html"
    context_object_name = "specialty"
    pk_url_kwarg = "specialty_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        specialty = self.get_object()

        doctors = (
            Doctor.objects.filter(specialty=specialty, is_active=True)
            .select_related("user")
            .order_by("user__last_name")
        )

        context["doctors"] = doctors
        context["doctor_count"] = doctors.count()
        return context


class SpecialtyCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):

    model = Specialty
    form_class = SpecialtyForm
    template_name = "doctors/specialty_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create New Specialty"
        context["submit_text"] = "Create Specialty"
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, f'Specialty "{self.object.name}" created successfully!'
        )
        return response

    def get_success_url(self):
        return reverse(
            "doctors:specialty_detail", kwargs={"specialty_id": self.object.id}
        )


class SpecialtyUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):

    model = Specialty
    form_class = SpecialtyForm
    template_name = "doctors/specialty_form.html"
    pk_url_kwarg = "specialty_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Update {self.object.name}"
        context["submit_text"] = "Update Specialty"
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, f'Specialty "{self.object.name}" updated successfully!'
        )
        return response

    def get_success_url(self):
        return reverse(
            "doctors:specialty_detail", kwargs={"specialty_id": self.object.id}
        )


class SpecialtyDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):

    model = Specialty
    template_name = "doctors/specialty_confirm_delete.html"
    pk_url_kwarg = "specialty_id"
    success_url = reverse_lazy("doctors:specialty_list")

    def delete(self, request, *args, **kwargs):
        specialty = self.get_object()
        doctor_count = specialty.doctor_set.count()

        if doctor_count > 0:
            messages.error(
                request,
                f'Cannot delete "{specialty.name}" because it has {doctor_count} doctor(s) assigned to it.',
            )
            return redirect("doctors:specialty_detail", specialty_id=specialty.id)

        specialty_name = specialty.name
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Specialty "{specialty_name}" deleted successfully!')
        return response


class DoctorListView(ListView):

    model = Doctor
    template_name = "doctors/doctor_list.html"
    context_object_name = "doctors"
    paginate_by = 12
    ordering = ["user__last_name"]

    def get_queryset(self):
        queryset = (
            Doctor.objects.filter(is_active=True)
            .select_related("user", "specialty")
            .order_by("user__last_name", "user__first_name")
        )

        search_query = self.request.GET.get("search", "")
        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query)
                | Q(user__last_name__icontains=search_query)
                | Q(specialty__name__icontains=search_query)
                | Q(bio__icontains=search_query)
            )

        specialty_filter = self.request.GET.get("specialty", "")
        if specialty_filter:
            queryset = queryset.filter(specialty_id=specialty_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["specialty_filter"] = self.request.GET.get("specialty", "")
        context["specialties"] = Specialty.objects.all().order_by("name")
        context["total_doctors"] = self.get_queryset().count()
        return context


class DoctorDetailView(DetailView):

    model = Doctor
    template_name = "doctors/doctor_detail.html"
    context_object_name = "doctor"
    pk_url_kwarg = "doctor_id"

    def get_queryset(self):
        return (
            Doctor.objects.filter(is_active=True)
            .select_related("user", "specialty")
            .order_by("user__last_name", "user__first_name")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = self.get_object()

        # Get reviews for this doctor
        from reviews.models import Review

        reviews = (
            Review.objects.filter(doctor=doctor)
            .select_related("patient")
            .order_by("-created_at")[:5]
        )
        context["reviews"] = reviews
        context["total_reviews"] = Review.objects.filter(doctor=doctor).count()

        # Get available time slots for this doctor
        from appointments.models import TimeSlot
        from django.utils import timezone
        from datetime import date

        # Get one slot per day for the next 6 days
        from django.db.models import Min
        from datetime import timedelta

        start_date = date.today()
        end_date = start_date + timedelta(days=6)

        # Get the earliest available slot for each day
        daily_slots = []
        for i in range(6):
            current_date = start_date + timedelta(days=i)
            earliest_slot = (
                TimeSlot.objects.filter(
                    doctor=doctor, is_available=True, date=current_date
                )
                .order_by("start_time")
                .first()
            )

            if earliest_slot:
                daily_slots.append(earliest_slot)

        available_slots = daily_slots

        context["available_slots"] = available_slots

        return context


class DoctorCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):

    model = Doctor
    form_class = DoctorCreationForm
    template_name = "doctors/doctor_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create New Doctor"
        context["submit_text"] = "Create Doctor"
        context["specialties"] = Specialty.objects.all().order_by("name")
        return context

    def form_valid(self, form):
        try:
            doctor = form.save(created_by=self.request.user)

            self.object = doctor

            messages.success(
                self.request,
                f'Doctor "{self.object.user.get_full_name()}" created successfully!',
            )

            return redirect(self.get_success_url())
        except Exception as e:
            messages.error(
                self.request,
                f"Error creating doctor: {str(e)}",
            )
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("doctors:doctor_detail", kwargs={"doctor_id": self.object.id})
