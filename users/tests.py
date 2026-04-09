from django.test import TestCase
from django.contrib.auth.models import Group
from django.conf import settings
from django.apps import apps
from django.urls import reverse

User = apps.get_model(settings.AUTH_USER_MODEL)


class UserCreationTest(TestCase):
    """Tests for basic user creation and custom fields."""

    def test_create_user_with_username_and_password(self):
        user = User.objects.create_user(username='testuser', password='pass1234')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('pass1234'))

    def test_registration_date_auto_generated(self):
        user = User.objects.create_user(username='user1', password='pass1234')
        self.assertIsNotNone(user.registration_date)

    def test_residence_address_field_exists(self):
        user = User.objects.create_user(
            username='user2',
            password='pass1234',
            residence_address='123 Main St',
        )
        self.assertEqual(user.residence_address, '123 Main St')

    def test_phone_number_field_exists(self):
        user = User.objects.create_user(
            username='user3',
            password='pass1234',
            phone_number='555-1234',
        )
        self.assertEqual(user.phone_number, '555-1234')

    def test_residence_address_defaults_to_empty(self):
        user = User.objects.create_user(username='user4', password='pass1234')
        self.assertEqual(user.residence_address, '')

    def test_phone_number_defaults_to_empty(self):
        user = User.objects.create_user(username='user5', password='pass1234')
        self.assertEqual(user.phone_number, '')


class RoleAssignmentTest(TestCase):
    """Tests for assigning Django Groups (roles) to users."""

    def setUp(self):
        self.user = User.objects.create_user(username='roleuser', password='pass1234')
        self.group = Group.objects.create(name='student')

    def test_assign_role_to_user(self):
        self.user.groups.add(self.group)
        self.assertIn(self.group, self.user.groups.all())

    def test_user_belongs_to_role(self):
        self.user.groups.add(self.group)
        self.assertTrue(self.user.groups.filter(name='student').exists())

    def test_user_not_in_role_by_default(self):
        self.assertFalse(self.user.groups.filter(name='student').exists())

    def test_user_can_have_multiple_roles(self):
        advisor = Group.objects.create(name='advisor')
        self.user.groups.add(self.group, advisor)
        self.assertEqual(self.user.groups.count(), 2)


class DefaultGroupsTest(TestCase):
    """Tests that the default roles are created via data migration."""

    def test_all_default_groups_exist(self):
        expected = ['admin', 'advisor', 'professor', 'student', 'beneficiary']
        for name in expected:
            self.assertTrue(
                Group.objects.filter(name=name).exists(),
                msg=f"Expected group '{name}' to exist",
            )

    def test_default_group_count(self):
        expected = ['admin', 'advisor', 'professor', 'student', 'beneficiary']
        existing = Group.objects.filter(name__in=expected).count()
        self.assertEqual(existing, len(expected))


class LoginAuthenticationTest(TestCase):
    """Tests for username/password authentication flow."""

    def setUp(self):
        self.login_url = reverse('users:login')
        self.username = 'authuser'
        self.password = 'StrongPass123'
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_successful_login_with_valid_credentials(self):
        response = self.client.post(
            self.login_url,
            data={'username': self.username, 'password': self.password},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['authenticated'], True)

    def test_login_fails_with_incorrect_password(self):
        response = self.client.post(
            self.login_url,
            data={'username': self.username, 'password': 'wrong-password'},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['authenticated'], False)

    def test_login_fails_with_non_existing_user(self):
        response = self.client.post(
            self.login_url,
            data={'username': 'missing-user', 'password': 'pass1234'},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['authenticated'], False)

    def test_authenticated_user_is_recognized_as_logged_in(self):
        self.client.post(
            self.login_url,
            data={'username': self.username, 'password': self.password},
        )

        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user, self.user)
