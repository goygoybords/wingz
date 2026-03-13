from django.urls import path
from apps.user import views

urlpatterns = [
    path('', views.LoginPage.as_view(), name='login'),
]
