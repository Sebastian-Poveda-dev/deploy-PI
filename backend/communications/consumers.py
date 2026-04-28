from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.exceptions import ObjectDoesNotExist

from . import services
from .serializers import user_display_name


class ConversationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.group_name = f'conversation_{self.conversation_id}'
        self.user = self.scope.get('user')

        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        try:
            await self.get_conversation()
        except (ObjectDoesNotExist, PermissionError):
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        if content.get('type') != 'message':
            await self.send_json(
                {
                    'type': 'error',
                    'errors': {'type': 'Unsupported WebSocket event type.'},
                }
            )
            return

        try:
            message_payload = await self.create_message(content.get('content'))
        except ValueError as exc:
            await self.send_json(
                {
                    'type': 'error',
                    'errors': {'content': str(exc)},
                }
            )
            return
        except (ObjectDoesNotExist, PermissionError) as exc:
            await self.send_json(
                {
                    'type': 'error',
                    'errors': {'detail': str(exc)},
                }
            )
            return

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat.message',
                'message': message_payload,
            },
        )

    async def chat_message(self, event):
        message = dict(event['message'])
        message['is_current_user'] = message['sender'] == self.user.id
        await self.send_json(
            {
                'type': 'message',
                'message': message,
            }
        )

    @database_sync_to_async
    def get_conversation(self):
        return services.get_conversation_for_participant(self.user, self.conversation_id)

    @database_sync_to_async
    def create_message(self, content):
        message = services.create_message(self.user, self.conversation_id, content)
        return {
            'id': message.id,
            'conversation': message.conversation_id,
            'sender': message.sender_id,
            'sender_username': message.sender.username,
            'sender_name': user_display_name(message.sender),
            'content': message.content,
            'created_at': message.created_at.isoformat(),
            'is_current_user': False,
        }
