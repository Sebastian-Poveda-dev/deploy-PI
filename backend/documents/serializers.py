from rest_framework import serializers

from .models import Document, DocumentExpirationNotification


class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id',
            'name',
            'description',
            'uploaded_at',
            'expiration_date',
            'uploaded_by',
        ]

    def get_uploaded_by(self, obj):
        return obj.uploaded_by.username


class DocumentUploadSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True, default='')
    expiration_date = serializers.DateField(required=False, allow_null=True)
    file = serializers.FileField()


class DocumentExpirationNotificationSerializer(serializers.ModelSerializer):
    document_id = serializers.IntegerField(source='document.id', read_only=True)
    document_name = serializers.CharField(source='document.name', read_only=True)
    expiration_date = serializers.DateField(source='document.expiration_date', read_only=True)

    class Meta:
        model = DocumentExpirationNotification
        fields = [
            'id',
            'document_id',
            'document_name',
            'event_type',
            'priority',
            'message',
            'created_at',
            'expiration_date',
        ]


class DocumentExpirationVerificationSerializer(serializers.Serializer):
    today = serializers.DateField(required=False)
    alert_days = serializers.IntegerField(required=False, min_value=0)
