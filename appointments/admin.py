from appointments.models import TimeSlot
from django.contrib import admin
from .models import Appointment, TimeSlot

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'time_slot_info', 'status')
    list_filter = ('status', 'doctor', 'patient')
    search_fields = ('doctor__user__username', 'patient__username')

@admin.action(description="Mark selected slots as available")
def make_available(modeladmin, request, queryset):
    queryset.update(is_available=True)


@admin.action(description="Mark selected slots as unavailable")
def make_unavailable(modeladmin, request, queryset):
    queryset.update(is_available=False)


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ("doctor", "date", "start_time", "end_time", "is_available", "created_at")
    list_filter = ("doctor", "date", "is_available")
    search_fields = ("doctor__user__first_name", "doctor__user__last_name", "doctor__license_number")
    actions = [make_available, make_unavailable]

    def time_slot_info(self, obj):
        return str(obj.time_slot)
    time_slot_info.short_description = 'Time Slot'
