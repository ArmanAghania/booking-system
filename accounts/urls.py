from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("register/", views.RegistrationView.as_view(), name="register"),
    path("logout/", views.custom_logout_view, name="logout"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("verify-email/", views.OTPVerificationView.as_view(), name="otp_verification"),
    path("resend-otp/", views.resend_otp_view, name="resend_otp"),
    path(
        "password-reset/",
        views.PasswordResetRequestView.as_view(),
        name="password_reset_request",
    ),
    path(
        "password-reset/<int:user_id>/",
        views.PasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password-reset/<int:user_id>/resend/",
        views.resend_password_reset_otp,
        name="resend_password_reset_otp",
    ),
    path("google-login/", views.GoogleLoginView.as_view(), name="google_login"),
    path(
        "mock-google-login/",
        views.MockGoogleLoginView.as_view(),
        name="mock_google_login",
    ),
]
