"""
    URL configuration for wingz-exam project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings



urlpatterns = [
    path('api/user/', include('apps.user.urls')),
    path('api/ride/', include('apps.ride.urls')),
]

if settings.DEBUG:
    urlpatterns.append(path('admin/', admin.site.urls))