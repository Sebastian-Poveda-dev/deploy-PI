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
