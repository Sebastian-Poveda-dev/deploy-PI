from django.apps import apps
from django.conf import settings
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from users.services import assign_role

User = apps.get_model(settings.AUTH_USER_MODEL)


class CommunicationDomainModelTest(TestCase):
    """Red-phase tests for the communication domain model shape."""

    def test_conversation_model_is_registered(self):
        Conversation = apps.get_model('communications', 'Conversation')

        expected_fields = {
            'channel',
            'beneficiary',
            'created_at',
            'updated_at',
        }
        actual_fields = {field.name for field in Conversation._meta.fields}

        self.assertTrue(expected_fields.issubset(actual_fields))
        self.assertTrue(
            {'advisor', 'initiator', 'creator', 'created_by'}.intersection(actual_fields)
        )

    def test_message_model_is_registered(self):
        Message = apps.get_model('communications', 'Message')

        expected_fields = {
            'conversation',
            'sender',
            'content',
            'created_at',
        }
        actual_fields = {field.name for field in Message._meta.fields}

        self.assertTrue(expected_fields.issubset(actual_fields))


class CommunicationApiTest(APITestCase):
    """Red-phase API tests for HTTP-based communication endpoints."""

    conversations_url = '/communications/conversations/'

    def setUp(self):
        self.admin = User.objects.create_user(username='comm_admin', password='pass1234')
        assign_role(self.admin, 'admin')

        self.advisor = User.objects.create_user(username='comm_advisor', password='pass1234')
        assign_role(self.advisor, 'advisor')

        self.professor = User.objects.create_user(username='comm_professor', password='pass1234')
        assign_role(self.professor, 'professor')

        self.student = User.objects.create_user(username='comm_student', password='pass1234')
        assign_role(self.student, 'student')

        self.beneficiary = User.objects.create_user(
            username='comm_beneficiary',
            password='pass1234',
            first_name='Ana',
            last_name='Perez',
            email='ana.beneficiary@example.com',
            phone_number='+573001112233',
        )
        assign_role(self.beneficiary, 'beneficiary')

        self.other_beneficiary = User.objects.create_user(
            username='other_comm_beneficiary',
            password='pass1234',
            email='other.beneficiary@example.com',
            phone_number='+573009998888',
        )
        assign_role(self.other_beneficiary, 'beneficiary')

        self.non_participant = User.objects.create_user(username='comm_non_participant', password='pass1234')
        assign_role(self.non_participant, 'student')

    def _conversation_payload(self, **overrides):
        payload = {
            'channel': 'whatsapp',
            'beneficiary_id': self.beneficiary.id,
        }
        payload.update(overrides)
        return payload

    def _create_conversation(self, user=None, **overrides):
        self.client.force_authenticate(user or self.advisor)
        response = self.client.post(
            self.conversations_url,
            self._conversation_payload(**overrides),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.data

    # --- Authentication ---

    def test_list_conversations_requires_authentication(self):
        response = self.client.get(self.conversations_url)

        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_create_conversation_requires_authentication(self):
        response = self.client.post(
            self.conversations_url,
            self._conversation_payload(),
            format='json',
        )

        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_list_conversations_returns_only_authenticated_users_conversations(self):
        conversation = self._create_conversation(self.advisor)
        self.client.force_authenticate(self.advisor)

        response = self.client.get(self.conversations_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item['id'] for item in response.data]
        self.assertIn(conversation['id'], ids)

    # --- Conversation creation ---

    def test_advisor_can_start_conversation_with_beneficiary(self):
        self.client.force_authenticate(self.advisor)

        response = self.client.post(
            self.conversations_url,
            self._conversation_payload(channel='whatsapp'),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['channel'], 'whatsapp')
        self.assertEqual(response.data['beneficiary_name'], 'Ana Perez')

    def test_admin_professor_and_student_can_start_conversations_with_beneficiaries(self):
        allowed_users = [self.admin, self.professor, self.student]

        for user in allowed_users:
            self.client.force_authenticate(user)
            response = self.client.post(
                self.conversations_url,
                self._conversation_payload(channel='email'),
                format='json',
            )

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_beneficiary_cannot_start_new_conversation(self):
        self.client.force_authenticate(self.beneficiary)

        response = self.client.post(
            self.conversations_url,
            self._conversation_payload(beneficiary_id=self.other_beneficiary.id),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_target_user_must_be_beneficiary(self):
        self.client.force_authenticate(self.advisor)

        response = self.client.post(
            self.conversations_url,
            self._conversation_payload(beneficiary_id=self.student.id),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_channel_returns_400(self):
        self.client.force_authenticate(self.advisor)

        response = self.client.post(
            self.conversations_url,
            self._conversation_payload(channel='sms'),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Channel response data ---

    def test_whatsapp_conversation_response_includes_external_url(self):
        self.client.force_authenticate(self.advisor)

        response = self.client.post(
            self.conversations_url,
            self._conversation_payload(channel='whatsapp'),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['channel'], 'whatsapp')
        self.assertEqual(response.data['beneficiary_name'], 'Ana Perez')
        self.assertEqual(response.data['beneficiary_email'], 'ana.beneficiary@example.com')
        self.assertEqual(response.data['beneficiary_phone_number'], '+573001112233')
        self.assertEqual(response.data['external_url'], 'https://wa.me/573001112233')

    def test_email_conversation_response_includes_external_url(self):
        self.client.force_authenticate(self.advisor)

        response = self.client.post(
            self.conversations_url,
            self._conversation_payload(channel='email'),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['channel'], 'email')
        self.assertEqual(response.data['external_url'], 'mailto:ana.beneficiary@example.com')

    def test_phone_conversation_response_includes_external_url(self):
        self.client.force_authenticate(self.advisor)

        response = self.client.post(
            self.conversations_url,
            self._conversation_payload(channel='phone'),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['channel'], 'phone')
        self.assertEqual(response.data['external_url'], 'tel:+573001112233')

    # --- Messages ---

    def test_get_messages_requires_authentication(self):
        conversation = self._create_conversation(self.advisor)
        self.client.force_authenticate(user=None)

        response = self.client.get(f'/communications/conversations/{conversation["id"]}/messages/')

        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_participant_can_view_messages(self):
        conversation = self._create_conversation(self.advisor)
        self.client.force_authenticate(self.beneficiary)

        response = self.client.get(f'/communications/conversations/{conversation["id"]}/messages/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_non_participant_cannot_view_messages(self):
        conversation = self._create_conversation(self.advisor)
        self.client.force_authenticate(self.non_participant)

        response = self.client.get(f'/communications/conversations/{conversation["id"]}/messages/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_participant_can_send_message(self):
        conversation = self._create_conversation(self.advisor)
        self.client.force_authenticate(self.advisor)

        response = self.client.post(
            f'/communications/conversations/{conversation["id"]}/messages/',
            {'content': 'Please confirm the appointment time.'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Please confirm the appointment time.')
        self.assertEqual(response.data['sender']['id'], self.advisor.id)

    def test_beneficiary_participant_can_reply_to_message(self):
        conversation = self._create_conversation(self.advisor)
        self.client.force_authenticate(self.beneficiary)

        response = self.client.post(
            f'/communications/conversations/{conversation["id"]}/messages/',
            {'content': 'Confirmed, thank you.'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['sender']['id'], self.beneficiary.id)

    def test_non_participant_cannot_send_message(self):
        conversation = self._create_conversation(self.advisor)
        self.client.force_authenticate(self.non_participant)

        response = self.client.post(
            f'/communications/conversations/{conversation["id"]}/messages/',
            {'content': 'I should not be here.'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_empty_message_content_returns_400(self):
        conversation = self._create_conversation(self.advisor)
        self.client.force_authenticate(self.advisor)

        response = self.client.post(
            f'/communications/conversations/{conversation["id"]}/messages/',
            {'content': '   '},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
