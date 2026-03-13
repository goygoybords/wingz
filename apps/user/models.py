from django.db import models

class UserType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, unique=True)  # e.g., "Admin", "Rider", "Driver"

    def __str__(self):
        return self.name

class User(models.Model):
    id_user = models.AutoField(primary_key=True)
    user_type = models.ForeignKey(UserType, on_delete=models.PROTECT)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"