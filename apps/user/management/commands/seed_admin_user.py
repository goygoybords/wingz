from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.user.models import UserType

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed an initial Admin user (Kevin Sean)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Seeding Admin user..."))

        try:
            admin_type = UserType.objects.get(name="Admin")
        except UserType.DoesNotExist:
            self.stdout.write(self.style.ERROR("UserType 'Admin' not found. Run `seed_usertypes` first."))
            return

        user, created = User.objects.get_or_create(
            email="kevin@test.com",
            defaults={
                "first_name": "Kevin",
                "last_name": "Sean",
                "phone_number": "09123456789",
                "user_type": admin_type,
                "is_staff": True,
                "is_superuser": True,
            }
        )

        if created:
            user.set_password("Admin123@!")
            user.save()
            self.stdout.write(self.style.SUCCESS(
                f"Admin user '{user.email}' created with password 'Admin123@!'."
            ))
        else:
            self.stdout.write(self.style.WARNING(f"Admin user '{user.email}' already exists."))
