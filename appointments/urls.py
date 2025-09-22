# appointments/urls.py

from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
    path("", views.appointment_list, name="appointment_list"),
    path("my-appointments/", views.my_appointments_view, name="my_appointments"),
    path("book/<int:doctor_id>/", views.book_view, name="book"),
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
        "pay/<int:appointment_id>/",
        views.pay_appointment_view,
        name="pay_appointment",
    ),
    path("admin-add-time-slot/<int:doctor_id>/", views.admin_add_time_slot_view, name="admin_add_time_slot"),

]