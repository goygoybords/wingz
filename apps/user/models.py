from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractUser

class UserType(models.Model):
    ADMIN = "Admin"
    RIDER = "Rider"
    DRIVER = "Driver"

    USER_TYPE_CHOICES = [
        (ADMIN, "Admin"),
        (RIDER, "Rider"),
        (DRIVER, "Driver"),
    ]

    name = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, unique=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    username = None
    user_type = models.ForeignKey(UserType, on_delete=models.PROTECT)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(unique=True)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'user_type']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"