from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth import get_user_model
from .forms import (
    CustomLoginForm,
    UserRegistrationForm,
    OTPVerificationForm,
    PasswordResetRequestForm,
    PasswordResetForm,
)
from .services import OTPService

User = get_user_model()


class CustomLoginView(LoginView):

    form_class = CustomLoginForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        next_url = self.request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts=settings.ALLOWED_HOSTS
        ):
            return next_url
        return get_redirect_url(self.request)

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)

        if not form.cleaned_data.get("remember_me"):
            self.request.session.set_expiry(0)
        else:
            self.request.session.set_expiry(1209600)

        messages.success(
            self.request, f"Welcome back, {user.first_name or user.username}!"
        )
        return super().form_valid(form)


def custom_logout_view(request):
    if request.user.is_authenticated:
        messages.info(request, "You have been logged out successfully.")
        logout(request)
    return redirect("core:home")


class CustomLogoutView(LogoutView):

    next_page = reverse_lazy("core:home")
    http_method_names = ["get", "post"]

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "You have been logged out successfully.")
        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, TemplateView):

    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


def get_redirect_url(request):
    if not request.user.is_authenticated:
        return reverse("core:home")

    if request.user.user_type == "admin":
        return reverse("admin:index")
    elif request.user.user_type == "doctor":
        return reverse("core:home")
    else:  # patient
        return reverse("core:home")


class RegistrationView(TemplateView):

    template_name = "accounts/register.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(get_redirect_url(request))

        form = UserRegistrationForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(get_redirect_url(request))

        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()

                try:
                    OTPService.send_verification_otp(user)
                    login(
                        request,
                        user,
                        backend="django.contrib.auth.backends.ModelBackend",
                    )
                    messages.success(
                        request,
                        f"Account created successfully! Please check your email for verification code.",
                    )
                    return redirect("accounts:otp_verification")
                except Exception as e:
                    messages.warning(
                        request,
                        f"Account created but failed to send verification email. Please contact support.",
                    )
                    return redirect("accounts:login")
            except Exception as e:
                messages.error(request, f"Error creating account: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")

        return render(request, self.template_name, {"form": form})


class OTPVerificationView(TemplateView):

    template_name = "accounts/otp_verification.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to verify your email.")
            return redirect("accounts:login")

        if request.user.is_verified:
            messages.info(request, "Your email is already verified.")
            return redirect("core:home")

        form = OTPVerificationForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to verify your email.")
            return redirect("accounts:login")

        if request.user.is_verified:
            messages.info(request, "Your email is already verified.")
            return redirect("core:home")

        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data["otp_code"]
            success, message = OTPService.verify_otp(request.user, otp_code)

            if success:
                messages.success(request, message)
                return redirect("core:home")
            else:
                messages.error(request, message)
        else:
            messages.error(request, "Please correct the errors below.")

        return render(request, self.template_name, {"form": form})


def resend_otp_view(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to resend OTP.")
        return redirect("accounts:login")

    if request.user.is_verified:
        messages.info(request, "Your email is already verified.")
        return redirect("core:home")

    if request.method == "POST":
        try:
            OTPService.resend_otp(request.user)
            messages.success(request, "New verification code sent to your email.")
        except Exception as e:
            messages.error(request, f"Failed to send verification code: {str(e)}")

    return redirect("accounts:otp_verification")


class PasswordResetRequestView(TemplateView):

    template_name = "accounts/password_reset_request.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("core:home")

        form = PasswordResetRequestForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("core:home")

        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email=email)

                try:
                    OTPService.send_password_reset_otp(user)
                    messages.success(
                        request,
                        f"Password reset code sent to {email}. Please check your email.",
                    )
                    return redirect("accounts:password_reset", user_id=user.id)
                except Exception as e:
                    messages.error(
                        request,
                        "Failed to send password reset code. Please try again later.",
                    )
            except User.DoesNotExist:
                messages.success(
                    request,
                    "If an account with this email exists, a password reset code has been sent.",
                )
                return redirect("accounts:password_reset_request")
        else:
            messages.error(request, "Please correct the errors below.")

        return render(request, self.template_name, {"form": form})


class PasswordResetView(TemplateView):

    template_name = "accounts/password_reset.html"

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        if not user_id:
            messages.error(request, "Invalid password reset link.")
            return redirect("accounts:password_reset_request")

        try:
            user = User.objects.get(id=user_id)
            if not user.is_verified:
                messages.error(request, "Account is not verified.")
                return redirect("accounts:password_reset_request")
        except User.DoesNotExist:
            messages.error(request, "Invalid password reset link.")
            return redirect("accounts:password_reset_request")

        form = PasswordResetForm()
        return render(request, self.template_name, {"form": form, "user": user})

    def post(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        if not user_id:
            messages.error(request, "Invalid password reset link.")
            return redirect("accounts:password_reset_request")

        try:
            user = User.objects.get(id=user_id)
            if not user.is_verified:
                messages.error(request, "Account is not verified.")
                return redirect("accounts:password_reset_request")
        except User.DoesNotExist:
            messages.error(request, "Invalid password reset link.")
            return redirect("accounts:password_reset_request")

        form = PasswordResetForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data["otp_code"]
            new_password = form.cleaned_data["new_password1"]

            success, message = OTPService.verify_password_reset_otp(user, otp_code)

            if success:
                user.set_password(new_password)
                user.save()

                messages.success(
                    request,
                    "Password reset successfully! You can now log in with your new password.",
                )
                return redirect("accounts:login")
            else:
                messages.error(request, message)
        else:
            messages.error(request, "Please correct the errors below.")

        return render(request, self.template_name, {"form": form, "user": user})


def resend_password_reset_otp(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        if not user.is_verified:
            messages.error(request, "Account is not verified.")
            return redirect("accounts:password_reset_request")

        try:
            OTPService.send_password_reset_otp(user)
            success, message = True, "New password reset code sent successfully."
        except Exception as e:
            success, message = False, "Failed to send password reset code."

        if success:
            messages.success(request, "New password reset code sent successfully.")
        else:
            messages.error(request, message)

        return redirect("accounts:password_reset", user_id=user_id)

    except User.DoesNotExist:
        messages.error(request, "Invalid user.")
        return redirect("accounts:password_reset_request")


class GoogleLoginView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return reverse("google_login")


class MockGoogleLoginView(TemplateView):

    template_name = "accounts/mock_google_login.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        # Create a mock user for testing
        email = request.POST.get("email", "test@example.com")
        first_name = request.POST.get("first_name", "Test")
        last_name = request.POST.get("last_name", "User")

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email,
                "first_name": first_name,
                "last_name": last_name,
                "user_type": "patient",
                "is_verified": True,
                "profile_picture_url": "https://via.placeholder.com/150/3b82f6/ffffff?text=G",
            },
        )

        if created:
            user.set_unusable_password()
            user.save()
            messages.success(
                request, f"Welcome, {user.first_name}! Your account has been created."
            )
        else:
            messages.success(request, f"Welcome back, {user.first_name}!")

        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect("core:home")
