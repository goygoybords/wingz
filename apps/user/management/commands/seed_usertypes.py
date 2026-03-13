from django.core.management.base import BaseCommand
from apps.user.models import UserType

class Command(BaseCommand):
    help = 'Seed initial user types (roles): Admin, Rider, Driver'

    def handle(self, *args, **kwargs):
        roles = [
            {"id": 1, "name": "Admin"},
            {"id": 2, "name": "Rider"},
            {"id": 3, "name": "Driver"},
        ]

        self.stdout.write(self.style.WARNING("Seeding user types..."))

        for role in roles:
            obj, created = UserType.objects.get_or_create(id=role["id"], defaults={"name": role["name"]})
            if created:
                self.stdout.write(self.style.SUCCESS(f'UserType "{obj.name}" created.'))
            else:
                self.stdout.write(self.style.WARNING(f'UserType "{obj.name}" already exists.'))

        self.stdout.write(self.style.SUCCESS("Seeding of UserTypes completed."))
