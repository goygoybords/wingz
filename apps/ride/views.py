from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import FloatField, Prefetch
from django.db.models.expressions import RawSQL
from django.utils import timezone
from datetime import timedelta

from apps.ride.models import Ride, RideEvent
from apps.ride.serializers import RideSerializer
from apps.ride.filters import RideFilter
from apps.user.permissions import IsAdminRole


class RideViewSet(viewsets.ModelViewSet):
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = RideFilter
    ordering = ['pickup_time']

    # Static fields always available for ordering.
    # distance_to_pickup is conditionally added in get_queryset —
    # we declare it here so OrderingFilter accepts it as a valid field.
    ordering_fields = ['pickup_time', 'distance_to_pickup']

    def _get_validated_coords(self):
        """
        Extracts and validates lat/lng from query params.
        Returns (lat, lng) as floats, or (None, None) if not provided.
        Raises ValidationError on malformed input.
        """
        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')

        if not lat and not lng:
            return None, None

        # Treat partial input (only lat OR lng) as a client error
        if bool(lat) ^ bool(lng):
            raise ValidationError({
                "detail": "Both 'lat' and 'lng' must be provided together."
            })

        try:
            lat = float(lat)
            lng = float(lng)
        except (TypeError, ValueError):
            raise ValidationError({
                "detail": "'lat' and 'lng' must be valid floating point numbers."
            })

        if not (-90 <= lat <= 90):
            raise ValidationError({"lat": "Latitude must be between -90 and 90."})

        if not (-180 <= lng <= 180):
            raise ValidationError({"lng": "Longitude must be between -180 and 180."})

        return lat, lng

    def get_queryset(self):
        """
        Builds the Ride queryset with:
        - select_related for rider/driver (prevents N+1)
        - Prefetch for last-24h RideEvents only (performance-safe on large tables)
        - Optional Haversine distance annotation when lat/lng are provided
        """
        lat, lng = self._get_validated_coords()

        yesterday = timezone.now() - timedelta(days=1)
        recent_events = RideEvent.objects.filter(created_at__gte=yesterday)

        queryset = (
            Ride.objects
            .select_related('id_rider', 'id_driver')
            .prefetch_related(
                Prefetch(
                    'ride_events',
                    queryset=recent_events,
                    to_attr='todays_events_cache'
                )
            )
        )

        if lat is not None and lng is not None:
            # Haversine formula — calculates great-circle distance in km.
            # RawSQL is used intentionally: Django ORM has no native trig
            # support portable across SQLite/PostgreSQL for this formula.
            # Params are passed as SQL params (not string-formatted) to
            # prevent injection.
            haversine_sql = """
                6371 * acos(
                    LEAST(1.0,
                        cos(radians(%s)) * cos(radians(pickup_latitude)) *
                        cos(radians(pickup_longitude) - radians(%s)) +
                        sin(radians(%s)) * sin(radians(pickup_latitude))
                    )
                )
            """
            queryset = queryset.annotate(
                distance_to_pickup=RawSQL(
                    haversine_sql,
                    params=[lat, lng, lat],
                    output_field=FloatField()
                )
            )

        return queryset

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({"message": "Ride created successfully.", "data": response.data}, status=response.status_code)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({"message": "Ride updated successfully.", "data": response.data}, status=response.status_code)

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return Response({"message": "Ride partially updated successfully.", "data": response.data}, status=response.status_code)

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return Response({"message": "Ride deleted successfully."}, status=response.status_code)
