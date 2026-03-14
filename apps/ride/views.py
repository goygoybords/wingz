from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter
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
    ordering_fields = ['pickup_time', 'distance_to_pickup']
    ordering = ['pickup_time']

    def get_queryset(self):
        """
        Dynamically builds the Ride queryset with related users, ride events (24h only),
        and optional distance-to-pickup annotation for sorting.
        """
        queryset = Ride.objects.select_related('id_rider', 'id_driver')
       
        yesterday = timezone.now() - timedelta(days=1)
        recent_events = RideEvent.objects.filter(created_at__gte=yesterday)

        queryset = queryset.prefetch_related(
            Prefetch('ride_events', queryset=recent_events, to_attr='todays_events_cache')
        )

        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')

        if lat and lng:
            raw_sql = """
                6371 * acos(
                    cos(radians(%s)) * cos(radians(pickup_latitude)) *
                    cos(radians(pickup_longitude) - radians(%s)) +
                    sin(radians(%s)) * sin(radians(pickup_latitude))
                )
            """
            params = [lat, lng, lat]
            queryset = queryset.annotate(
                distance_to_pickup=RawSQL(raw_sql, params, output_field=FloatField())
            )

        return queryset

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({"message": "Ride created successfully."}, status=response.status_code)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({"message": "Ride updated successfully."}, status=response.status_code)

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return Response({"message": "Ride partially updated successfully."}, status=response.status_code)

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return Response({"message": "Ride deleted successfully."}, status=response.status_code)
