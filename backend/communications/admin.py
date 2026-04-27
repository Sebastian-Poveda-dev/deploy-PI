from django.contrib import admin

from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'channel', 'creator', 'beneficiary', 'created_at', 'updated_at')
    list_filter = ('channel', 'created_at')
    search_fields = ('creator__username', 'beneficiary__username', 'beneficiary__email')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'created_at')
    search_fields = ('content', 'sender__username')
