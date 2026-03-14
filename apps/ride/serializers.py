from rest_framework import serializers
from apps.ride.models import Ride, RideEvent
from apps.user.models import User


class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']


class RideEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideEvent
        fields = ['id_ride_event', 'description', 'created_at']


class RideSerializer(serializers.ModelSerializer):
    id_rider = UserDisplaySerializer(read_only=True)
    id_driver = UserDisplaySerializer(read_only=True)

    id_rider_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(user_type__id=2),
        source='id_rider',
        write_only=True
    )
    id_driver_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(user_type__id=3),
        source='id_driver',
        write_only=True
    )

    ride_events = RideEventSerializer(many=True, write_only=True)

    class Meta:
        model = Ride
        fields = [
            'id_ride',
            'status',
            'pickup_latitude',
            'pickup_longitude',
            'dropoff_latitude',
            'dropoff_longitude',
            'pickup_time',
            'id_rider',
            'id_driver',
            'id_rider_id',
            'id_driver_id',
            'ride_events'
        ]
        read_only_fields = ['id_ride', 'id_rider', 'id_driver']

    def create(self, validated_data):
        ride_events_data = validated_data.pop('ride_events', [])
        ride = Ride.objects.create(**validated_data)

        for event_data in ride_events_data:
            RideEvent.objects.create(id_ride=ride, **event_data)

        return ride

