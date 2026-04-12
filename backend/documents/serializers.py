from rest_framework import serializers

from .models import Document


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
    description = serializers.CharField()
    expiration_date = serializers.DateField(required=False, allow_null=True)
    file = serializers.FileField()
