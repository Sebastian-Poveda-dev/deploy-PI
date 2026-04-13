from django.test import Client, TestCase
from django.contrib.auth.models import Group
from django.conf import settings
from django.apps import apps
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .services import admin_create_user, assign_role, list_users, update_user

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
        self.group, _ = Group.objects.get_or_create(name='student')

    def test_assign_role_to_user(self):
        self.user.groups.add(self.group)
        self.assertIn(self.group, self.user.groups.all())

    def test_user_belongs_to_role(self):
        self.user.groups.add(self.group)
        self.assertTrue(self.user.groups.filter(name='student').exists())

    def test_user_not_in_role_by_default(self):
        self.assertFalse(self.user.groups.filter(name='student').exists())

    def test_user_can_have_multiple_roles(self):
        advisor, _ = Group.objects.get_or_create(name='advisor')
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
        response = self.client.post(
            self.login_url,
            data={'username': self.username, 'password': self.password},
        )

        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user, self.user)

    def test_login_accepts_request_without_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)

        response = csrf_client.post(
            self.login_url,
            data={'username': self.username, 'password': self.password},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['authenticated'], True)


class RoleAssignmentMethodTest(TestCase):
    """Tests for assign_role() and role helper methods on the User model."""

    def setUp(self):
        self.user = User.objects.create_user(username='roleuser', password='pass1234')

    def test_assign_role_sets_correct_group(self):
        self.user.assign_role('student')
        self.assertTrue(self.user.groups.filter(name='student').exists())

    def test_assign_role_enforces_single_role(self):
        self.user.assign_role('student')
        self.user.assign_role('advisor')
        self.assertEqual(self.user.groups.count(), 1)

    def test_assign_role_replaces_previous_role(self):
        self.user.assign_role('student')
        self.user.assign_role('advisor')
        self.assertFalse(self.user.groups.filter(name='student').exists())
        self.assertTrue(self.user.groups.filter(name='advisor').exists())

    def test_assign_role_raises_for_nonexistent_role(self):
        with self.assertRaises(Group.DoesNotExist):
            self.user.assign_role('nonexistent')

    def test_helper_methods_return_false_with_no_role(self):
        self.assertFalse(self.user.is_admin())
        self.assertFalse(self.user.is_advisor())
        self.assertFalse(self.user.is_professor())
        self.assertFalse(self.user.is_student())
        self.assertFalse(self.user.is_beneficiary())

    def test_is_admin_returns_true(self):
        self.user.assign_role('admin')
        self.assertTrue(self.user.is_admin())

    def test_is_advisor_returns_true(self):
        self.user.assign_role('advisor')
        self.assertTrue(self.user.is_advisor())

    def test_is_professor_returns_true(self):
        self.user.assign_role('professor')
        self.assertTrue(self.user.is_professor())

    def test_is_student_returns_true(self):
        self.user.assign_role('student')
        self.assertTrue(self.user.is_student())

    def test_is_beneficiary_returns_true(self):
        self.user.assign_role('beneficiary')
        self.assertTrue(self.user.is_beneficiary())

    def test_helper_returns_false_for_other_roles(self):
        self.user.assign_role('student')
        self.assertFalse(self.user.is_admin())
        self.assertFalse(self.user.is_advisor())
        self.assertFalse(self.user.is_professor())
        self.assertFalse(self.user.is_beneficiary())
        
class SelfRegistrationTest(TestCase):
    """Tests for beneficiary self-registration flow."""

    def setUp(self):
        self.register_url = reverse('users:register')
        self.valid_payload = {
            'username': 'newuser',
            'first_name': 'Ana',
            'last_name': 'Perez',
            'email': 'ana@example.com',
            'residence_address': '123 Main St',
            'phone_number': '555-1234',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }

    def test_beneficiary_can_register_successfully(self):
        response = self.client.post(self.register_url, data=self.valid_payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['registered'], True)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        user = User.objects.get(username='newuser')
        self.assertEqual(user.first_name, 'Ana')
        self.assertEqual(user.last_name, 'Perez')
        self.assertEqual(user.email, 'ana@example.com')
        self.assertEqual(user.residence_address, '123 Main St')
        self.assertEqual(user.phone_number, '555-1234')

    def test_registered_user_has_beneficiary_role(self):
        self.client.post(self.register_url, data=self.valid_payload)

        user = User.objects.get(username='newuser')
        self.assertTrue(user.groups.filter(name='beneficiary').exists())

    def test_user_cannot_self_assign_different_role(self):
        payload = {**self.valid_payload, 'role': 'admin'}
        self.client.post(self.register_url, data=payload)

        user = User.objects.get(username='newuser')
        self.assertFalse(user.groups.filter(name='admin').exists())
        self.assertTrue(user.groups.filter(name='beneficiary').exists())

    def test_invalid_data_does_not_create_user(self):
        invalid_payload = {**self.valid_payload, 'email': ''}
        response = self.client.post(self.register_url, data=invalid_payload)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['registered'], False)
        self.assertIn('email', response.json()['errors'])
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_password_validation_is_enforced(self):
        weak_password_payload = {
            **self.valid_payload,
            'password1': '123',
            'password2': '123',
        }

        response = self.client.post(self.register_url, data=weak_password_payload)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['registered'], False)
        self.assertIn('password2', response.json()['errors'])
        self.assertFalse(User.objects.filter(username='newuser').exists())


class AdminUserCreationTest(TestCase):
    """Tests for admin-driven user creation flow."""

    def test_admin_can_create_user_with_role(self):
        user = admin_create_user('student1', 'pass1234', 'student')
        self.assertIsNotNone(user)
        self.assertTrue(User.objects.filter(username='student1').exists())

    def test_created_user_has_correct_role(self):
        user = admin_create_user('professor1', 'pass1234', 'professor')
        self.assertTrue(user.groups.filter(name='professor').exists())

    def test_created_user_has_only_one_role(self):
        user = admin_create_user('advisor1', 'pass1234', 'advisor')
        self.assertEqual(user.groups.count(), 1)

    def test_role_reassignment_removes_previous_role(self):
        user = admin_create_user('user1', 'pass1234', 'student')
        assign_role(user, 'advisor')
        self.assertFalse(user.groups.filter(name='student').exists())
        self.assertTrue(user.groups.filter(name='advisor').exists())
        self.assertEqual(user.groups.count(), 1)


<<<<<<< HEAD
class AdminUserManagementServiceTest(TestCase):
    """Tests for list_users and update_user service functions."""

    def setUp(self):
        self.admin = User.objects.create_user(username='admin_svc', password='pass')
        assign_role(self.admin, 'admin')

        self.student = User.objects.create_user(username='student_svc', password='pass')
        assign_role(self.student, 'student')

        self.advisor = User.objects.create_user(username='advisor_svc', password='pass')
        assign_role(self.advisor, 'advisor')

    def test_admin_can_list_users(self):
        users = list(list_users(self.admin))
        self.assertGreaterEqual(len(users), 1)

    def test_non_admin_cannot_list_users(self):
        with self.assertRaises(PermissionError):
            list_users(self.advisor)

    def test_list_users_includes_inactive_users(self):
        self.student.is_active = False
        self.student.save()
        users = list(list_users(self.admin))
        ids = [u.id for u in users]
        self.assertIn(self.student.id, ids)

    def test_admin_can_update_user_role(self):
        update_user(self.admin, self.student, {'role': 'advisor'})
        self.assertTrue(self.student.groups.filter(name='advisor').exists())

    def test_update_user_role_removes_previous_role(self):
        update_user(self.admin, self.student, {'role': 'professor'})
        self.assertFalse(self.student.groups.filter(name='student').exists())
        self.assertTrue(self.student.groups.filter(name='professor').exists())
        self.assertEqual(self.student.groups.count(), 1)

    def test_non_admin_cannot_update_user(self):
        with self.assertRaises(PermissionError):
            update_user(self.advisor, self.student, {'role': 'professor'})

    def test_admin_cannot_modify_own_account(self):
        with self.assertRaises(PermissionError):
            update_user(self.admin, self.admin, {'role': 'student'})

    def test_update_user_invalid_role_raises_value_error(self):
        with self.assertRaises(ValueError):
            update_user(self.admin, self.student, {'role': 'nonexistent'})

    def test_admin_can_deactivate_user(self):
        update_user(self.admin, self.student, {'is_active': False})
        self.student.refresh_from_db()
        self.assertFalse(self.student.is_active)

    def test_admin_can_reactivate_user(self):
        self.student.is_active = False
        self.student.save()
        update_user(self.admin, self.student, {'is_active': True})
        self.student.refresh_from_db()
        self.assertTrue(self.student.is_active)

    def test_admin_cannot_deactivate_self(self):
        with self.assertRaises(PermissionError):
            update_user(self.admin, self.admin, {'is_active': False})


class AdminUserManagementApiTest(APITestCase):
    """API tests for admin-only user management endpoints."""

    def setUp(self):
        self.admin = User.objects.create_user(username='admin_api_mgmt', password='pass')
        assign_role(self.admin, 'admin')

        self.advisor = User.objects.create_user(username='advisor_api_mgmt', password='pass')
        assign_role(self.advisor, 'advisor')

        self.student = User.objects.create_user(username='student_api_mgmt', password='pass')
        assign_role(self.student, 'student')

    # --- GET /users/ ---

    def test_admin_can_list_all_users(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_list_users_requires_authentication(self):
        response = self.client.get('/users/')
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_non_admin_cannot_list_users(self):
        self.client.force_authenticate(self.advisor)
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_users_response_contains_expected_fields(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        for field in ('id', 'username', 'role', 'is_active'):
            self.assertIn(field, response.data[0])

    def test_list_users_includes_inactive_users(self):
        self.student.is_active = False
        self.student.save()
        self.client.force_authenticate(self.admin)
        response = self.client.get('/users/')
        ids = [u['id'] for u in response.data]
        self.assertIn(self.student.id, ids)

    # --- POST /users/ ---

    def test_admin_can_create_user(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post('/users/', {
            'username': 'newprofessor_mgmt',
            'password': 'pass1234',
            'role': 'professor',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newprofessor_mgmt').exists())

    def test_create_user_requires_authentication(self):
        response = self.client.post('/users/', {
            'username': 'newuser_mgmt',
            'password': 'pass1234',
            'role': 'student',
        }, format='json')
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_non_admin_cannot_create_user(self):
        self.client.force_authenticate(self.advisor)
        response = self.client.post('/users/', {
            'username': 'newuser_mgmt',
            'password': 'pass1234',
            'role': 'student',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_user_with_duplicate_username_returns_400(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post('/users/', {
            'username': 'student_api_mgmt',
            'password': 'pass1234',
            'role': 'student',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_created_user_has_correct_role(self):
        self.client.force_authenticate(self.admin)
        self.client.post('/users/', {
            'username': 'newadvisor_mgmt',
            'password': 'pass1234',
            'role': 'advisor',
        }, format='json')
        user = User.objects.get(username='newadvisor_mgmt')
        self.assertTrue(user.groups.filter(name='advisor').exists())

    def test_create_user_with_invalid_role_returns_400(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post('/users/', {
            'username': 'newuser_mgmt',
            'password': 'pass1234',
            'role': 'nonexistent_role',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_response_contains_expected_fields(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post('/users/', {
            'username': 'newstudent_mgmt',
            'password': 'pass1234',
            'role': 'student',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for field in ('id', 'username', 'role', 'is_active'):
            self.assertIn(field, response.data)

    # --- PATCH /users/<id>/ ---

    def test_admin_can_change_user_role(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch(f'/users/{self.student.id}/', {
            'role': 'advisor',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertTrue(self.student.groups.filter(name='advisor').exists())

    def test_update_user_requires_authentication(self):
        response = self.client.patch(f'/users/{self.student.id}/', {
            'role': 'advisor',
        }, format='json')
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_non_admin_cannot_update_user(self):
        self.client.force_authenticate(self.advisor)
        response = self.client.patch(f'/users/{self.student.id}/', {
            'role': 'professor',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_change_own_role(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch(f'/users/{self.admin.id}/', {
            'role': 'student',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_deactivate_user(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch(f'/users/{self.student.id}/', {
            'is_active': False,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertFalse(self.student.is_active)

    def test_admin_cannot_deactivate_self(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch(f'/users/{self.admin.id}/', {
            'is_active': False,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_reactivate_user(self):
        self.student.is_active = False
        self.student.save()
        self.client.force_authenticate(self.admin)
        response = self.client.patch(f'/users/{self.student.id}/', {
            'is_active': True,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertTrue(self.student.is_active)

    def test_update_nonexistent_user_returns_404(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch('/users/99999/', {
            'role': 'student',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
class BeneficiaryListEndpointTest(TestCase):
    """Tests for the beneficiaries endpoint used by case creation form/modal."""

    def setUp(self):
        self.register_url = reverse('users:register')
        self.beneficiaries_url = reverse('users:beneficiaries')

        self.viewer = User.objects.create_user(username='admin_viewer', password='pass1234')
        assign_role(self.viewer, 'admin')

        self.valid_payload = {
            'username': 'beneficiary_new',
            'first_name': 'Laura',
            'last_name': 'Gomez',
            'email': 'laura@example.com',
            'residence_address': 'Street 123',
            'phone_number': '3000000000',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }

    def test_registered_beneficiary_is_returned_by_beneficiaries_endpoint(self):
        register_response = self.client.post(self.register_url, data=self.valid_payload)
        self.assertEqual(register_response.status_code, 201)

        self.client.force_login(self.viewer)
        response = self.client.get(self.beneficiaries_url)

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertTrue(any(item['full_name'] == 'Laura Gomez' for item in payload))
        self.assertTrue(any(item['id'] == User.objects.get(username='beneficiary_new').id for item in payload))

>>>>>>> dev
