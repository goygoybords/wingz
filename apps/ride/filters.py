import django_filters
from apps.ride.models import Ride

class RideFilter(django_filters.FilterSet):
    rider_email = django_filters.CharFilter(
        field_name='id_rider__email', lookup_expr='icontains', label='Rider Email'
    )
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')

    class Meta:
        model = Ride
        fields = ['status', 'rider_email']
