from django.contrib import admin
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib import messages
from .models import Doctor, Specialty
from .forms import DoctorCreationForm
from .services import DoctorService


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    form = DoctorCreationForm

    list_display = [
        "get_full_name",
        "specialty",
        "license_number",
        "experience_years",
        "consultation_fee",
        "is_active",
        "created_at",
    ]
    list_filter = [
        "specialty",
        "is_active",
        "experience_years",
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__email",
        "user__phone_number",
        "license_number",
        "bio",
    ]
    readonly_fields = ["created_at", "updated_at", "average_rating", "total_reviews"]

    fieldsets = (
        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "username",
                    "phone_number",
                )
            },
        ),
        (
            "Account Information",
            {"fields": ("wallet_balance",)},
        ),
        (
            "Professional Information",
            {"fields": ("specialty", "license_number", "experience_years", "bio")},
        ),
        ("Financial Information", {"fields": ("consultation_fee",)}),
        (
            "Status & Statistics",
            {
                "fields": ("is_active", "average_rating", "total_reviews"),
                "classes": ("collapse",),
            },
        ),
        (
            "System Information",
            {
                "fields": ("created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_full_name(self, obj):
        """Display full name in list view."""
        return f"{obj.user.first_name} {obj.user.last_name}"

    get_full_name.short_description = "Full Name"
    get_full_name.admin_order_field = "user__first_name"

    def has_add_permission(self, request):
        """Allow superusers or admin type users to create doctors."""
        return DoctorService.can_user_manage_doctors(request.user)

    def has_change_permission(self, request, obj=None):
        """Allow superusers or admin type users to edit doctors."""
        return DoctorService.can_user_manage_doctors(request.user)

    def has_delete_permission(self, request, obj=None):
        """Allow superusers or admin type users to delete doctors."""
        return DoctorService.can_user_manage_doctors(request.user)

    def save_model(self, request, obj, form, change):
        """Override save_model to pass created_by to form."""
        if not change:  # Only for new objects
            # Pass the request user to the form's save method
            form.save(commit=True, created_by=request.user)
        else:
            super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return (
            super()
            .get_queryset(request)
            .select_related("user", "specialty", "created_by")
        )


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ["name", "doctor_count", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at", "doctor_count"]
    ordering = ["name"]

    fieldsets = (
        (
            "Specialty Information",
            {
                "fields": ("name", "description"),
                "description": "Enter the specialty name and a detailed description.",
            },
        ),
        (
            "Statistics",
            {
                "fields": ("doctor_count",),
                "classes": ("collapse",),
                "description": "Number of doctors in this specialty.",
            },
        ),
        (
            "System Information",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def doctor_count(self, obj):
        """Display the number of doctors in this specialty."""
        if obj.pk:
            return obj.doctor_set.count()
        return 0

    doctor_count.short_description = "Number of Doctors"
    doctor_count.admin_order_field = "doctor_set__count"

    def get_queryset(self, request):
        """Optimize queryset with annotations."""
        from django.db.models import Count

        return super().get_queryset(request).annotate(doctor_count=Count("doctor"))

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion if specialty has doctors."""
        if obj and obj.doctor_set.exists():
            return False
        return super().has_delete_permission(request, obj)

    def delete_model(self, request, obj):
        """Custom delete with validation."""
        if obj.doctor_set.exists():
            from django.contrib import messages

            messages.error(
                request,
                f"Cannot delete '{obj.name}' because it has {obj.doctor_set.count()} doctor(s) assigned to it.",
            )
            return
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """Custom bulk delete with validation."""
        from django.contrib import messages

        deleted_count = 0
        for obj in queryset:
            if not obj.doctor_set.exists():
                obj.delete()
                deleted_count += 1
            else:
                messages.warning(
                    request,
                    f"Cannot delete '{obj.name}' because it has {obj.doctor_set.count()} doctor(s) assigned to it.",
                )

        if deleted_count > 0:
            messages.success(
                request, f"Successfully deleted {deleted_count} specialty(ies)."
            )
