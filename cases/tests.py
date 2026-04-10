from django.test import TestCase
from django.conf import settings
from django.apps import apps

from cases.models import Case, Category, Subclinic
from cases.services import create_case, create_case_log, get_case_logs
from users.services import assign_role

User = apps.get_model(settings.AUTH_USER_MODEL)


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
        case = create_case(self.admin, 'description', self.category, self.subclinic)
        self.assertEqual(case.status.name, 'active')

    def test_advisor_creates_case_with_active_status(self):
        case = create_case(self.advisor, 'description', self.category, self.subclinic)
        self.assertEqual(case.status.name, 'active')

    def test_professor_creates_case_with_active_status(self):
        case = create_case(self.professor, 'description', self.category, self.subclinic)
        self.assertEqual(case.status.name, 'active')

    def test_student_creates_case_with_pending_authorization_status(self):
        case = create_case(self.student, 'description', self.category, self.subclinic)
        self.assertEqual(case.status.name, 'pending_authorization')

    def test_beneficiary_cannot_create_case(self):
        with self.assertRaises(PermissionError):
            create_case(self.beneficiary, 'description', self.category, self.subclinic)

    # --- Case field linkage ---

    def test_case_is_linked_to_creator(self):
        case = create_case(self.admin, 'description', self.category, self.subclinic)
        self.assertEqual(case.created_by, self.admin)

    def test_case_is_linked_to_category(self):
        case = create_case(self.admin, 'description', self.category, self.subclinic)
        self.assertEqual(case.category, self.category)

    def test_case_is_linked_to_subclinic(self):
        case = create_case(self.admin, 'description', self.category, self.subclinic)
        self.assertEqual(case.subclinic, self.subclinic)

    # --- Creator assignment and log ---

    def test_creator_is_automatically_assigned_to_case(self):
        case = create_case(self.admin, 'description', self.category, self.subclinic)
        self.assertTrue(case.users.filter(pk=self.admin.pk).exists())

    def test_initial_log_is_created(self):
        case = create_case(self.admin, 'description', self.category, self.subclinic)
        self.assertTrue(case.logs.filter(content__icontains='Case created by').exists())

    def test_case_is_persisted_to_database(self):
        case = create_case(self.admin, 'description', self.category, self.subclinic)
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

        self.case = create_case(self.student, 'Case for logs', self.category, self.subclinic)
        self.case.users.add(self.professor)

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

        logs = list(get_case_logs(self.case))
        self.assertGreaterEqual(len(logs), 3)
        self.assertEqual([logs[-3].pk, logs[-2].pk, logs[-1].pk], [first.pk, second.pk, third.pk])

    def test_log_content_cannot_be_empty(self):
        with self.assertRaises(ValueError):
            create_case_log(self.student, self.case, '   ')
