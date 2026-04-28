import unittest

from asgiref.sync import sync_to_async
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import TestCase, TransactionTestCase
from rest_framework import status
from rest_framework.test import APITestCase

from users.services import assign_role

User = apps.get_model(settings.AUTH_USER_MODEL)


def user_summary_keys():
    return {'id', 'username', 'first_name', 'last_name'}


class CommunicationTestUsersMixin:
    def create_user(self, username, role='student', **overrides):
        defaults = {
            'password': 'pass1234',
            'first_name': username.replace('_', ' ').title(),
            'last_name': 'User',
            'email': f'{username}@example.com',
        }
        defaults.update(overrides)
        user = User.objects.create_user(username=username, **defaults)
        Group.objects.get_or_create(name=role)
        assign_role(user, role)
        return user


class CommunicationDomainModelTest(CommunicationTestUsersMixin, TestCase):
    """Red-phase tests for the internal chat domain model shape."""

    def setUp(self):
        self.creator = self.create_user('chat_creator', 'advisor')
        self.student = self.create_user('chat_student', 'student')

    def test_conversation_model_supports_internal_participant_chat(self):
        Conversation = apps.get_model('communications', 'Conversation')

        field_names = {field.name for field in Conversation._meta.get_fields()}

        self.assertIn('creator', field_names)
        self.assertIn('participants', field_names)
        self.assertIn('created_at', field_names)
        self.assertIn('updated_at', field_names)
        self.assertTrue({'title', 'name'}.intersection(field_names))

    def test_conversation_model_has_no_external_channel_fields(self):
        Conversation = apps.get_model('communications', 'Conversation')

        field_names = {field.name for field in Conversation._meta.get_fields()}

        self.assertNotIn('channel', field_names)
        self.assertNotIn('beneficiary', field_names)
        self.assertFalse(hasattr(Conversation, 'CHANNEL_CHOICES'))
        self.assertFalse(hasattr(Conversation, 'CHANNEL_WHATSAPP'))
        self.assertFalse(hasattr(Conversation, 'CHANNEL_EMAIL'))
        self.assertFalse(hasattr(Conversation, 'CHANNEL_PHONE'))

    def test_conversation_can_be_created_with_creator_and_participants(self):
        Conversation = apps.get_model('communications', 'Conversation')

        conversation = Conversation.objects.create(
            title='Civil clinic team',
            creator=self.creator,
        )
        conversation.participants.add(self.creator, self.student)

        self.assertEqual(conversation.creator, self.creator)
        self.assertTrue(conversation.participants.filter(pk=self.creator.pk).exists())
        self.assertTrue(conversation.participants.filter(pk=self.student.pk).exists())
        self.assertIsNotNone(conversation.created_at)
        self.assertIsNotNone(conversation.updated_at)

    def test_message_model_supports_internal_messages(self):
        Message = apps.get_model('communications', 'Message')

        field_names = {field.name for field in Message._meta.fields}

        self.assertTrue({'conversation', 'sender', 'content', 'created_at'}.issubset(field_names))

    def test_empty_message_is_rejected_by_model_validation(self):
        Conversation = apps.get_model('communications', 'Conversation')
        Message = apps.get_model('communications', 'Message')
        conversation = Conversation.objects.create(title='Validation chat', creator=self.creator)
        conversation.participants.add(self.creator, self.student)

        message = Message(conversation=conversation, sender=self.creator, content='   ')

        with self.assertRaises(ValidationError):
            message.full_clean()


class CommunicationServiceTest(CommunicationTestUsersMixin, TestCase):
    """Red-phase tests that business rules live behind service functions."""

    def setUp(self):
        self.creator = self.create_user('svc_creator', 'advisor')
        self.student = self.create_user('svc_student', 'student')
        self.professor = self.create_user('svc_professor', 'professor')
        self.inactive_user = self.create_user('svc_inactive', 'student', is_active=False)
        self.outsider = self.create_user('svc_outsider', 'student')

    def test_service_creates_internal_conversation_with_creator_as_participant(self):
        from communications import services

        conversation = services.create_conversation(
            creator=self.creator,
            participant_ids=[self.student.id, self.professor.id],
            title='Service chat',
        )

        participant_ids = set(conversation.participants.values_list('id', flat=True))
        self.assertEqual(conversation.creator, self.creator)
        self.assertSetEqual(participant_ids, {self.creator.id, self.student.id, self.professor.id})

    def test_service_rejects_conversation_without_other_participants(self):
        from communications import services

        with self.assertRaises(ValueError):
            services.create_conversation(
                creator=self.creator,
                participant_ids=[],
                title='Lonely chat',
            )

    def test_service_rejects_inactive_participants(self):
        from communications import services

        with self.assertRaises(ValueError):
            services.create_conversation(
                creator=self.creator,
                participant_ids=[self.inactive_user.id],
                title='Inactive user chat',
            )

    def test_service_lists_only_conversations_where_user_is_participant(self):
        from communications import services

        visible = services.create_conversation(
            creator=self.creator,
            participant_ids=[self.student.id],
            title='Visible chat',
        )
        services.create_conversation(
            creator=self.professor,
            participant_ids=[self.outsider.id],
            title='Hidden chat',
        )

        conversations = services.list_conversations_for_user(self.student)

        self.assertIn(visible, conversations)
        self.assertTrue(all(c.participants.filter(pk=self.student.pk).exists() for c in conversations))

    def test_service_creates_message_for_participant(self):
        from communications import services

        conversation = services.create_conversation(
            creator=self.creator,
            participant_ids=[self.student.id],
            title='Message chat',
        )

        message = services.create_message(self.student, conversation.id, 'I reviewed the draft.')

        self.assertEqual(message.conversation, conversation)
        self.assertEqual(message.sender, self.student)
        self.assertEqual(message.content, 'I reviewed the draft.')

    def test_service_rejects_message_from_non_participant(self):
        from communications import services

        conversation = services.create_conversation(
            creator=self.creator,
            participant_ids=[self.student.id],
            title='Private chat',
        )

        with self.assertRaises(PermissionError):
            services.create_message(self.outsider, conversation.id, 'I should not be able to post here.')

    def test_service_rejects_empty_message(self):
        from communications import services

        conversation = services.create_conversation(
            creator=self.creator,
            participant_ids=[self.student.id],
            title='Empty message chat',
        )

        with self.assertRaises(ValueError):
            services.create_message(self.creator, conversation.id, '   ')


class CommunicationApiTest(CommunicationTestUsersMixin, APITestCase):
    """Red-phase REST API tests for internal chat endpoints."""

    conversations_url = '/communications/conversations/'
    users_url = '/communications/users/'

    def setUp(self):
        self.admin = self.create_user('api_admin', 'admin')
        self.advisor = self.create_user('api_advisor', 'advisor')
        self.professor = self.create_user('api_professor', 'professor')
        self.student = self.create_user('api_student', 'student')
        self.beneficiary = self.create_user('api_beneficiary', 'beneficiary')
        self.other_student = self.create_user('api_other_student', 'student')
        self.inactive_user = self.create_user('api_inactive', 'student', is_active=False)

    def conversation_payload(self, **overrides):
        payload = {
            'title': 'Internal case team',
            'participant_ids': [self.student.id, self.professor.id],
        }
        payload.update(overrides)
        return payload

    def create_conversation(self, creator=None, **overrides):
        self.client.force_authenticate(creator or self.advisor)
        response = self.client.post(
            self.conversations_url,
            self.conversation_payload(**overrides),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.data

    def messages_url(self, conversation_id):
        return f'/communications/conversations/{conversation_id}/messages/'

    def test_list_conversations_requires_authentication(self):
        response = self.client.get(self.conversations_url)

        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_create_conversation_requires_authentication(self):
        response = self.client.post(self.conversations_url, self.conversation_payload(), format='json')

        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_messages_require_authentication(self):
        conversation = self.create_conversation(self.advisor)
        self.client.force_authenticate(user=None)

        get_response = self.client.get(self.messages_url(conversation['id']))
        post_response = self.client.post(
            self.messages_url(conversation['id']),
            {'content': 'Unauthenticated message'},
            format='json',
        )

        self.assertIn(get_response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))
        self.assertIn(post_response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_authenticated_user_can_create_internal_conversation_with_active_users(self):
        self.client.force_authenticate(self.advisor)

        response = self.client.post(
            self.conversations_url,
            self.conversation_payload(),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Internal case team')
        self.assertNotIn('channel', response.data)
        self.assertNotIn('external_url', response.data)
        participant_ids = {participant['id'] for participant in response.data['participants']}
        self.assertSetEqual(participant_ids, {self.advisor.id, self.student.id, self.professor.id})

    def test_conversation_creation_rejects_inactive_users(self):
        self.client.force_authenticate(self.advisor)

        response = self.client.post(
            self.conversations_url,
            self.conversation_payload(participant_ids=[self.inactive_user.id]),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_conversation_creation_rejects_external_channel_payload(self):
        self.client.force_authenticate(self.advisor)

        response = self.client.post(
            self.conversations_url,
            self.conversation_payload(channel='whatsapp', beneficiary_id=self.beneficiary.id),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_list_only_participant_conversations(self):
        visible = self.create_conversation(self.advisor, participant_ids=[self.student.id])
        hidden = self.create_conversation(self.professor, participant_ids=[self.other_student.id])
        self.client.force_authenticate(self.student)

        response = self.client.get(self.conversations_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        conversation_ids = {conversation['id'] for conversation in response.data}
        self.assertIn(visible['id'], conversation_ids)
        self.assertNotIn(hidden['id'], conversation_ids)

    def test_conversation_response_includes_participants_and_last_message(self):
        conversation = self.create_conversation(self.advisor, participant_ids=[self.student.id])
        self.client.force_authenticate(self.student)
        self.client.post(
            self.messages_url(conversation['id']),
            {'content': 'Latest update from the student.'},
            format='json',
        )

        response = self.client.get(self.conversations_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = next(c for c in response.data if c['id'] == conversation['id'])
        self.assertIn('participants', item)
        self.assertIn('last_message', item)
        self.assertEqual(item['last_message']['content'], 'Latest update from the student.')
        self.assertTrue(user_summary_keys().issubset(item['participants'][0].keys()))
        self.assertTrue({'id', 'content', 'sender', 'created_at'}.issubset(item['last_message'].keys()))

    def test_participant_can_list_messages(self):
        conversation = self.create_conversation(self.advisor, participant_ids=[self.student.id])
        self.client.force_authenticate(self.advisor)
        self.client.post(
            self.messages_url(conversation['id']),
            {'content': 'Please review the case notes.'},
            format='json',
        )
        self.client.force_authenticate(self.student)

        response = self.client.get(self.messages_url(conversation['id']))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['content'], 'Please review the case notes.')
        self.assertIn('sender', response.data[0])
        self.assertIn('is_current_user', response.data[0])
        self.assertFalse(response.data[0]['is_current_user'])

    def test_participant_can_create_message(self):
        conversation = self.create_conversation(self.advisor, participant_ids=[self.student.id])
        self.client.force_authenticate(self.student)

        response = self.client.post(
            self.messages_url(conversation['id']),
            {'content': 'I can attend the meeting.'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'I can attend the meeting.')
        self.assertEqual(response.data['sender']['id'], self.student.id)
        self.assertTrue(response.data['is_current_user'])

    def test_non_participant_cannot_list_or_create_messages(self):
        conversation = self.create_conversation(self.advisor, participant_ids=[self.student.id])
        self.client.force_authenticate(self.other_student)

        get_response = self.client.get(self.messages_url(conversation['id']))
        post_response = self.client.post(
            self.messages_url(conversation['id']),
            {'content': 'I should not be here.'},
            format='json',
        )

        self.assertEqual(get_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(post_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_empty_message_content_returns_400(self):
        conversation = self.create_conversation(self.advisor, participant_ids=[self.student.id])
        self.client.force_authenticate(self.advisor)

        response = self.client.post(
            self.messages_url(conversation['id']),
            {'content': '   '},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authenticated_users_endpoint_lists_active_internal_users(self):
        self.client.force_authenticate(self.advisor)

        response = self.client.get(self.users_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_ids = {user['id'] for user in response.data}
        self.assertIn(self.student.id, user_ids)
        self.assertIn(self.beneficiary.id, user_ids)
        self.assertNotIn(self.inactive_user.id, user_ids)
        self.assertTrue(user_summary_keys().issubset(response.data[0].keys()))


@unittest.skip('WebSocket chat will be implemented in the Channels phase.')
class CommunicationWebSocketTest(CommunicationTestUsersMixin, TransactionTestCase):
    """Red-phase WebSocket tests for real-time internal chat delivery."""

    reset_sequences = True

    def setUp(self):
        self.advisor = self.create_user('ws_advisor', 'advisor')
        self.student = self.create_user('ws_student', 'student')
        self.other_student = self.create_user('ws_other_student', 'student')
        self.conversation = self.create_conversation()

    def create_conversation(self):
        Conversation = apps.get_model('communications', 'Conversation')
        conversation = Conversation.objects.create(
            title='Socket chat',
            creator=self.advisor,
        )
        conversation.participants.add(self.advisor, self.student)
        return conversation

    async def connect(self, user):
        from channels.testing import WebsocketCommunicator
        from lawclinic.asgi import application

        communicator = WebsocketCommunicator(
            application,
            f'/ws/communications/conversations/{self.conversation.id}/',
        )
        communicator.scope['user'] = user
        connected, _ = await communicator.connect()
        return communicator, connected

    async def test_authenticated_participant_can_connect(self):
        communicator, connected = await self.connect(self.advisor)
        try:
            self.assertTrue(connected)
        finally:
            await communicator.disconnect()

    async def test_non_participant_cannot_connect(self):
        communicator, connected = await self.connect(self.other_student)
        try:
            self.assertFalse(connected)
        finally:
            await communicator.disconnect()

    async def test_websocket_message_is_persisted_and_broadcast(self):
        sender, sender_connected = await self.connect(self.advisor)
        recipient, recipient_connected = await self.connect(self.student)
        try:
            self.assertTrue(sender_connected)
            self.assertTrue(recipient_connected)

            await sender.send_json_to({'content': 'Live update for the team.'})
            event = await recipient.receive_json_from()

            self.assertEqual(event['type'], 'message.created')
            self.assertEqual(event['message']['content'], 'Live update for the team.')
            self.assertEqual(event['message']['sender']['id'], self.advisor.id)
            self.assertFalse(event['message']['is_current_user'])

            Message = apps.get_model('communications', 'Message')
            exists = await sync_to_async(
                Message.objects.filter(
                    conversation=self.conversation,
                    sender=self.advisor,
                    content='Live update for the team.',
                ).exists
            )()
            self.assertTrue(exists)
        finally:
            await sender.disconnect()
            await recipient.disconnect()

    async def test_empty_websocket_message_is_rejected(self):
        communicator, connected = await self.connect(self.advisor)
        try:
            self.assertTrue(connected)

            await communicator.send_json_to({'content': '   '})
            event = await communicator.receive_json_from()

            self.assertEqual(event['type'], 'error')
            self.assertIn('content', event['errors'])
        finally:
            await communicator.disconnect()
