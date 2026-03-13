"""
    URL configuration for wingz project.
"""
from django.urls import path, include
from django.conf import settings
from config.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/user/', include('apps.user.urls')), 
]

if settings.DEBUG:
    from django.contrib import admin
    urlpatterns.append(path('admin/', admin.site.urls))

    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]