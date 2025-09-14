# appointments/admin.py

from django.contrib import admin
from .models import Appointment, TimeSlot

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'start_time', 'is_available')
    list_filter = ('doctor', 'date', 'is_available')
    search_fields = ('doctor__user__username',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'time_slot_info', 'status')
    list_filter = ('status', 'doctor', 'patient')
    search_fields = ('doctor__user__username', 'patient__username')

    def time_slot_info(self, obj):
        return str(obj.time_slot)
    time_slot_info.short_description = 'Time Slot'