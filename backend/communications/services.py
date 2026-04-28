from django.apps import apps
from django.conf import settings
from django.db import transaction
from django.db.models import Max, Prefetch

from .models import Conversation, ConversationParticipant, Message

User = apps.get_model(settings.AUTH_USER_MODEL)


def get_user_role(user):
    return user.groups.values_list('name', flat=True).first()


def ensure_active_user(user):
    if not user or not user.is_authenticated or not user.is_active:
        raise PermissionError('Only authenticated active users can use chat.')


def conversation_queryset():
    last_message_prefetch = Prefetch(
        'messages',
        queryset=Message.objects.select_related('sender').order_by('-created_at', '-id'),
        to_attr='prefetched_last_messages',
    )
    return (
        Conversation.objects.select_related('creator')
        .prefetch_related('participants__groups', last_message_prefetch)
        .annotate(last_message_created_at=Max('messages__created_at'))
        .order_by('-updated_at', '-created_at')
    )


def user_is_participant(user, conversation):
    return conversation.participants.filter(pk=user.pk).exists()


@transaction.atomic
def create_conversation(creator, participant_ids, title=''):
    ensure_active_user(creator)

    unique_participant_ids = set(participant_ids or [])
    if not unique_participant_ids:
        raise ValueError('At least one participant is required.')

    participants = list(
        User.objects.filter(id__in=unique_participant_ids, is_active=True).prefetch_related('groups')
    )
    found_ids = {user.id for user in participants}
    if found_ids != unique_participant_ids:
        raise ValueError('All participants must be active users.')

    conversation = Conversation.objects.create(
        creator=creator,
        title=(title or '').strip(),
    )

    all_participants = {creator.id: creator}
    all_participants.update({participant.id: participant for participant in participants})
    ConversationParticipant.objects.bulk_create(
        [
            ConversationParticipant(conversation=conversation, user=participant)
            for participant in all_participants.values()
        ],
        ignore_conflicts=True,
    )
    return conversation_queryset().get(pk=conversation.pk)


def list_conversations_for_user(user):
    ensure_active_user(user)
    return conversation_queryset().filter(participants=user).distinct()


def get_conversation_for_participant(user, conversation_id):
    ensure_active_user(user)
    conversation = conversation_queryset().get(pk=conversation_id)
    if not user_is_participant(user, conversation):
        raise PermissionError('Only conversation participants can access this conversation.')
    return conversation


def list_messages(user, conversation_id):
    conversation = get_conversation_for_participant(user, conversation_id)
    return conversation.messages.select_related('sender').prefetch_related('sender__groups').all()


def create_message(user, conversation_id, content):
    conversation = get_conversation_for_participant(user, conversation_id)
    stripped_content = (content or '').strip()
    if not stripped_content:
        raise ValueError('Message content cannot be empty.')

    message = Message.objects.create(
        conversation=conversation,
        sender=user,
        content=stripped_content,
    )
    conversation.save(update_fields=['updated_at'])
    return Message.objects.select_related('sender', 'conversation').prefetch_related('sender__groups').get(pk=message.pk)


def list_chat_users(requesting_user):
    ensure_active_user(requesting_user)
    return (
        User.objects.filter(is_active=True)
        .exclude(pk=requesting_user.pk)
        .prefetch_related('groups')
        .order_by('first_name', 'last_name', 'username', 'id')
    )
