from django.urls import path
from . import views

app_name = "doctors"

urlpatterns = [
    # Placeholder URLs - to be implemented
    path("", views.list_view, name="list"),
    path("<int:doctor_id>/", views.detail_view, name="detail"),
]
