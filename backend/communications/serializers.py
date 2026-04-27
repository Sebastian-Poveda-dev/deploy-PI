from django.apps import apps
from django.conf import settings
from rest_framework import serializers

from .models import Conversation, Message
from .services import build_external_contact

User = apps.get_model(settings.AUTH_USER_MODEL)


def user_display_name(user):
    full_name = f'{user.first_name} {user.last_name}'.strip()
    return full_name or user.username


def user_summary(user):
    return {
        'id': user.id,
        'username': user.username,
        'name': user_display_name(user),
    }


class ConversationCreateSerializer(serializers.Serializer):
    beneficiary_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='beneficiary',
    )
    channel = serializers.ChoiceField(choices=[choice[0] for choice in Conversation.CHANNEL_CHOICES])


class ConversationSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField()
    creator_name = serializers.SerializerMethodField()
    beneficiary = serializers.SerializerMethodField()
    beneficiary_name = serializers.SerializerMethodField()
    beneficiary_email = serializers.EmailField(source='beneficiary.email', read_only=True)
    beneficiary_phone = serializers.CharField(source='beneficiary.phone_number', read_only=True)
    beneficiary_phone_number = serializers.CharField(source='beneficiary.phone_number', read_only=True)
    external_url = serializers.SerializerMethodField()
    external_url_warning = serializers.SerializerMethodField()

    def _external_contact(self, obj):
        return build_external_contact(obj)

    def get_creator(self, obj):
        return user_summary(obj.creator)

    def get_creator_name(self, obj):
        return user_display_name(obj.creator)

    def get_beneficiary(self, obj):
        return user_summary(obj.beneficiary)

    def get_beneficiary_name(self, obj):
        return user_display_name(obj.beneficiary)

    def get_external_url(self, obj):
        external_url, _warning = self._external_contact(obj)
        return external_url

    def get_external_url_warning(self, obj):
        _external_url, warning = self._external_contact(obj)
        return warning or None

    class Meta:
        model = Conversation
        fields = [
            'id',
            'channel',
            'creator',
            'creator_name',
            'beneficiary',
            'beneficiary_name',
            'beneficiary_email',
            'beneficiary_phone',
            'beneficiary_phone_number',
            'external_url',
            'external_url_warning',
            'created_at',
            'updated_at',
        ]


class MessageCreateSerializer(serializers.Serializer):
    content = serializers.CharField(allow_blank=True, trim_whitespace=False)


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
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
            'sender_name',
            'content',
            'created_at',
            'is_current_user',
        ]
