from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


User = get_user_model()


class Command(BaseCommand):

    help = "Create the initial platform administrator"

    def handle(self, *args, **options):

        email = input("Enter platform admin email: ").strip().lower()

        if not email:
            self.stdout.write(
                self.style.ERROR("Email is required.")
            )
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR("This email already exists.")
            )
            return

        password = input("Enter password: ")

        if len(password) < 12:
            self.stdout.write(
                self.style.ERROR(
                    "Password must contain at least 12 characters."
                )
            )
            return

        user = User.objects.create_superuser(
            email=email,
            password=password,
            is_platform_admin=True
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Platform administrator created: {user.email}"
            )
        )