from django.conf import settings
from django.apps import apps
from rest_framework import serializers

from .models import Case, CancellationRequestNotification, CaseLog, CaseProgressStatus, Category, Subclinic

User = apps.get_model(settings.AUTH_USER_MODEL)


class CaseCancellationRequestSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.CharField(source='requested_by.username', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.username', read_only=True)

    class Meta:
        from .models import CaseCancellationRequest
        model = CaseCancellationRequest
        fields = [
            'id',
            'case',
            'requested_by',
            'requested_by_name',
            'reason',
            'status',
            'reviewed_by',
            'reviewed_by_name',
            'created_at',
            'reviewed_at',
        ]
        read_only_fields = ['status', 'reviewed_by', 'reviewed_at', 'requested_by', 'case']


class CaseSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    status = serializers.CharField(source='status.name', read_only=True)
    category = serializers.CharField(source='category.name', read_only=True)
    subclinic = serializers.CharField(source='subclinic.name', read_only=True)
    assigned_users = serializers.SerializerMethodField()
    beneficiary = serializers.PrimaryKeyRelatedField(read_only=True)
    beneficiary_name = serializers.SerializerMethodField()
    pending_cancellation_request = serializers.SerializerMethodField()
    attended_by_name = serializers.SerializerMethodField()

    def get_assigned_users(self, obj):
        return [{'name': user.username, 'id': user.id} for user in obj.users.all()]

    def get_beneficiary_name(self, obj):
        full_name = f'{obj.beneficiary.first_name} {obj.beneficiary.last_name}'.strip()
        return full_name or obj.beneficiary.username

    def get_pending_cancellation_request(self, obj):
        request = obj.cancellation_requests.filter(status='pending').first()
        if request:
            return CaseCancellationRequestSerializer(request).data
        return None

    def get_attended_by_name(self, obj):
        return obj.attended_by.username if obj.attended_by_id else None

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
            'pending_cancellation_request',
            'is_immediate',
            'immediate_resolution',
            'attended_by',
            'attended_by_name',
        ]


class BeneficiaryCaseSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='status.name', read_only=True)

    class Meta:
        model = Case
        fields = ['id', 'status']


class PublicProgressStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseProgressStatus
        fields = ['label', 'created_at']


class PublicBeneficiaryCaseStatusSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='status.name', read_only=True)
    progress_statuses = PublicProgressStatusSerializer(many=True, read_only=True)

    class Meta:
        model = Case
        fields = ['status', 'progress_statuses']


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
    is_immediate = serializers.BooleanField(default=False)
    immediate_resolution = serializers.CharField(required=False, allow_blank=True, default='')
    attended_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.exclude(groups__name='beneficiary').distinct(),
        source='attended_by',
        required=False,
        allow_null=True,
        default=None,
    )

    def validate_beneficiary(self, beneficiary):
        if not beneficiary.groups.filter(name='beneficiary').exists():
            raise serializers.ValidationError('Selected user must belong to the beneficiary group.')
        return beneficiary

    def validate(self, data):
        if data.get('is_immediate'):
            if not data.get('immediate_resolution', '').strip():
                raise serializers.ValidationError(
                    {'immediate_resolution': 'La resolución es requerida para casos inmediatos.'}
                )
        return data


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


class CaseProgressStatusSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = CaseProgressStatus
        fields = ['id', 'label', 'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['created_by', 'created_at']


class CaseProgressStatusCreateSerializer(serializers.Serializer):
    label = serializers.CharField(max_length=200)


class CancellationRequestNotificationSerializer(serializers.ModelSerializer):
    case_id = serializers.IntegerField(source='cancellation_request.case_id', read_only=True)
    requested_by = serializers.CharField(
        source='cancellation_request.requested_by.username', read_only=True
    )

    class Meta:
        model = CancellationRequestNotification
        fields = [
            'id',
            'cancellation_request',
            'case_id',
            'requested_by',
            'message',
            'is_read',
            'created_at',
        ]
        read_only_fields = ['cancellation_request', 'case_id', 'requested_by', 'message', 'created_at']
