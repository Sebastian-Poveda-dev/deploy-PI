from django.contrib.auth.models import Group
from django.conf import settings
from django.apps import apps

User = apps.get_model(settings.AUTH_USER_MODEL)

VALID_ROLES = {'admin', 'advisor', 'student', 'beneficiary'}


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


def admin_create_user(
    username,
    password,
    role,
    residence_address='',
    phone_number='',
    category_id=None,
):
    """Create a user with a specific role (for admin-driven creation)."""
    user = User.objects.create_user(
        username=username,
        password=password,
        residence_address=residence_address,
        phone_number=phone_number,
    )
    assign_role(user, role)
    if category_id is not None:
        user.category_id = category_id
        user.save(update_fields=['category_id'])
    return user


def list_users(requesting_user):
    """Return all users. Requires admin role."""
    role = requesting_user.groups.values_list('name', flat=True).first()
    if role != 'admin':
        raise PermissionError('Only admins can list users.')
    return User.objects.prefetch_related('groups').order_by('username')


BENEFICIARY_UPDATABLE_FIELDS = {'first_name', 'last_name', 'email', 'identification_number', 'residence_address', 'phone_number'}


def update_beneficiary_info(requesting_user, target_user, data):
    """Update contact/personal info of a beneficiary. Requires admin or advisor role."""
    role = requesting_user.groups.values_list('name', flat=True).first()
    if role not in {'admin', 'advisor'}:
        raise PermissionError('Solo admins y asesores pueden editar información de beneficiarios.')

    if not target_user.groups.filter(name='beneficiary').exists():
        raise ValueError('Solo se puede actualizar información de usuarios beneficiarios.')

    update_fields = []
    for field in BENEFICIARY_UPDATABLE_FIELDS:
        if field in data:
            setattr(target_user, field, data[field])
            update_fields.append(field)

    if update_fields:
        target_user.save(update_fields=update_fields)

    return target_user


def update_user(requesting_user, target_user, data):
    """
    Update role and/or is_active on a user. Requires admin role.
    Admins cannot modify their own account to prevent lockout.
    """
    role = requesting_user.groups.values_list('name', flat=True).first()
    if role != 'admin':
        raise PermissionError('Only admins can update users.')

    if requesting_user.pk == target_user.pk:
        raise PermissionError('Admins cannot modify their own account from this panel.')

    if 'role' in data:
        new_role = data['role']
        if new_role not in VALID_ROLES:
            raise ValueError(f"Invalid role '{new_role}'.")
        assign_role(target_user, new_role)

    if 'is_active' in data:
        target_user.is_active = data['is_active']
        target_user.save(update_fields=['is_active'])

    if 'category_id' in data:
        target_user.category_id = data['category_id']
        target_user.save(update_fields=['category_id'])

    return target_user
