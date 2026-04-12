from rest_framework import serializers

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            'id',
            'name',
            'description',
            'uploaded_at',
            'expiration_date',
        ]


class DocumentUploadSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField()
    expiration_date = serializers.DateTimeField(required=False, allow_null=True)
    file = serializers.FileField()
