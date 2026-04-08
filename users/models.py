from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    residence_address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
