from datetime import timedelta

from django.apps import apps
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from cases.models import Case, CaseAssignment, CaseStatus, Category, Subclinic
from documents.models import Document
from users.services import assign_role

User = apps.get_model(settings.AUTH_USER_MODEL)


class MetricsDashboardAccessTest(APITestCase):
    def setUp(self):
        self.beneficiary = User.objects.create_user(username='bene_access', password='pass')
        assign_role(self.beneficiary, 'beneficiary')
        self.admin = User.objects.create_user(username='admin_access', password='pass')
        assign_role(self.admin, 'admin')
        self.advisor = User.objects.create_user(username='advisor_access', password='pass')
        assign_role(self.advisor, 'advisor')
        self.student = User.objects.create_user(username='student_access', password='pass')
        assign_role(self.student, 'student')
        self.professor = User.objects.create_user(username='prof_access', password='pass')
        assign_role(self.professor, 'professor')

    def test_admin_can_access(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get('/metrics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_advisor_can_access(self):
        self.client.force_authenticate(self.advisor)
        response = self.client.get('/metrics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_student_cannot_access(self):
        self.client.force_authenticate(self.student)
        response = self.client.get('/metrics/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_professor_cannot_access(self):
        self.client.force_authenticate(self.professor)
        response = self.client.get('/metrics/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_beneficiary_cannot_access(self):
        self.client.force_authenticate(self.beneficiary)
        response = self.client.get('/metrics/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_access(self):
        response = self.client.get('/metrics/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class MetricsDashboardDataTest(APITestCase):
    def setUp(self):
        self.s_active = CaseStatus.objects.get(name='active')
        self.s_in_progress = CaseStatus.objects.get(name='in_progress')
        self.s_finished = CaseStatus.objects.get(name='finished')
        self.s_canceled = CaseStatus.objects.get(name='canceled')

        self.cat_laboral = Category.objects.get(name='laboral')
        self.cat_penal = Category.objects.get(name='penal')
        self.subclinic_a = Subclinic.objects.create(name='sub_a')
        self.subclinic_b = Subclinic.objects.create(name='sub_b')

        self.admin = User.objects.create_user(username='admin_data', password='pass')
        assign_role(self.admin, 'admin')
        self.student1 = User.objects.create_user(username='student1_data', password='pass')
        assign_role(self.student1, 'student')
        self.student2 = User.objects.create_user(username='student2_data', password='pass')
        assign_role(self.student2, 'student')
        self.professor = User.objects.create_user(username='prof_data', password='pass')
        assign_role(self.professor, 'professor')
        self.beneficiary = User.objects.create_user(username='bene_data', password='pass')
        assign_role(self.beneficiary, 'beneficiary')

        def make_case(status_obj, category, subclinic):
            return Case.objects.create(
                description='test case',
                created_by=self.admin,
                status=status_obj,
                category=category,
                subclinic=subclinic,
                beneficiary=self.beneficiary,
            )

        # 2 active, 1 in_progress, 2 finished (one per category), 1 canceled
        self.case_active1 = make_case(self.s_active, self.cat_laboral, self.subclinic_a)
        self.case_active2 = make_case(self.s_active, self.cat_penal, self.subclinic_b)
        self.case_in_progress = make_case(self.s_in_progress, self.cat_laboral, self.subclinic_a)
        self.case_finished_laboral = make_case(self.s_finished, self.cat_laboral, self.subclinic_a)
        self.case_finished_penal = make_case(self.s_finished, self.cat_penal, self.subclinic_b)
        self.case_canceled = make_case(self.s_canceled, self.cat_laboral, self.subclinic_a)

        # student1 → 2 active-status cases, student2 → 0 active (only finished), professor → 0 active
        CaseAssignment.objects.create(case=self.case_active1, user=self.student1)
        CaseAssignment.objects.create(case=self.case_in_progress, user=self.student1)
        CaseAssignment.objects.create(case=self.case_finished_laboral, user=self.student2)
        CaseAssignment.objects.create(case=self.case_finished_penal, user=self.professor)
        # case_active2 and case_canceled have no assignment

        today = timezone.now().date()
        self.doc_expired = Document.objects.create(
            name='expired_doc', description='expired', file='cases/1/a.pdf',
            case=self.case_active1, uploaded_by=self.admin,
            is_expired=True, expiration_date=today - timedelta(days=10),
        )
        self.doc_expiring_soon = Document.objects.create(
            name='expiring_soon_doc', description='soon', file='cases/1/b.pdf',
            case=self.case_active1, uploaded_by=self.admin,
            is_expired=False, expiration_date=today + timedelta(days=3),
        )
        self.doc_ok = Document.objects.create(
            name='ok_doc', description='ok', file='cases/1/c.pdf',
            case=self.case_active1, uploaded_by=self.admin,
            is_expired=False, expiration_date=today + timedelta(days=30),
        )

        self.client.force_authenticate(self.admin)

    def test_response_has_all_metric_keys(self):
        response = self.client.get('/metrics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in [
            'cases_by_status', 'cases_by_category', 'cases_by_subclinic',
            'working_velocity', 'avg_resolution_time', 'opened_vs_closed',
            'cases_per_user', 'unassigned_cases', 'cancellation_rate',
            'document_expiration',
        ]:
            self.assertIn(key, response.data)

    def test_cases_by_status(self):
        response = self.client.get('/metrics/')
        by_status = {item['status']: item['count'] for item in response.data['cases_by_status']}
        self.assertEqual(by_status.get('active'), 2)
        self.assertEqual(by_status.get('in_progress'), 1)
        self.assertEqual(by_status.get('finished'), 2)
        self.assertEqual(by_status.get('canceled'), 1)

    def test_cases_by_category(self):
        response = self.client.get('/metrics/')
        by_cat = {item['category']: item['count'] for item in response.data['cases_by_category']}
        # laboral: active1, in_progress, finished_laboral, canceled = 4
        # penal: active2, finished_penal = 2
        self.assertEqual(by_cat.get('laboral'), 4)
        self.assertEqual(by_cat.get('penal'), 2)

    def test_cases_by_subclinic(self):
        response = self.client.get('/metrics/')
        by_sub = {item['subclinic']: item['count'] for item in response.data['cases_by_subclinic']}
        self.assertEqual(by_sub.get('sub_a'), 4)
        self.assertEqual(by_sub.get('sub_b'), 2)

    def test_working_velocity_total_finished(self):
        response = self.client.get('/metrics/')
        velocity = response.data['working_velocity']
        self.assertTrue(len(velocity) >= 1)
        total = sum(item['count'] for item in velocity)
        self.assertEqual(total, 2)

    def test_working_velocity_item_structure(self):
        response = self.client.get('/metrics/')
        item = response.data['working_velocity'][0]
        self.assertIn('month', item)
        self.assertIn('count', item)

    def test_avg_resolution_time_categories(self):
        response = self.client.get('/metrics/')
        avg_res = response.data['avg_resolution_time']
        categories = {item['category'] for item in avg_res}
        self.assertIn('laboral', categories)
        self.assertIn('penal', categories)

    def test_avg_resolution_time_non_negative(self):
        response = self.client.get('/metrics/')
        for item in response.data['avg_resolution_time']:
            self.assertIn('avg_days', item)
            self.assertGreaterEqual(item['avg_days'], 0)

    def test_opened_vs_closed_totals(self):
        response = self.client.get('/metrics/')
        ovc = response.data['opened_vs_closed']
        total_opened = sum(item['opened'] for item in ovc)
        total_closed = sum(item['closed'] for item in ovc)
        self.assertEqual(total_opened, 6)   # all 6 cases opened this month
        self.assertEqual(total_closed, 3)   # finished (2) + canceled (1)

    def test_opened_vs_closed_item_structure(self):
        response = self.client.get('/metrics/')
        item = response.data['opened_vs_closed'][0]
        self.assertIn('month', item)
        self.assertIn('opened', item)
        self.assertIn('closed', item)

    def test_cases_per_user_active_counts(self):
        response = self.client.get('/metrics/')
        per_user = {u['username']: u['active_cases'] for u in response.data['cases_per_user']}
        # student1: active1 + in_progress → both in ACTIVE_STATUSES → 2
        self.assertEqual(per_user.get('student1_data'), 2)
        # student2: only finished_laboral → NOT in ACTIVE_STATUSES → 0
        self.assertEqual(per_user.get('student2_data'), 0)
        # professor: only finished_penal → 0
        self.assertEqual(per_user.get('prof_data'), 0)

    def test_cases_per_user_only_student_and_professor_roles(self):
        response = self.client.get('/metrics/')
        per_user = response.data['cases_per_user']
        roles = {u['role'] for u in per_user}
        self.assertTrue(roles.issubset({'student', 'professor'}))
        admin_entries = [u for u in per_user if u['username'] == 'admin_data']
        self.assertEqual(len(admin_entries), 0)

    def test_cases_per_user_item_structure(self):
        response = self.client.get('/metrics/')
        item = response.data['cases_per_user'][0]
        for key in ['id', 'username', 'first_name', 'last_name', 'role', 'active_cases']:
            self.assertIn(key, item)

    def test_unassigned_cases(self):
        response = self.client.get('/metrics/')
        # Only active-status cases without assignment count: case_active2
        # case_canceled is also unassigned but has non-active status
        self.assertEqual(response.data['unassigned_cases'], 1)

    def test_cancellation_rate(self):
        response = self.client.get('/metrics/')
        rate_data = response.data['cancellation_rate']
        self.assertEqual(rate_data['total'], 6)
        self.assertEqual(rate_data['canceled'], 1)
        self.assertAlmostEqual(rate_data['rate'], round(1 / 6, 4), places=4)

    def test_document_expiration_counts(self):
        response = self.client.get('/metrics/')
        doc_exp = response.data['document_expiration']
        self.assertEqual(doc_exp['expired'], 1)
        self.assertEqual(doc_exp['expiring_soon'], 1)

    def test_document_expiration_structure(self):
        response = self.client.get('/metrics/')
        doc_exp = response.data['document_expiration']
        self.assertIn('expired', doc_exp)
        self.assertIn('expiring_soon', doc_exp)
