from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "user_type",
        "phone_number",
        "wallet_balance",
        "is_active",
        "created_at",
    )
    list_filter = ("user_type", "is_active", "is_staff", "created_at")
    search_fields = ("username", "email", "first_name", "last_name", "phone_number")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "email", "phone_number")},
        ),
        ("Account Type", {"fields": ("user_type",)}),
        ("Wallet", {"fields": ("wallet_balance",)}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            "Important dates",
            {"fields": ("last_login", "date_joined", "created_at", "updated_at")},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "user_type",
                    "phone_number",
                ),
            },
        ),
    )

    readonly_fields = ("created_at", "updated_at", "date_joined", "last_login")
