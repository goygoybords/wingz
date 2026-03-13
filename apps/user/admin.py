from django.contrib import admin
from .models import User, UserType


# Registering models for visibility in Django admin.
# Useful for managing users and roles without needing API or direct DB access.
admin.site.register(User)
admin.site.register(UserType)
