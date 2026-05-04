from django.contrib import admin

from .models import Document, DocumentExpirationNotification


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'case', 'uploaded_by', 'expiration_date', 'is_expired')
    list_filter = ('is_expired', 'expiration_date')
    search_fields = ('name', 'description', 'uploaded_by__username')


@admin.register(DocumentExpirationNotification)
class DocumentExpirationNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'recipient', 'event_type', 'priority', 'created_at')
    list_filter = ('event_type', 'priority', 'created_at')
    search_fields = ('document__name', 'recipient__username', 'message')
