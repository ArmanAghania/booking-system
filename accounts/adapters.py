from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

User = get_user_model()


class CustomAccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, sociallogin, form=None):
        """Save user from social login with custom fields."""
        user = super().save_user(request, sociallogin, form)

        user.user_type = "patient"
        user.is_verified = True
        user.save()

        return user


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)

        extra_data = sociallogin.account.extra_data

        user.user_type = "patient"
        user.is_verified = True

        if "picture" in extra_data:
            user.profile_picture_url = extra_data.get("picture")

        if "given_name" in extra_data:
            user.first_name = extra_data.get("given_name", "")
        if "family_name" in extra_data:
            user.last_name = extra_data.get("family_name", "")

        return user

    def pre_social_login(self, request, sociallogin):
        if request.user.is_authenticated:
            sociallogin.connect(request, request.user)
            messages.success(
                request,
                f"Your Google account has been successfully linked to your profile.",
            )
            return redirect("accounts:profile")

    def is_auto_signup_allowed(self, request, sociallogin):
        return True

    def get_connect_redirect_url(self, request, socialaccount):
        return reverse("accounts:profile")

    def get_signup_redirect_url(self, request, socialaccount):
        return reverse("core:home")
