from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
    # Placeholder URLs - to be implemented
    path("", views.list_view, name="list"),
    path("my-appointments/", views.my_appointments_view, name="my_appointments"),
    path("book/<int:doctor_id>/", views.book_view, name="book"),
]
