"""
URL configuration for booking_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.conf import settings
from django.conf.urls.static import static


def admin_logout_redirect(request):
    """Redirect Django admin logout to home page."""
    # Log out the user
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out successfully.")

    return redirect("core:home")


urlpatterns = [
    # Override admin logout before including admin URLs
    path("admin/logout/", admin_logout_redirect, name="admin_logout_redirect"),
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("allauth.urls")),
    path("doctors/", include("doctors.urls")),
    path("appointments/", include("appointments.urls")),
    path("payments/", include("payments.urls")),
    path("reviews/", include("reviews.urls")),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
