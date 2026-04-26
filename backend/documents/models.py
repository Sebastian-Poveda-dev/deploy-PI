from django.conf import settings
from django.db import models


def document_upload_path(instance, filename):
    return f'cases/{instance.case_id}/{filename}'


class Document(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    file = models.FileField(upload_to=document_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateField(null=True, blank=True)
    is_expired = models.BooleanField(default=False)

    case = models.ForeignKey(
        'cases.Case',
        on_delete=models.CASCADE,
        related_name='documents',
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='uploaded_documents',
    )

    def __str__(self):
        return f'{self.name} (Case #{self.case_id})'


class DocumentExpirationNotification(models.Model):
    EVENT_UPCOMING = 'upcoming'
    EVENT_EXPIRED = 'expired'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'
    EVENT_CHOICES = [
        (EVENT_UPCOMING, 'Upcoming'),
        (EVENT_EXPIRED, 'Expired'),
    ]
    PRIORITY_CHOICES = [
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
    ]

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='expiration_notifications',
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='document_expiration_notifications',
    )
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES)
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('document', 'recipient', 'event_type')

    def __str__(self):
        return f"{self.document.name} -> {self.recipient.username} ({self.event_type})"
