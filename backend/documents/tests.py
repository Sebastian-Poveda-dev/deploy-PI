from datetime import timedelta

from django.http import FileResponse
from django.test import TestCase, override_settings
from django.conf import settings
from django.apps import apps
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from cases.models import Category, Subclinic
from cases.services import create_case
from documents.models import Document
from documents.test_storage import TestMemoryStorage
from documents.services import upload_document, get_case_documents, download_document
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
        self.case = create_case(self.student, 'Case for documents', self.category, self.subclinic, beneficiary=self.beneficiary)

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
        self.assertTrue(doc.file.name.startswith(f'cases/{self.case.pk}/'))
        self.assertIn('report', doc.file.name)
        self.assertTrue(doc.file.name.endswith('.pdf'))

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


class GetCaseDocumentsTest(TestCase):
    """Tests for role-based document listing logic."""

    def setUp(self):
        self.subclinic = Subclinic.objects.create(name='family')
        self.category, _ = Category.objects.get_or_create(name='laboral')

        self.admin = User.objects.create_user(username='admin_list', password='pass')
        assign_role(self.admin, 'admin')

        self.advisor = User.objects.create_user(username='advisor_list', password='pass')
        assign_role(self.advisor, 'advisor')

        self.student = User.objects.create_user(username='student_list', password='pass')
        assign_role(self.student, 'student')

        self.beneficiary = User.objects.create_user(username='beneficiary_list', password='pass')
        assign_role(self.beneficiary, 'beneficiary')

        self.other_student = User.objects.create_user(username='other_student_list', password='pass')
        assign_role(self.other_student, 'student')

        # student is creator and therefore auto-assigned
        self.case = create_case(self.student, 'Case for listing docs', self.category, self.subclinic, beneficiary=self.beneficiary)
        self.other_case = create_case(self.student, 'Another case', self.category, self.subclinic, beneficiary=self.beneficiary)

    def _upload(self, name, case=None):
        return upload_document(
            case=case or self.case,
            user=self.student,
            file=SimpleUploadedFile(f'{name}.pdf', b'content', content_type='application/pdf'),
            name=name,
            description=f'Description for {name}',
        )

    # --- Access control ---

    def test_assigned_user_can_retrieve_documents(self):
        self._upload('doc1')
        docs = get_case_documents(case=self.case, user=self.student)
        self.assertGreaterEqual(len(list(docs)), 1)

    def test_admin_can_retrieve_documents_without_being_assigned(self):
        self.assertFalse(self.case.users.filter(pk=self.admin.pk).exists())
        self._upload('doc_admin')
        docs = get_case_documents(case=self.case, user=self.admin)
        self.assertGreaterEqual(len(list(docs)), 1)

    def test_advisor_can_retrieve_documents_without_being_assigned(self):
        self.assertFalse(self.case.users.filter(pk=self.advisor.pk).exists())
        self._upload('doc_advisor')
        docs = get_case_documents(case=self.case, user=self.advisor)
        self.assertGreaterEqual(len(list(docs)), 1)

    def test_non_assigned_user_cannot_retrieve_documents(self):
        with self.assertRaises(PermissionError):
            get_case_documents(case=self.case, user=self.other_student)

    def test_beneficiary_cannot_retrieve_documents(self):
        with self.assertRaises(PermissionError):
            get_case_documents(case=self.case, user=self.beneficiary)

    # --- Correct documents returned ---

    def test_only_documents_belonging_to_case_are_returned(self):
        doc_this = self._upload('belongs_here', case=self.case)
        self._upload('belongs_elsewhere', case=self.other_case)

        docs = list(get_case_documents(case=self.case, user=self.student))
        pks = [d.pk for d in docs]

        self.assertIn(doc_this.pk, pks)
        for d in docs:
            self.assertEqual(d.case_id, self.case.pk)

    def test_empty_list_returned_when_case_has_no_documents(self):
        docs = list(get_case_documents(case=self.case, user=self.student))
        self.assertEqual(docs, [])


class DownloadDocumentTest(TestCase):
    """Tests for role-based document download logic."""

    def setUp(self):
        self.subclinic = Subclinic.objects.create(name='penal')
        self.category, _ = Category.objects.get_or_create(name='laboral')

        self.admin = User.objects.create_user(username='admin_dl', password='pass')
        assign_role(self.admin, 'admin')

        self.advisor = User.objects.create_user(username='advisor_dl', password='pass')
        assign_role(self.advisor, 'advisor')

        self.student = User.objects.create_user(username='student_dl', password='pass')
        assign_role(self.student, 'student')

        self.beneficiary = User.objects.create_user(username='beneficiary_dl', password='pass')
        assign_role(self.beneficiary, 'beneficiary')

        self.other_student = User.objects.create_user(username='other_student_dl', password='pass')
        assign_role(self.other_student, 'student')

        self.case = create_case(self.student, 'Case for download', self.category, self.subclinic, beneficiary=self.beneficiary)

        self.file_content = b'test file content for download'
        self.doc = upload_document(
            case=self.case,
            user=self.student,
            file=SimpleUploadedFile('contract.pdf', self.file_content, content_type='application/pdf'),
            name='Contract',
            description='A test contract',
        )

    # --- Access control ---

    def test_assigned_user_can_download_document(self):
        response = download_document(self.doc.pk, self.student)
        self.assertIsNotNone(response)
        response.close()

    def test_admin_can_download_document_without_being_assigned(self):
        self.assertFalse(self.case.users.filter(pk=self.admin.pk).exists())
        response = download_document(self.doc.pk, self.admin)
        self.assertIsNotNone(response)
        response.close()

    def test_advisor_can_download_document_without_being_assigned(self):
        self.assertFalse(self.case.users.filter(pk=self.advisor.pk).exists())
        response = download_document(self.doc.pk, self.advisor)
        self.assertIsNotNone(response)
        response.close()

    def test_non_assigned_user_cannot_download_document(self):
        with self.assertRaises(PermissionError):
            download_document(self.doc.pk, self.other_student)

    def test_beneficiary_cannot_download_document(self):
        with self.assertRaises(PermissionError):
            download_document(self.doc.pk, self.beneficiary)

    # --- File response ---

    def test_download_returns_file_response(self):
        from django.http import FileResponse
        response = download_document(self.doc.pk, self.student)
        self.assertIsInstance(response, FileResponse)
        response.close()

    def test_correct_file_content_is_returned(self):
        response = download_document(self.doc.pk, self.student)
        content = b''.join(response.streaming_content)
        self.assertEqual(content, self.file_content)

    # --- Error handling ---

    def test_nonexistent_document_raises_error(self):
        with self.assertRaises(Document.DoesNotExist):
            download_document(99999, self.student)


class DocumentApiBaseTest(APITestCase):
    def setUp(self):
        super().setUp()
        TestMemoryStorage.clear()
        self._storage_override = override_settings(
            STORAGES={
                'default': {'BACKEND': 'documents.test_storage.TestMemoryStorage'},
                'staticfiles': {
                    'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
                },
            }
        )
        self._storage_override.enable()
        self.addCleanup(self._storage_override.disable)
        self.addCleanup(TestMemoryStorage.clear)

        self.subclinic = Subclinic.objects.create(name=self._name('api_subclinic'))
        self.category, _ = Category.objects.get_or_create(name=self._name('api_category'))

        self.admin = User.objects.create_user(username=self._name('admin'), password='pass')
        assign_role(self.admin, 'admin')

        self.advisor = User.objects.create_user(username=self._name('advisor'), password='pass')
        assign_role(self.advisor, 'advisor')

        self.student = User.objects.create_user(username=self._name('student'), password='pass')
        assign_role(self.student, 'student')

        self.other_student = User.objects.create_user(
            username=self._name('other_student'),
            password='pass',
        )
        assign_role(self.other_student, 'student')

        self.beneficiary = User.objects.create_user(
            username=self._name('beneficiary'),
            password='pass',
        )
        assign_role(self.beneficiary, 'beneficiary')

        self.case = create_case(self.student, 'Documents API case', self.category, self.subclinic, beneficiary=self.beneficiary)
        self.other_case = create_case(
            self.student,
            'Other documents API case',
            self.category,
            self.subclinic,
            beneficiary=self.beneficiary,
        )

    def _name(self, prefix):
        return f'{prefix}_{self.__class__.__name__.lower()}'

    def _file(self, name='evidence.pdf', content=b'document content'):
        return SimpleUploadedFile(name, content, content_type='application/pdf')

    def _upload_document(self, *, case=None, user=None, name='Existing Doc', content=b'existing doc'):
        return upload_document(
            case=case or self.case,
            user=user or self.student,
            file=self._file(f'{name.lower().replace(" ", "_")}.pdf', content=content),
            name=name,
            description=f'Description for {name}',
        )


class DocumentUploadApiTest(DocumentApiBaseTest):
    def test_assigned_user_can_upload_document(self):
        self.client.force_authenticate(self.student)

        response = self.client.post(
            f'/cases/{self.case.id}/documents/',
            {
                'name': 'Contract',
                'description': 'Signed contract',
                'expiration_date': '2030-01-01T00:00:00Z',
                'file': self._file('contract.pdf', b'contract content'),
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertSetEqual(
            set(response.data.keys()),
            {'id', 'name', 'description', 'uploaded_at', 'expiration_date'},
        )

        document = Document.objects.get(pk=response.data['id'])
        self.assertEqual(document.case, self.case)
        self.assertEqual(document.uploaded_by, self.student)
        self.assertTrue(document.file.name.startswith(f'cases/{self.case.pk}/'))
        self.assertIn('contract', document.file.name)
        self.assertEqual(document.file.read(), b'contract content')
        document.file.close()

    def test_admin_can_upload_document(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            f'/cases/{self.case.id}/documents/',
            {
                'name': 'Admin Contract',
                'description': 'Uploaded by admin',
                'file': self._file('admin-contract.pdf'),
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_advisor_can_upload_document(self):
        self.client.force_authenticate(self.advisor)

        response = self.client.post(
            f'/cases/{self.case.id}/documents/',
            {
                'name': 'Advisor Contract',
                'description': 'Uploaded by advisor',
                'file': self._file('advisor-contract.pdf'),
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_non_assigned_user_cannot_upload_document(self):
        self.client.force_authenticate(self.other_student)

        response = self.client.post(
            f'/cases/{self.case.id}/documents/',
            {
                'name': 'Unauthorized',
                'description': 'Should fail',
                'file': self._file('unauthorized.pdf'),
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_beneficiary_cannot_upload_document(self):
        self.client.force_authenticate(self.beneficiary)

        response = self.client.post(
            f'/cases/{self.case.id}/documents/',
            {
                'name': 'Beneficiary Upload',
                'description': 'Should fail',
                'file': self._file('beneficiary.pdf'),
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DocumentListApiTest(DocumentApiBaseTest):
    def setUp(self):
        super().setUp()
        self.case_document = self._upload_document(case=self.case, name='Case Document')
        self._upload_document(case=self.other_case, name='Other Case Document')

    def test_assigned_user_can_view_documents(self):
        self.client.force_authenticate(self.student)

        response = self.client.get(f'/cases/{self.case.id}/documents/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_admin_can_view_documents(self):
        self.client.force_authenticate(self.admin)

        response = self.client.get(f'/cases/{self.case.id}/documents/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_advisor_can_view_documents(self):
        self.client.force_authenticate(self.advisor)

        response = self.client.get(f'/cases/{self.case.id}/documents/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_assigned_user_cannot_view_documents(self):
        self.client.force_authenticate(self.other_student)

        response = self.client.get(f'/cases/{self.case.id}/documents/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_beneficiary_cannot_view_documents(self):
        self.client.force_authenticate(self.beneficiary)

        response = self.client.get(f'/cases/{self.case.id}/documents/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_only_documents_for_the_case_are_returned(self):
        self.client.force_authenticate(self.student)

        response = self.client.get(f'/cases/{self.case.id}/documents/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.case_document.id)
        self.assertEqual(response.data[0]['name'], self.case_document.name)
        self.assertSetEqual(
            set(response.data[0].keys()),
            {'id', 'name', 'description', 'uploaded_at', 'expiration_date'},
        )


class DocumentDownloadApiTest(DocumentApiBaseTest):
    def setUp(self):
        super().setUp()
        self.file_content = b'test file content for api download'
        self.document = self._upload_document(
            case=self.case,
            name='Downloadable Doc',
            content=self.file_content,
        )

    def test_assigned_user_can_download_document(self):
        self.client.force_authenticate(self.student)

        response = self.client.get(f'/documents/{self.document.id}/download/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_download_document(self):
        self.client.force_authenticate(self.admin)

        response = self.client.get(f'/documents/{self.document.id}/download/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_advisor_can_download_document(self):
        self.client.force_authenticate(self.advisor)

        response = self.client.get(f'/documents/{self.document.id}/download/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_assigned_user_cannot_download_document(self):
        self.client.force_authenticate(self.other_student)

        response = self.client.get(f'/documents/{self.document.id}/download/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_beneficiary_cannot_download_document(self):
        self.client.force_authenticate(self.beneficiary)

        response = self.client.get(f'/documents/{self.document.id}/download/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_fileresponse_is_returned_correctly(self):
        self.client.force_authenticate(self.student)

        response = self.client.get(f'/documents/{self.document.id}/download/')

        self.assertIsInstance(response, FileResponse)
        self.assertEqual(response.get('Content-Type'), 'application/pdf')
        self.assertIn('attachment;', response.get('Content-Disposition', ''))

    def test_correct_file_is_returned(self):
        self.client.force_authenticate(self.student)

        response = self.client.get(f'/documents/{self.document.id}/download/')

        content = b''.join(response.streaming_content)
        self.assertEqual(content, self.file_content)


class DocumentExpirationVerificationTest(TestCase):
    """Red-phase tests for expiring and expired document notifications."""

    def setUp(self):
        self.subclinic = Subclinic.objects.create(name='expiration_subclinic')
        self.category, _ = Category.objects.get_or_create(name='expiration_category')

        self.student = User.objects.create_user(username='student_expiration', password='pass')
        assign_role(self.student, 'student')

        self.beneficiary = User.objects.create_user(
            username='beneficiary_expiration',
            password='pass',
        )
        assign_role(self.beneficiary, 'beneficiary')

        self.case = create_case(
            self.student,
            'Case with expiring documents',
            self.category,
            self.subclinic,
            beneficiary=self.beneficiary,
        )

    def _upload_document(self, *, name, expiration_date=None):
        return upload_document(
            case=self.case,
            user=self.student,
            file=SimpleUploadedFile(
                f'{name.lower().replace(" ", "_")}.pdf',
                b'expiration content',
                content_type='application/pdf',
            ),
            name=name,
            description=f'Document {name}',
            expiration_date=expiration_date,
        )

    def test_document_within_alert_range_creates_notification_for_assigned_student(self):
        from documents.services import verify_document_expirations

        today = timezone.now().date()
        document = self._upload_document(
            name='Power of Attorney',
            expiration_date=today + timedelta(days=2),
        )

        created_notifications = verify_document_expirations(today=today, alert_days=3)
        Notification = apps.get_model('documents', 'DocumentExpirationNotification')
        notification = Notification.objects.get(document=document, recipient=self.student)

        self.assertEqual(len(created_notifications), 1)
        self.assertEqual(notification.event_type, 'upcoming')
        self.assertIn(document.name, notification.message)
        self.assertIn(str(document.expiration_date), notification.message)

    def test_expired_document_is_marked_and_generates_expired_notification(self):
        from documents.services import verify_document_expirations

        today = timezone.now().date()
        document = self._upload_document(
            name='Expired Contract',
            expiration_date=today - timedelta(days=1),
        )

        created_notifications = verify_document_expirations(today=today, alert_days=3)
        Notification = apps.get_model('documents', 'DocumentExpirationNotification')
        notification = Notification.objects.get(document=document, recipient=self.student)
        document.refresh_from_db()

        self.assertEqual(len(created_notifications), 1)
        self.assertEqual(notification.event_type, 'expired')
        self.assertTrue(document.is_expired)

    def test_verification_does_not_generate_duplicate_notifications_for_same_event(self):
        from documents.services import verify_document_expirations

        today = timezone.now().date()
        document = self._upload_document(
            name='Upcoming Evidence',
            expiration_date=today + timedelta(days=1),
        )

        first_run = verify_document_expirations(today=today, alert_days=3)
        second_run = verify_document_expirations(today=today, alert_days=3)
        Notification = apps.get_model('documents', 'DocumentExpirationNotification')

        self.assertEqual(len(first_run), 1)
        self.assertEqual(second_run, [])
        self.assertEqual(
            Notification.objects.filter(
                document=document,
                recipient=self.student,
                event_type='upcoming',
            ).count(),
            1,
        )

    def test_document_without_expiration_date_is_ignored(self):
        from documents.services import verify_document_expirations

        today = timezone.now().date()
        document = self._upload_document(name='Open Document')

        created_notifications = verify_document_expirations(today=today, alert_days=3)
        Notification = apps.get_model('documents', 'DocumentExpirationNotification')

        self.assertEqual(created_notifications, [])
        self.assertFalse(
            Notification.objects.filter(document=document, recipient=self.student).exists()
        )

    def test_alert_range_can_be_configured(self):
        from documents.services import verify_document_expirations

        today = timezone.now().date()
        document = self._upload_document(
            name='Five Day Notice',
            expiration_date=today + timedelta(days=5),
        )
        Notification = apps.get_model('documents', 'DocumentExpirationNotification')

        no_alert_notifications = verify_document_expirations(today=today, alert_days=3)
        alert_notifications = verify_document_expirations(today=today, alert_days=5)

        self.assertEqual(no_alert_notifications, [])
        self.assertEqual(len(alert_notifications), 1)
        self.assertTrue(
            Notification.objects.filter(
                document=document,
                recipient=self.student,
                event_type='upcoming',
            ).exists()
        )

