# reviews/admin.py

from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'patient', 'doctor', 'rating', 'created_at')
    list_filter = ('doctor', 'rating')
    search_fields = ('doctor__user__username', 'patient__username', 'comment')