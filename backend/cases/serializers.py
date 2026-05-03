from django.conf import settings
from django.apps import apps
from rest_framework import serializers

from .models import Case, CaseLog, Category, Subclinic

User = apps.get_model(settings.AUTH_USER_MODEL)


class CaseSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    status = serializers.CharField(source='status.name', read_only=True)
    category = serializers.CharField(source='category.name', read_only=True)
    subclinic = serializers.CharField(source='subclinic.name', read_only=True)
    assigned_users = serializers.SerializerMethodField()
    beneficiary = serializers.PrimaryKeyRelatedField(read_only=True)
    beneficiary_name = serializers.SerializerMethodField()

    def get_assigned_users(self, obj):
        return [{'name': user.username} for user in obj.users.all()]

    def get_beneficiary_name(self, obj):
        full_name = f'{obj.beneficiary.first_name} {obj.beneficiary.last_name}'.strip()
        return full_name or obj.beneficiary.username

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
            'beneficiary',
            'beneficiary_name',
            'assigned_users',
        ]


class BeneficiaryCaseSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='status.name', read_only=True)

    class Meta:
        model = Case
        fields = ['id', 'status']


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
    beneficiary_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(groups__name='beneficiary').distinct(),
        source='beneficiary',
    )
    professor_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(groups__name='professor'),
        source='professor',
        required=False,
        allow_null=True,
        default=None,
    )

    def validate_beneficiary(self, beneficiary):
        if not beneficiary.groups.filter(name='beneficiary').exists():
            raise serializers.ValidationError('Selected user must belong to the beneficiary group.')
        return beneficiary


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
    created_by_name = serializers.CharField(source='user.username', read_only=True)
    is_current_user = serializers.SerializerMethodField()

    def get_is_current_user(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.user_id == request.user.id

    class Meta:
        model = CaseLog
        fields = [
            'id',
            'content',
            'created_at',
            'created_by',
            'created_by_name',
            'is_current_user',
        ]


class CaseLogCreateSerializer(serializers.Serializer):
    content = serializers.CharField()
