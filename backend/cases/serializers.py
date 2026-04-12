from rest_framework import serializers

from .models import Case, CaseLog, Category, Subclinic


class CaseSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    status = serializers.CharField(source='status.name', read_only=True)
    category = serializers.CharField(source='category.name', read_only=True)
    subclinic = serializers.CharField(source='subclinic.name', read_only=True)

    class Meta:
        model = Case
        fields = [
            'id',
            'description',
            'created_at',
            'updated_at',
            'created_by',
            'status',
            'category',
            'subclinic',
        ]


class CaseCreateSerializer(serializers.Serializer):
    description = serializers.CharField()
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
    )
    subclinic_id = serializers.PrimaryKeyRelatedField(
        queryset=Subclinic.objects.all(),
        source='subclinic',
    )


class CaseUpdateSerializer(serializers.Serializer):
    description = serializers.CharField(required=False)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        required=False,
    )
    subclinic_id = serializers.PrimaryKeyRelatedField(
        queryset=Subclinic.objects.all(),
        source='subclinic',
        required=False,
    )


class CaseLogSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(source='user', read_only=True)

    class Meta:
        model = CaseLog
        fields = [
            'id',
            'content',
            'created_at',
            'created_by',
        ]


class CaseLogCreateSerializer(serializers.Serializer):
    content = serializers.CharField()