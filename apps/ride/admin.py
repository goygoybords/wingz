from django.contrib import admin
from .models import Ride, RideEvent

# Registering models for Django admin interface.
# Best practice during development to easily view, edit, and verify model data.

admin.site.register(Ride)
admin.site.register(RideEvent)