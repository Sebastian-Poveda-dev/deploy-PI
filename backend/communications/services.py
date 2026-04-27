import re

from .models import Conversation, Message


CONVERSATION_CREATOR_ROLES = {'admin', 'advisor', 'professor', 'student'}
VALID_CHANNELS = {choice[0] for choice in Conversation.CHANNEL_CHOICES}


def get_user_role(user):
    return user.groups.values_list('name', flat=True).first()


def user_is_beneficiary(user):
    return user.groups.filter(name='beneficiary').exists()


def user_can_create_conversation(user):
    return get_user_role(user) in CONVERSATION_CREATOR_ROLES


def user_is_participant(user, conversation):
    return user.pk in {conversation.creator_id, conversation.beneficiary_id}


def create_conversation(creator, beneficiary, channel):
    if not user_can_create_conversation(creator):
        raise PermissionError('Only admins, advisors, professors, or students can start conversations.')

    if channel not in VALID_CHANNELS:
        raise ValueError('Invalid communication channel.')

    if not user_is_beneficiary(beneficiary):
        raise ValueError('Target user must have the beneficiary role.')

    return Conversation.objects.create(
        channel=channel,
        creator=creator,
        beneficiary=beneficiary,
    )


def list_conversations_for_user(user):
    role = get_user_role(user)

    if role == 'admin':
        return Conversation.objects.select_related('creator', 'beneficiary').all()

    if role in CONVERSATION_CREATOR_ROLES:
        return Conversation.objects.select_related('creator', 'beneficiary').filter(creator=user)

    if user_is_beneficiary(user):
        return Conversation.objects.select_related('creator', 'beneficiary').filter(beneficiary=user)

    return Conversation.objects.none()


def get_conversation_for_user(conversation_id, user):
    conversation = Conversation.objects.select_related('creator', 'beneficiary').get(pk=conversation_id)
    if not user_is_participant(user, conversation):
        raise PermissionError('Only conversation participants can access this conversation.')
    return conversation


def create_message(conversation, sender, content):
    if not user_is_participant(sender, conversation):
        raise PermissionError('Only conversation participants can send messages.')

    stripped_content = (content or '').strip()
    if not stripped_content:
        raise ValueError('Message content cannot be empty.')

    message = Message.objects.create(
        conversation=conversation,
        sender=sender,
        content=stripped_content,
    )
    conversation.save(update_fields=['updated_at'])
    return message


def list_messages(conversation, user):
    if not user_is_participant(user, conversation):
        raise PermissionError('Only conversation participants can view messages.')

    return conversation.messages.select_related('sender').all()


def sanitize_phone_number(phone_number):
    digits = re.sub(r'\D', '', phone_number or '')
    if len(digits) == 10 and digits.startswith('3'):
        return f'57{digits}'
    return digits


def build_external_contact(conversation):
    beneficiary = conversation.beneficiary

    if conversation.channel == Conversation.CHANNEL_WHATSAPP:
        phone = sanitize_phone_number(beneficiary.phone_number)
        if not phone:
            return None, 'Beneficiary phone number is required for WhatsApp communication.'
        return f'https://wa.me/{phone}', ''

    if conversation.channel == Conversation.CHANNEL_EMAIL:
        if not beneficiary.email:
            return None, 'Beneficiary email is required for email communication.'
        return f'mailto:{beneficiary.email}', ''

    if conversation.channel == Conversation.CHANNEL_PHONE:
        phone = sanitize_phone_number(beneficiary.phone_number)
        if not phone:
            return None, 'Beneficiary phone number is required for phone communication.'
        return f'tel:+{phone}', ''

    return None, 'Invalid communication channel.'
