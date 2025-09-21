from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import User, OTP


class OTPService:

    @staticmethod
    def send_verification_otp(user):
        otp = OTP.generate_otp(user, purpose="email_verification")

        subject = "Verify Your Email Address - Booking System"

        html_message = render_to_string(
            "accounts/emails/verification_email.html",
            {
                "user": user,
                "otp_code": otp.code,
                "expiry_minutes": settings.OTP_EXPIRY_MINUTES,
            },
        )

        plain_message = f"""
        Hello {user.first_name},
        
        Welcome to Booking System! Please verify your email address by entering the following code:
        
        Verification Code: {otp.code}
        
        This code will expire in {settings.OTP_EXPIRY_MINUTES} minutes.
        
        If you didn't create an account with us, please ignore this email.
        
        Best regards,
        Booking System Team
        """

        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return otp

    @staticmethod
    def send_password_reset_otp(user):
        otp = OTP.generate_otp(user, purpose="password_reset")

        subject = "Password Reset Request - Booking System"

        html_message = render_to_string(
            "accounts/emails/password_reset_email.html",
            {
                "user": user,
                "otp_code": otp.code,
                "expiry_minutes": settings.OTP_EXPIRY_MINUTES,
            },
        )

        plain_message = f"""
        Hello {user.first_name},
        
        You requested to reset your password. Please use the following code to reset your password:
        
        Reset Code: {otp.code}
        
        This code will expire in {settings.OTP_EXPIRY_MINUTES} minutes.
        
        If you didn't request a password reset, please ignore this email.
        
        Best regards,
        Booking System Team
        """

        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return otp

    @staticmethod
    def verify_otp(user, code, purpose="email_verification"):
        try:
            otp = OTP.objects.get(user=user, code=code, purpose=purpose, is_used=False)

            if not otp.is_valid():
                return False, "OTP has expired"

            otp.mark_as_used()

            if purpose == "email_verification":
                user.is_verified = True
                user.save()
                return True, "Email verified successfully"

            return True, "OTP verified successfully"

        except OTP.DoesNotExist:
            return False, "Invalid OTP code"

    @staticmethod
    def verify_password_reset_otp(user, code):
        return OTPService.verify_otp(user, code, purpose="password_reset")

    @staticmethod
    def resend_otp(user, purpose="email_verification"):
        if purpose == "email_verification":
            return OTPService.send_verification_otp(user)
        elif purpose == "password_reset":
            return OTPService.send_password_reset_otp(user)
        else:
            raise ValueError("Invalid OTP purpose")
