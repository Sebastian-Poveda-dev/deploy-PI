from django.test import TestCase
from django.conf import settings
from django.apps import apps
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.test import APITestCase

from cases.forms import CaseCreateForm
from cases.models import Case, Category, Subclinic
from cases.services import create_case, create_case_log, get_case_logs, update_case, approve_case, reject_case_assignment
from users.services import assign_role

User = apps.get_model(settings.AUTH_USER_MODEL)


class CaseCreateFormAndTemplateTest(TestCase):
    def setUp(self):
        self.subclinic = Subclinic.objects.create(name='beneficiary_subclinic')
        self.category, _ = Category.objects.get_or_create(name='beneficiary_category')

        self.admin = User.objects.create_user(username='admin_form', password='pass')
        assign_role(self.admin, 'admin')

        self.beneficiary_a = User.objects.create_user(
            username='beneficiary_a',
            password='pass',
            first_name='Ana',
            last_name='Zuluaga',
        )
        assign_role(self.beneficiary_a, 'beneficiary')

        self.beneficiary_b = User.objects.create_user(
            username='beneficiary_b',
            password='pass',
            first_name='Bruno',
            last_name='Alvarez',
        )
        assign_role(self.beneficiary_b, 'beneficiary')

        self.non_beneficiary = User.objects.create_user(
            username='student_form',
            password='pass',
            first_name='Carlos',
            last_name='Perez',
        )
        assign_role(self.non_beneficiary, 'student')

    def _form_data(self, **overrides):
        data = {
            'description': 'Case with beneficiary from form',
            'category': self.category.id,
            'subclinic': self.subclinic.id,
            'beneficiary': self.beneficiary_a.id,
        }
        data.update(overrides)
        return data

    def test_only_beneficiaries_appear_in_beneficiary_field_queryset(self):
        form = CaseCreateForm()
        beneficiary_ids = list(form.fields['beneficiary'].queryset.values_list('id', flat=True))

        self.assertEqual(beneficiary_ids, [self.beneficiary_a.id, self.beneficiary_b.id])
        self.assertNotIn(self.non_beneficiary.id, beneficiary_ids)

    def test_case_can_be_created_with_valid_beneficiary(self):
        form = CaseCreateForm(data=self._form_data())
        self.assertTrue(form.is_valid(), form.errors)

        case = create_case(
            self.admin,
            form.cleaned_data['description'],
            form.cleaned_data['category'],
            form.cleaned_data['subclinic'],
            beneficiary=form.cleaned_data['beneficiary'],
        )

        self.assertEqual(case.beneficiary, self.beneficiary_a)

    def test_assigning_non_beneficiary_user_raises_validation_error(self):
        with self.assertRaises(ValueError):
            create_case(
                self.admin,
                'Case with invalid beneficiary',
                self.category,
                self.subclinic,
                beneficiary=self.non_beneficiary,
            )

    def test_beneficiary_field_is_required(self):
        form = CaseCreateForm(data=self._form_data(beneficiary=''))

        self.assertFalse(form.is_valid())
        self.assertIn('beneficiary', form.errors)

    def test_case_create_template_renders_beneficiary_select_with_full_name(self):
        html = render_to_string('cases/case_form.html', {'form': CaseCreateForm(), 'created': False})

        self.assertIn('name="beneficiary"', html)
        self.assertIn('Ana Zuluaga', html)
        self.assertIn('Bruno Alvarez', html)
        self.assertNotIn('Carlos Perez', html)


class CreateCaseTest(TestCase):
    """Tests for role-based case creation logic."""

    def setUp(self):
        self.subclinic = Subclinic.objects.create(name='civil')
        self.category, _ = Category.objects.get_or_create(name='laboral')

        self.admin = User.objects.create_user(username='admin1', password='pass')
        assign_role(self.admin, 'admin')

        self.advisor = User.objects.create_user(username='advisor1', password='pass')
        assign_role(self.advisor, 'advisor')

        self.professor = User.objects.create_user(username='professor1', password='pass')
        assign_role(self.professor, 'professor')

        self.student = User.objects.create_user(username='student1', password='pass')
        assign_role(self.student, 'student')

        self.beneficiary = User.objects.create_user(username='beneficiary1', password='pass')
        assign_role(self.beneficiary, 'beneficiary')

    # --- Role-based status assignment ---

    def test_admin_creates_case_with_active_status(self):
        case = create_case(self.admin, 'description', self.category, self.subclinic, beneficiary=self.beneficiary)
        self.assertEqual(case.status.name, 'active')

    def test_advisor_creates_case_with_active_status(self):
        case = create_case(self.advisor, 'description', self.category, self.subclinic, beneficiary=self.beneficiary)
        self.assertEqual(case.status.name, 'active')

    def test_professor_creates_case_with_active_status(self):
        case = create_case(self.professor, 'description', self.category, self.subclinic, beneficiary=self.beneficiary)
        self.assertEqual(case.status.name, 'active')

    def test_student_creates_case_with_pending_authorization_status(self):
        case = create_case(self.student, 'description', self.category, self.subclinic, professor=self.professor)
        self.assertEqual(case.status.name, 'pending_authorization')

    def test_student_without_professor_cannot_create_case(self):
        with self.assertRaises(ValueError):
            create_case(self.student, 'description', self.category, self.subclinic)

    def test_beneficiary_cannot_create_case(self):
        with self.assertRaises(PermissionError):
            create_case(self.beneficiary, 'description', self.category, self.subclinic, beneficiary=self.beneficiary)

    # --- Case field linkage ---

    def test_case_is_linked_to_creator(self):
        case = create_case(self.admin, 'description', self.category, self.subclinic, beneficiary=self.beneficiary)
        self.assertEqual(case.created_by, self.admin)

    def test_case_is_linked_to_category(self):
        case = create_case(self.admin, 'description', self.category, self.subclinic, beneficiary=self.beneficiary)
        self.assertEqual(case.category, self.category)

    def test_case_is_linked_to_subclinic(self):
        case = create_case(self.admin, 'description', self.category, self.subclinic, beneficiary=self.beneficiary)
        self.assertEqual(case.subclinic, self.subclinic)

    # --- Creator assignment and log ---

    def test_creator_is_automatically_assigned_to_case(self):
        case = create_case(self.admin, 'description', self.category, self.subclinic, beneficiary=self.beneficiary)
        self.assertTrue(case.users.filter(pk=self.admin.pk).exists())

    def test_initial_log_is_created(self):
        case = create_case(self.admin, 'description', self.category, self.subclinic, beneficiary=self.beneficiary)
        self.assertTrue(case.logs.filter(content__icontains='Case created by').exists())

    def test_case_is_persisted_to_database(self):
        case = create_case(self.admin, 'description', self.category, self.subclinic, beneficiary=self.beneficiary)
        self.assertIsNotNone(case.pk)
        self.assertTrue(Case.objects.filter(pk=case.pk).exists())


class CaseLogServiceTest(TestCase):
    """Tests for case log creation and retrieval rules."""

    def setUp(self):
        self.subclinic = Subclinic.objects.create(name='family')
        self.category, _ = Category.objects.get_or_create(name='civil')

        self.admin = User.objects.create_user(username='admin_logs', password='pass')
        assign_role(self.admin, 'admin')

        self.advisor = User.objects.create_user(username='advisor_logs', password='pass')
        assign_role(self.advisor, 'advisor')

        self.professor = User.objects.create_user(username='professor_logs', password='pass')
        assign_role(self.professor, 'professor')

        self.student = User.objects.create_user(username='student_logs', password='pass')
        assign_role(self.student, 'student')

        self.beneficiary = User.objects.create_user(username='beneficiary_logs', password='pass')
        assign_role(self.beneficiary, 'beneficiary')

        self.other_student = User.objects.create_user(username='other_student_logs', password='pass')
        assign_role(self.other_student, 'student')

        self.case = create_case(self.student, 'Case for logs', self.category, self.subclinic, professor=self.professor)


    def test_valid_roles_can_create_case_log(self):
        valid_users = [self.student, self.professor, self.advisor, self.admin]

        for index, user in enumerate(valid_users, start=1):
            log = create_case_log(user, self.case, f'Log from {user.username} #{index}')
            self.assertEqual(log.user, user)
            self.assertEqual(log.case, self.case)

    def test_beneficiary_cannot_create_case_log(self):
        self.case.users.add(self.beneficiary)

        with self.assertRaises(PermissionError):
            create_case_log(self.beneficiary, self.case, 'I should not be able to log')

    def test_unassigned_non_privileged_user_cannot_create_case_log(self):
        with self.assertRaises(PermissionError):
            create_case_log(self.other_student, self.case, 'Not assigned to case')

    def test_log_is_associated_with_case(self):
        log = create_case_log(self.student, self.case, 'Progress update')
        self.assertTrue(self.case.logs.filter(pk=log.pk).exists())

    def test_logs_are_returned_in_chronological_order(self):
        first = create_case_log(self.professor, self.case, 'First feedback')
        second = create_case_log(self.student, self.case, 'Second update')
        third = create_case_log(self.advisor, self.case, 'Third note')

        logs = list(get_case_logs(self.case, self.student))
        self.assertGreaterEqual(len(logs), 3)
        self.assertEqual([logs[-3].pk, logs[-2].pk, logs[-1].pk], [first.pk, second.pk, third.pk])

    def test_privileged_role_can_log_without_being_assigned(self):
        # advisor and admin are not assigned to the case (only student and professor are)
        self.assertFalse(self.case.users.filter(pk=self.advisor.pk).exists())
        self.assertFalse(self.case.users.filter(pk=self.admin.pk).exists())

        advisor_log = create_case_log(self.advisor, self.case, 'Advisor note without assignment')
        admin_log = create_case_log(self.admin, self.case, 'Admin note without assignment')

        self.assertEqual(advisor_log.case, self.case)
        self.assertEqual(admin_log.case, self.case)

    def test_log_content_cannot_be_empty(self):
        with self.assertRaises(ValueError):
            create_case_log(self.student, self.case, '   ')


class UpdateCaseTest(TestCase):
    """Tests for role-based case update logic."""

    def setUp(self):
        self.subclinic = Subclinic.objects.create(name='criminal')
        self.new_subclinic = Subclinic.objects.create(name='update_civil')
        self.category, _ = Category.objects.get_or_create(name='laboral')
        self.new_category, _ = Category.objects.get_or_create(name='penal')

        self.admin = User.objects.create_user(username='admin_upd', password='pass')
        assign_role(self.admin, 'admin')

        self.advisor = User.objects.create_user(username='advisor_upd', password='pass')
        assign_role(self.advisor, 'advisor')

        self.professor = User.objects.create_user(username='professor_upd', password='pass')
        assign_role(self.professor, 'professor')

        self.student = User.objects.create_user(username='student_upd', password='pass')
        assign_role(self.student, 'student')

        self.beneficiary = User.objects.create_user(username='beneficiary_upd', password='pass')
        assign_role(self.beneficiary, 'beneficiary')

        self.other_student = User.objects.create_user(username='other_student_upd', password='pass')
        assign_role(self.other_student, 'student')

        # student is creator (auto-assigned); professor is co-assigned via create_case
        self.case = create_case(self.student, 'Original description', self.category, self.subclinic, professor=self.professor)

    # --- Access control ---

    def test_assigned_user_can_update_case(self):
        updated = update_case(self.case, self.student, {'description': 'Updated by student'})
        self.assertEqual(updated.description, 'Updated by student')

    def test_admin_can_update_case_without_being_assigned(self):
        self.assertFalse(self.case.users.filter(pk=self.admin.pk).exists())
        updated = update_case(self.case, self.admin, {'description': 'Updated by admin'})
        self.assertEqual(updated.description, 'Updated by admin')

    def test_advisor_can_update_case_without_being_assigned(self):
        self.assertFalse(self.case.users.filter(pk=self.advisor.pk).exists())
        updated = update_case(self.case, self.advisor, {'description': 'Updated by advisor'})
        self.assertEqual(updated.description, 'Updated by advisor')

    def test_non_assigned_user_cannot_update_case(self):
        with self.assertRaises(PermissionError):
            update_case(self.case, self.other_student, {'description': 'Should not work'})

    def test_beneficiary_cannot_update_case(self):
        with self.assertRaises(PermissionError):
            update_case(self.case, self.beneficiary, {'description': 'Should not work'})

    # --- Field update rules ---

    def test_allowed_fields_are_updated(self):
        updated = update_case(self.case, self.student, {
            'description': 'New description',
            'category': self.new_category,
            'subclinic': self.new_subclinic,
        })
        self.assertEqual(updated.description, 'New description')
        self.assertEqual(updated.category, self.new_category)
        self.assertEqual(updated.subclinic, self.new_subclinic)

    def test_disallowed_fields_are_not_modified(self):
        original_status = self.case.status
        original_creator = self.case.created_by

        update_case(self.case, self.student, {
            'description': 'New description',
            'status': None,
            'created_by': self.admin,
        })

        self.case.refresh_from_db()
        self.assertEqual(self.case.status, original_status)
        self.assertEqual(self.case.created_by, original_creator)

    # --- Audit log ---

    def test_case_log_is_created_after_update(self):
        update_case(self.case, self.student, {'description': 'Updated'})
        self.assertTrue(self.case.logs.filter(content__icontains='Case updated by').exists())


class ApproveCaseTest(TestCase):
    """Tests for role-based case approval logic."""

    def setUp(self):
        self.subclinic = Subclinic.objects.create(name='approval_sub')
        self.category, _ = Category.objects.get_or_create(name='laboral')

        self.admin = User.objects.create_user(username='admin_appr', password='pass')
        assign_role(self.admin, 'admin')

        self.advisor = User.objects.create_user(username='advisor_appr', password='pass')
        assign_role(self.advisor, 'advisor')

        self.professor = User.objects.create_user(username='professor_appr', password='pass')
        assign_role(self.professor, 'professor')

        self.other_professor = User.objects.create_user(username='other_prof_appr', password='pass')
        assign_role(self.other_professor, 'professor')

        self.student = User.objects.create_user(username='student_appr', password='pass')
        assign_role(self.student, 'student')

        self.beneficiary = User.objects.create_user(username='beneficiary_appr', password='pass')
        assign_role(self.beneficiary, 'beneficiary')

        # student creates the case → status is "pending_authorization", both student and professor assigned
        self.case = create_case(self.student, 'Pending case', self.category, self.subclinic, professor=self.professor)


    # --- Access control ---

    def test_admin_can_approve_case(self):
        approved = approve_case(self.case, self.admin)
        self.assertEqual(approved.status.name, 'active')

    def test_advisor_can_approve_case(self):
        approved = approve_case(self.case, self.advisor)
        self.assertEqual(approved.status.name, 'active')

    def test_assigned_professor_can_approve_case(self):
        approved = approve_case(self.case, self.professor)
        self.assertEqual(approved.status.name, 'active')

    def test_non_assigned_professor_cannot_approve_case(self):
        with self.assertRaises(PermissionError):
            approve_case(self.case, self.other_professor)

    def test_student_cannot_approve_case(self):
        with self.assertRaises(PermissionError):
            approve_case(self.case, self.student)

    def test_beneficiary_cannot_approve_case(self):
        with self.assertRaises(PermissionError):
            approve_case(self.case, self.beneficiary)

    # --- Status transition ---

    def test_case_status_changes_to_active(self):
        self.assertEqual(self.case.status.name, 'pending_authorization')
        approve_case(self.case, self.admin)
        self.case.refresh_from_db()
        self.assertEqual(self.case.status.name, 'active')

    def test_cannot_approve_case_not_in_pending_authorization(self):
        approve_case(self.case, self.admin)  # first approval → now active
        self.case.refresh_from_db()
        with self.assertRaises(ValueError):
            approve_case(self.case, self.admin)

    # --- Audit log ---

    def test_case_log_is_created_after_approval(self):
        approve_case(self.case, self.admin)
        self.assertTrue(self.case.logs.filter(content__icontains='Case approved by').exists())


class RejectCaseAssignmentTest(TestCase):
    """Tests for user self-removal from a case assignment."""

    def setUp(self):
        self.subclinic = Subclinic.objects.create(name='reject_sub')
        self.category, _ = Category.objects.get_or_create(name='laboral')

        self.admin = User.objects.create_user(username='admin_rej', password='pass')
        assign_role(self.admin, 'admin')

        self.advisor = User.objects.create_user(username='advisor_rej', password='pass')
        assign_role(self.advisor, 'advisor')

        self.professor = User.objects.create_user(username='professor_rej', password='pass')
        assign_role(self.professor, 'professor')

        self.student = User.objects.create_user(username='student_rej', password='pass')
        assign_role(self.student, 'student')

        self.beneficiary = User.objects.create_user(username='beneficiary_rej', password='pass')
        assign_role(self.beneficiary, 'beneficiary')

        self.other_student = User.objects.create_user(username='other_student_rej', password='pass')
        assign_role(self.other_student, 'student')


        # student creates the case; professor co-assigned via create_case
        self.case = create_case(self.student, 'Case for rejection', self.category, self.subclinic, professor=self.professor)

    # --- Access control ---

    def test_assigned_student_can_reject_assignment(self):
        reject_case_assignment(self.case, self.student)
        self.assertFalse(self.case.users.filter(pk=self.student.pk).exists())

    def test_assigned_professor_can_reject_when_another_professor_remains(self):
        second_professor = User.objects.create_user(username='professor2_rej', password='pass')
        assign_role(second_professor, 'professor')
        self.case.users.add(second_professor)
        reject_case_assignment(self.case, self.professor)
        self.assertFalse(self.case.users.filter(pk=self.professor.pk).exists())

    def test_professor_cannot_reject_if_leaves_student_without_professor(self):
        with self.assertRaises(PermissionError):
            reject_case_assignment(self.case, self.professor)

    def test_non_assigned_user_cannot_reject(self):
        with self.assertRaises(PermissionError):
            reject_case_assignment(self.case, self.other_student)

    def test_admin_cannot_reject_assignment(self):
        with self.assertRaises(PermissionError):
            reject_case_assignment(self.case, self.admin)

    def test_advisor_cannot_reject_assignment(self):
        with self.assertRaises(PermissionError):
            reject_case_assignment(self.case, self.advisor)

    def test_beneficiary_cannot_reject_assignment(self):
        with self.assertRaises(PermissionError):
            reject_case_assignment(self.case, self.beneficiary)

    # --- Assignment removal ---

    def test_case_assignment_record_is_deleted(self):
        from cases.models import CaseAssignment
        reject_case_assignment(self.case, self.student)
        self.assertFalse(
            CaseAssignment.objects.filter(case=self.case, user=self.student).exists()
        )

    # --- Case status unchanged ---

    def test_case_status_is_not_modified(self):
        original_status = self.case.status
        reject_case_assignment(self.case, self.student)
        self.case.refresh_from_db()
        self.assertEqual(self.case.status, original_status)

    # --- Audit log ---

    def test_case_log_is_created_after_rejection(self):
        reject_case_assignment(self.case, self.student)
        self.assertTrue(
            self.case.logs.filter(content__icontains='rejected the case assignment').exists()
        )


class CaseApiTest(APITestCase):
    """API tests for cases endpoints wired to the service layer."""

    def setUp(self):
        self.subclinic = Subclinic.objects.create(name='api_subclinic')
        self.category, _ = Category.objects.get_or_create(name='laboral')
        self.other_category, _ = Category.objects.get_or_create(name='penal')

        self.admin = User.objects.create_user(username='admin_api', password='pass')
        assign_role(self.admin, 'admin')

        self.advisor = User.objects.create_user(username='advisor_api', password='pass')
        assign_role(self.advisor, 'advisor')

        self.professor = User.objects.create_user(username='professor_api', password='pass')
        assign_role(self.professor, 'professor')

        self.student = User.objects.create_user(username='student_api', password='pass')
        assign_role(self.student, 'student')

        self.other_student = User.objects.create_user(username='other_student_api', password='pass')
        assign_role(self.other_student, 'student')

        self.beneficiary = User.objects.create_user(username='beneficiary_api', password='pass')
        assign_role(self.beneficiary, 'beneficiary')


        self.case = create_case(self.student, 'Initial API case', self.category, self.subclinic, professor=self.professor)

    def test_create_case_requires_authentication(self):
        response = self.client.post('/cases/', {
            'description': 'Created via API',
            'category_id': self.category.id,
            'subclinic_id': self.subclinic.id,
            'beneficiary_id': self.beneficiary.id,
        }, format='json')
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_create_case_success_for_authenticated_user(self):
        self.client.force_authenticate(self.student)
        response = self.client.post('/cases/', {
            'description': 'Created via API',
            'category_id': self.category.id,
            'subclinic_id': self.subclinic.id,

            'professor_id': self.professor.id,

        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['description'], 'Created via API')
        self.assertEqual(response.data['created_by'], self.student.id)

    def test_create_case_invalid_input_returns_400(self):
        self.client.force_authenticate(self.student)
        response = self.client.post('/cases/', {
            'description': 'Missing category and subclinic',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_case_forbidden_role_returns_403(self):
        self.client.force_authenticate(self.beneficiary)
        response = self.client.post('/cases/', {
            'description': 'Should fail',
            'category_id': self.category.id,
            'subclinic_id': self.subclinic.id,
            'beneficiary_id': self.beneficiary.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_case_success_for_assigned_user(self):
        self.client.force_authenticate(self.student)
        response = self.client.patch(f'/cases/{self.case.id}/', {
            'description': 'Updated via API',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated via API')

    def test_update_case_forbidden_for_unassigned_user(self):
        self.client.force_authenticate(self.other_student)
        response = self.client.patch(f'/cases/{self.case.id}/', {
            'description': 'Should not update',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_case_not_found_returns_404(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch('/cases/99999/', {
            'description': 'Unknown case',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_approve_case_success(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(f'/cases/{self.case.id}/approve/', {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'active')

    def test_approve_case_invalid_operation_returns_400(self):
        self.client.force_authenticate(self.admin)
        first = self.client.post(f'/cases/{self.case.id}/approve/', {}, format='json')
        self.assertEqual(first.status_code, status.HTTP_200_OK)

        second = self.client.post(f'/cases/{self.case.id}/approve/', {}, format='json')
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)

    def test_approve_case_forbidden_role_returns_403(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(f'/cases/{self.case.id}/approve/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reject_assignment_success_and_unassigns_user(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(f'/cases/{self.case.id}/reject-assignment/', {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Case assignment rejected.')
        self.assertFalse(self.case.users.filter(pk=self.student.pk).exists())

    def test_reject_assignment_forbidden_role_returns_403(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(f'/cases/{self.case.id}/reject-assignment/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CaseListApiTest(APITestCase):
    """API tests for GET /cases/ — list cases for the authenticated user."""

    def setUp(self):
        self.subclinic = Subclinic.objects.create(name='list_subclinic')
        self.category, _ = Category.objects.get_or_create(name='laboral')

        self.admin = User.objects.create_user(username='admin_list_api', password='pass')
        assign_role(self.admin, 'admin')

        self.professor = User.objects.create_user(username='professor_list_api', password='pass')
        assign_role(self.professor, 'professor')

        self.student = User.objects.create_user(username='student_list_api', password='pass')
        assign_role(self.student, 'student')

        self.other_student = User.objects.create_user(username='other_student_list_api', password='pass')
        assign_role(self.other_student, 'student')

        self.beneficiary = User.objects.create_user(username='beneficiary_list_api', password='pass')
        assign_role(self.beneficiary, 'beneficiary')

        self.case = create_case(self.student, 'Case for listing', self.category, self.subclinic, professor=self.professor)


    def test_unauthenticated_request_is_rejected(self):
        response = self.client.get('/cases/')
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_assigned_student_sees_their_cases(self):
        self.client.force_authenticate(self.student)
        response = self.client.get('/cases/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [c['id'] for c in response.data]
        self.assertIn(self.case.id, ids)

    def test_unassigned_student_does_not_see_case(self):
        self.client.force_authenticate(self.other_student)
        response = self.client.get('/cases/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [c['id'] for c in response.data]
        self.assertNotIn(self.case.id, ids)

    def test_admin_sees_all_cases(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get('/cases/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [c['id'] for c in response.data]
        self.assertIn(self.case.id, ids)

    def test_response_contains_expected_fields(self):
        self.client.force_authenticate(self.student)
        response = self.client.get('/cases/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        case_data = response.data[0]
        for field in ('id', 'status', 'category', 'created_at', 'updated_at', 'assigned_users'):
            self.assertIn(field, case_data)

    def test_assigned_users_lists_case_members(self):
        self.client.force_authenticate(self.student)
        response = self.client.get('/cases/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        case_data = next(c for c in response.data if c['id'] == self.case.id)
        usernames = [u['name'] for u in case_data['assigned_users']]
        self.assertIn(self.student.username, usernames)


class CaseLogApiTest(APITestCase):
    """API tests for case logs endpoints wired to the service layer."""

    def setUp(self):
        self.subclinic = Subclinic.objects.create(name='api_logs_subclinic')
        self.category, _ = Category.objects.get_or_create(name='laboral')

        self.admin = User.objects.create_user(username='admin_logs_api', password='pass')
        assign_role(self.admin, 'admin')

        self.advisor = User.objects.create_user(username='advisor_logs_api', password='pass')
        assign_role(self.advisor, 'advisor')

        self.professor = User.objects.create_user(username='professor_logs_api', password='pass')
        assign_role(self.professor, 'professor')

        self.student = User.objects.create_user(username='student_logs_api', password='pass')
        assign_role(self.student, 'student')

        self.other_student = User.objects.create_user(username='other_student_logs_api', password='pass')
        assign_role(self.other_student, 'student')

        self.beneficiary = User.objects.create_user(username='beneficiary_logs_api', password='pass')
        assign_role(self.beneficiary, 'beneficiary')


        self.case = create_case(self.student, 'Case with logs endpoint', self.category, self.subclinic, professor=self.professor)

        self.initial_log = create_case_log(self.student, self.case, 'Initial chat message')

    def test_assigned_user_can_retrieve_logs(self):
        self.client.force_authenticate(self.student)
        response = self.client.get(f'/cases/{self.case.id}/logs/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_admin_can_retrieve_logs(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(f'/cases/{self.case.id}/logs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_advisor_can_retrieve_logs(self):
        self.client.force_authenticate(self.advisor)
        response = self.client.get(f'/cases/{self.case.id}/logs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_assigned_user_cannot_retrieve_logs(self):
        self.client.force_authenticate(self.other_student)
        response = self.client.get(f'/cases/{self.case.id}/logs/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_beneficiary_cannot_retrieve_logs(self):
        self.client.force_authenticate(self.beneficiary)
        response = self.client.get(f'/cases/{self.case.id}/logs/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_assigned_user_can_create_logs(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(
            f'/cases/{self.case.id}/logs/',
            {'content': 'Log from assigned student'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Log from assigned student')

    def test_admin_can_create_logs(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            f'/cases/{self.case.id}/logs/',
            {'content': 'Log from admin'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_advisor_can_create_logs(self):
        self.client.force_authenticate(self.advisor)
        response = self.client.post(
            f'/cases/{self.case.id}/logs/',
            {'content': 'Log from advisor'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_non_assigned_user_cannot_create_logs(self):
        self.client.force_authenticate(self.other_student)
        response = self.client.post(
            f'/cases/{self.case.id}/logs/',
            {'content': 'Should fail'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_beneficiary_cannot_create_logs(self):
        self.client.force_authenticate(self.beneficiary)
        response = self.client.post(
            f'/cases/{self.case.id}/logs/',
            {'content': 'Should fail'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logs_are_associated_with_case(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(
            f'/cases/{self.case.id}/logs/',
            {'content': 'Association check'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.case.logs.filter(pk=response.data['id']).exists())

    def test_logs_response_format_is_correct(self):
        self.client.force_authenticate(self.student)
        response = self.client.get(f'/cases/{self.case.id}/logs/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        log_item = response.data[-1]
        self.assertIn('id', log_item)
        self.assertIn('content', log_item)
        self.assertIn('created_at', log_item)
        self.assertIn('created_by', log_item)

