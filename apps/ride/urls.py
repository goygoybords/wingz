from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.ride import views

router = DefaultRouter()
router.register(r'rides', views.RideViewSet, basename='ride')

urlpatterns = [
    path('', include(router.urls)),
]
