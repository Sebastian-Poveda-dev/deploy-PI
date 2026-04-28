from rest_framework import serializers

from .models import Conversation, Message
from .services import get_user_role


def user_display_name(user):
    full_name = f'{user.first_name} {user.last_name}'.strip()
    return full_name or user.username


def user_summary(user):
    return {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'full_name': user_display_name(user),
        'name': user_display_name(user),
        'role': get_user_role(user),
    }


class ChatUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    full_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return user_display_name(obj)

    def get_role(self, obj):
        return get_user_role(obj)


class ConversationCreateSerializer(serializers.Serializer):
    participant_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
    )
    title = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)

    def validate(self, attrs):
        unsupported_fields = {'channel', 'beneficiary_id', 'external_url'}.intersection(self.initial_data)
        if unsupported_fields:
            field_list = ', '.join(sorted(unsupported_fields))
            raise serializers.ValidationError(f'Unsupported chat fields: {field_list}.')
        return attrs


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    sender_name = serializers.SerializerMethodField()
    is_current_user = serializers.SerializerMethodField()

    def get_sender(self, obj):
        return user_summary(obj.sender)

    def get_sender_name(self, obj):
        return user_display_name(obj.sender)

    def get_is_current_user(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.sender_id == request.user.id

    class Meta:
        model = Message
        fields = [
            'id',
            'conversation',
            'sender',
            'sender_username',
            'sender_name',
            'content',
            'created_at',
            'is_current_user',
        ]


class ConversationSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    def get_participants(self, obj):
        return [user_summary(user) for user in obj.participants.all()]

    def get_last_message(self, obj):
        messages = getattr(obj, 'prefetched_last_messages', None)
        message = messages[0] if messages else obj.messages.select_related('sender').order_by('-created_at', '-id').first()
        if message is None:
            return None
        return MessageSerializer(message, context=self.context).data

    class Meta:
        model = Conversation
        fields = [
            'id',
            'title',
            'participants',
            'last_message',
            'created_at',
            'updated_at',
        ]


class MessageCreateSerializer(serializers.Serializer):
    content = serializers.CharField(allow_blank=True, trim_whitespace=False)
