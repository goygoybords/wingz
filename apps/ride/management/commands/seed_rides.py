from django.core.management.base import BaseCommand
from django.utils import timezone
from random import choice, uniform
from datetime import timedelta

from apps.ride.models import Ride, RideEvent
from apps.user.models import User

class Command(BaseCommand):
    help = 'Seed 1000 rides across the last 5 days'

    def handle(self, *args, **options):
        riders = User.objects.filter(user_type__name='Rider')
        drivers = User.objects.filter(user_type__name='Driver')

        if riders.count() < 50 or drivers.count() < 50:
            self.stdout.write(self.style.ERROR("❌ You need at least 50 riders and 50 drivers."))
            return

        total = 0
        for day_offset in [4, 3, 2, 1, 0]:
            group_time = timezone.now() - timedelta(days=day_offset)
            for _ in range(200):
                rider = choice(riders)
                driver = choice(drivers)
                pickup_time = group_time - timedelta(minutes=choice(range(10, 60)))

                ride = Ride.objects.create(
                    status=choice(['pickup', 'en-route', 'dropoff']),
                    id_rider=rider,
                    id_driver=driver,
                    pickup_latitude=uniform(14.55, 14.70),
                    pickup_longitude=uniform(120.90, 121.05),
                    dropoff_latitude=uniform(14.55, 14.70),
                    dropoff_longitude=uniform(120.90, 121.05),
                    pickup_time=pickup_time
                )

                RideEvent.objects.create(
                    id_ride=ride,
                    description='Status changed to pickup',
                    created_at=pickup_time
                )
                RideEvent.objects.create(
                    id_ride=ride,
                    description='Status changed to dropoff',
                    created_at=pickup_time + timedelta(minutes=choice(range(10, 90)))
                )
                total += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Seeded {total} rides across 5 days"))
