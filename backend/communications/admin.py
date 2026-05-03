from django.contrib import admin

from .models import Conversation, ConversationParticipant, Message


class ConversationParticipantInline(admin.TabularInline):
    model = ConversationParticipant
    extra = 0
    autocomplete_fields = ('user',)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'creator', 'created_at', 'updated_at')
    search_fields = ('title', 'creator__username', 'participants__username')
    inlines = (ConversationParticipantInline,)


@admin.register(ConversationParticipant)
class ConversationParticipantAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'user', 'joined_at')
    search_fields = ('conversation__title', 'user__username', 'user__first_name', 'user__last_name')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'created_at')
    search_fields = ('content', 'sender__username', 'conversation__title')
