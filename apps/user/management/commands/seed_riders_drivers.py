from django.core.management.base import BaseCommand
from faker import Faker
from apps.user.models import User, UserType

class Command(BaseCommand):
    help = 'Seed 50 riders and 50 drivers'

    def handle(self, *args, **kwargs):
        fake = Faker()

        rider_type, _ = UserType.objects.get_or_create(name='Rider')
        driver_type, _ = UserType.objects.get_or_create(name='Driver')

        self.stdout.write(self.style.WARNING("Seeding 50 Riders..."))
        for _ in range(50):
            user = User.objects.create(
                email=fake.unique.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                phone_number=fake.phone_number()[:11],
                user_type=rider_type,
                is_active=True
            )
            user.set_password("Test123@!")
            user.save()

        self.stdout.write(self.style.WARNING("Seeding 50 Drivers..."))
        for _ in range(50):
            user = User.objects.create(
                email=fake.unique.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                phone_number=fake.phone_number()[:11],
                user_type=driver_type,
                is_active=True
            )
            user.set_password("Test123@!")
            user.save()

        self.stdout.write(self.style.SUCCESS("✅ Successfully seeded 50 Riders and 50 Drivers."))
