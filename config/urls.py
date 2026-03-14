"""
    URL configuration for wingz-exam project.
"""
from django.urls import path, include
from django.conf import settings
from config.views import home

urlpatterns = [
    path('', home),  # 👈 set root route to home
    path('api/user/', include('apps.user.urls')),
    path('api/ride/', include('apps.ride.urls')),
]

urlpatterns += [path('api-auth/', include('rest_framework.urls'))]

if settings.DEBUG:
    from django.contrib import admin
    urlpatterns.append(path('admin/', admin.site.urls))

    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]