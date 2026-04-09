from django.contrib.auth.models import AbstractUser, Group
from django.db import models


class User(AbstractUser):
    residence_address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)

    def assign_role(self, role_name):
        group = Group.objects.get(name=role_name)
        self.groups.clear()
        self.groups.add(group)

    def is_admin(self):
        return self.groups.filter(name='admin').exists()

    def is_advisor(self):
        return self.groups.filter(name='advisor').exists()

    def is_professor(self):
        return self.groups.filter(name='professor').exists()

    def is_student(self):
        return self.groups.filter(name='student').exists()

    def is_beneficiary(self):
        return self.groups.filter(name='beneficiary').exists()
