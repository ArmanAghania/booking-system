from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.google.provider import GoogleProvider


class Command(BaseCommand):
    help = "Set up Google OAuth provider for development"

    def add_arguments(self, parser):
        parser.add_argument(
            "--client-id",
            type=str,
            help="Google OAuth Client ID",
            default="your-google-client-id",
        )
        parser.add_argument(
            "--client-secret",
            type=str,
            help="Google OAuth Client Secret",
            default="your-google-client-secret",
        )

    def handle(self, *args, **options):
        # Get or create the site
        site, created = Site.objects.get_or_create(
            id=1,
            defaults={
                "domain": "localhost:8001",
                "name": "Booking System",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created site: {site.domain}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Using existing site: {site.domain}"))

        # Create or update Google OAuth app
        app, created = SocialApp.objects.get_or_create(
            provider=GoogleProvider.id,
            defaults={
                "name": "Google",
                "client_id": options["client_id"],
                "secret": options["client_secret"],
            },
        )

        if not created:
            app.client_id = options["client_id"]
            app.secret = options["client_secret"]
            app.save()

        # Add the site to the app
        app.sites.add(site)

        self.stdout.write(
            self.style.SUCCESS(
                f"Google OAuth app {'created' if created else 'updated'} successfully!"
            )
        )
        self.stdout.write(
            self.style.WARNING(
                "Remember to set up your Google OAuth credentials in the Google Cloud Console:"
            )
        )
        self.stdout.write("1. Go to https://console.cloud.google.com/")
        self.stdout.write("2. Create a new project or select existing one")
        self.stdout.write("3. Enable Google+ API")
        self.stdout.write("4. Create OAuth 2.0 credentials")
        self.stdout.write(
            "5. Add authorized redirect URI: http://localhost:8001/accounts/google/login/callback/"
        )
        self.stdout.write("6. Update the client ID and secret in this command")
