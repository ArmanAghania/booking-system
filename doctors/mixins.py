from django.contrib.auth.mixins import UserPassesTestMixin


def is_admin_user(user):
    """Check if user is admin or superuser."""
    return user.is_authenticated and (
        user.is_superuser or getattr(user, "user_type", None) == "admin"
    )


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to require admin or superuser permissions."""

    def test_func(self):
        return is_admin_user(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to access this page.")
        return redirect("doctors:specialty_list")
