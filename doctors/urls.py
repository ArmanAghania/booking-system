from django.urls import path
from . import views

app_name = "doctors"

urlpatterns = [
    # Doctor URLs
    path("", views.DoctorListView.as_view(), name="doctor_list"),
    path("doctors/create/", views.DoctorCreateView.as_view(), name="doctor_create"),
    path(
        "doctors/<int:doctor_id>/",
        views.DoctorDetailView.as_view(),
        name="doctor_detail",
    ),
    # Specialty URLs
    path("specialties/", views.SpecialtyListView.as_view(), name="specialty_list"),
    path(
        "specialties/<int:specialty_id>/",
        views.SpecialtyDetailView.as_view(),
        name="specialty_detail",
    ),
    path(
        "specialties/create/",
        views.SpecialtyCreateView.as_view(),
        name="specialty_create",
    ),
    path(
        "specialties/<int:specialty_id>/update/",
        views.SpecialtyUpdateView.as_view(),
        name="specialty_update",
    ),
    path(
        "specialties/<int:specialty_id>/delete/",
        views.SpecialtyDeleteView.as_view(),
        name="specialty_delete",
    ),
]
