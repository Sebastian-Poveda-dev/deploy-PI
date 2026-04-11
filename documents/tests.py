from django.test import TestCase
from django.conf import settings
from django.apps import apps
from django.core.files.uploadedfile import SimpleUploadedFile

from cases.models import Category, Subclinic
from cases.services import create_case
from documents.services import upload_document
from users.services import assign_role

User = apps.get_model(settings.AUTH_USER_MODEL)


class DocumentUploadTest(TestCase):
    """Tests for role-based document upload logic."""

    def setUp(self):
        self.subclinic = Subclinic.objects.create(name='civil')
        self.category, _ = Category.objects.get_or_create(name='laboral')

        self.admin = User.objects.create_user(username='admin_doc', password='pass')
        assign_role(self.admin, 'admin')

        self.advisor = User.objects.create_user(username='advisor_doc', password='pass')
        assign_role(self.advisor, 'advisor')

        self.student = User.objects.create_user(username='student_doc', password='pass')
        assign_role(self.student, 'student')

        self.beneficiary = User.objects.create_user(username='beneficiary_doc', password='pass')
        assign_role(self.beneficiary, 'beneficiary')

        self.other_student = User.objects.create_user(username='other_student_doc', password='pass')
        assign_role(self.other_student, 'student')

        # student is creator and therefore auto-assigned
        self.case = create_case(self.student, 'Case for documents', self.category, self.subclinic)

    def _make_file(self, name='test.pdf'):
        return SimpleUploadedFile(name, b'file content', content_type='application/pdf')

    # --- Access control ---

    def test_assigned_user_can_upload_document(self):
        doc = upload_document(
            case=self.case,
            user=self.student,
            file=self._make_file(),
            name='Contract',
            description='Signed contract',
        )
        self.assertIsNotNone(doc.pk)

    def test_admin_can_upload_document_without_being_assigned(self):
        self.assertFalse(self.case.users.filter(pk=self.admin.pk).exists())
        doc = upload_document(
            case=self.case,
            user=self.admin,
            file=self._make_file(),
            name='Admin Doc',
            description='Uploaded by admin',
        )
        self.assertIsNotNone(doc.pk)

    def test_advisor_can_upload_document_without_being_assigned(self):
        self.assertFalse(self.case.users.filter(pk=self.advisor.pk).exists())
        doc = upload_document(
            case=self.case,
            user=self.advisor,
            file=self._make_file(),
            name='Advisor Doc',
            description='Uploaded by advisor',
        )
        self.assertIsNotNone(doc.pk)

    def test_non_assigned_user_cannot_upload_document(self):
        with self.assertRaises(PermissionError):
            upload_document(
                case=self.case,
                user=self.other_student,
                file=self._make_file(),
                name='Unauthorized Doc',
                description='Should not be saved',
            )

    def test_beneficiary_cannot_upload_document(self):
        with self.assertRaises(PermissionError):
            upload_document(
                case=self.case,
                user=self.beneficiary,
                file=self._make_file(),
                name='Beneficiary Doc',
                description='Should not be saved',
            )

    # --- Document field linkage ---

    def test_document_is_linked_to_case(self):
        doc = upload_document(
            case=self.case,
            user=self.student,
            file=self._make_file(),
            name='Linked Doc',
            description='Check case link',
        )
        self.assertEqual(doc.case, self.case)

    def test_document_is_linked_to_uploader(self):
        doc = upload_document(
            case=self.case,
            user=self.student,
            file=self._make_file(),
            name='Linked Doc',
            description='Check uploader link',
        )
        self.assertEqual(doc.uploaded_by, self.student)

    # --- File storage ---

    def test_file_is_saved_correctly(self):
        uploaded_file = self._make_file('report.pdf')
        doc = upload_document(
            case=self.case,
            user=self.student,
            file=uploaded_file,
            name='Report',
            description='Annual report',
        )
        self.assertIn(f'cases/{self.case.pk}/', doc.file.name)
        self.assertIn('report.pdf', doc.file.name)

    # --- CaseLog creation ---

    def test_case_log_is_created_after_upload(self):
        upload_document(
            case=self.case,
            user=self.student,
            file=self._make_file(),
            name='Log Test Doc',
            description='Should trigger a log',
        )
        self.assertTrue(
            self.case.logs.filter(content__icontains='Document uploaded by').exists()
        )
