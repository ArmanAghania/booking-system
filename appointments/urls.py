# appointments/urls.py

from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
    path("", views.appointment_list, name="appointment_list"),
    path("my-appointments/", views.my_appointments_view, name="my_appointments"),
    path("book/<int:doctor_id>/", views.book_view, name="book"),
    path(
        "calendar-book/<int:doctor_id>/", views.calendar_book_view, name="calendar_book"
    ),
    path("reserve/<int:slot_id>/", views.reserve_slot_view, name="reserve_slot"),
    path(
        "confirmation/<int:appointment_id>/",
        views.booking_confirmation_view,
        name="booking_confirmation",
    ),
    path(
        "cancel/<int:appointment_id>/",
        views.cancel_appointment_view,
        name="cancel_appointment",
    ),
    path(
        "mark-completed/<int:appointment_id>/",
        views.mark_completed,
        name="mark_completed",
    ),
    path(
        "admin-add-time-slot/<int:doctor_id>/",
        views.admin_add_time_slot_view,
        name="admin_add_time_slot",
    ),
    path(
        "time-slot-management/<int:doctor_id>/",
        views.time_slot_management_view,
        name="time_slot_management",
    ),
    path(
        "bulk-create-slots/<int:doctor_id>/",
        views.bulk_create_time_slots_view,
        name="bulk_create_time_slots",
    ),
    path(
        "delete-time-slot/<int:time_slot_id>/",
        views.delete_time_slot_view,
        name="delete_time_slot",
    ),
    path(
        "delete-day-slots/<int:doctor_id>/",
        views.delete_day_slots_view,
        name="delete_day_slots",
    ),
]
