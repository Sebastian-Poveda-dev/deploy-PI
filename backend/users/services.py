from django.contrib.auth.models import Group
from django.conf import settings
from django.apps import apps

User = apps.get_model(settings.AUTH_USER_MODEL)


def assign_role(user, role_name):
    """Assign a single role to a user, replacing any existing roles."""
    group = Group.objects.get(name=role_name)
    user.groups.clear()
    user.groups.add(group)


def register_beneficiary(username, password, residence_address='', phone_number=''):
    """Create a new user and automatically assign the beneficiary role."""
    user = User.objects.create_user(
        username=username,
        password=password,
        residence_address=residence_address,
        phone_number=phone_number,
    )
    assign_role(user, 'beneficiary')
    return user


def admin_create_user(username, password, role, residence_address='', phone_number=''):
    """Create a user with a specific role (for admin-driven creation)."""
    user = User.objects.create_user(
        username=username,
        password=password,
        residence_address=residence_address,
        phone_number=phone_number,
    )
    assign_role(user, role)
    return user
