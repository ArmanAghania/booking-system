# reviews/urls.py

from django.urls import path
from . import views

app_name = 'reviews' # Optional but good practice

urlpatterns = [
    path('submit/<int:appointment_id>/', views.submit_review, name='submit_review'),
]