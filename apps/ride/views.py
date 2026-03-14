from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.ride.models import Ride
from apps.ride.serializers import RideSerializer
from apps.ride.filters import RideFilter
from apps.user.permissions import IsAdminRole


class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.select_related('id_rider', 'id_driver').prefetch_related('ride_events').all()
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RideFilter

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({"message": "Ride created successfully."}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({"message": "Ride updated successfully."}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response({"message": "Ride partially updated successfully."}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"message": "Ride deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
