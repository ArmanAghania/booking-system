from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


class EmailVerificationRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect("accounts:login")

        if not request.user.is_verified:
            messages.warning(
                request, "Please verify your email address to access this page."
            )
            return redirect("accounts:otp_verification")

        return super().dispatch(request, *args, **kwargs)
