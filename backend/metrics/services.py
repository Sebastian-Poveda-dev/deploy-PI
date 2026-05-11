from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone

from cases.models import Case, CaseAssignment
from documents.models import Document

ACTIVE_STATUSES = {'active', 'pending_authorization', 'in_progress'}
CLOSED_STATUSES = {'finished', 'canceled', 'inactive'}
RESOLVED_STATUS = 'finished'


def get_cases_by_status():
    qs = (
        Case.objects.values('status__name')
        .annotate(count=Count('id'))
        .order_by('status__name')
    )
    return [{'status': item['status__name'], 'count': item['count']} for item in qs]


def get_cases_by_category():
    qs = (
        Case.objects.values('category__name')
        .annotate(count=Count('id'))
        .order_by('category__name')
    )
    return [{'category': item['category__name'], 'count': item['count']} for item in qs]


def get_cases_by_subclinic():
    qs = (
        Case.objects.values('subclinic__name')
        .annotate(count=Count('id'))
        .order_by('subclinic__name')
    )
    return [{'subclinic': item['subclinic__name'], 'count': item['count']} for item in qs]


def get_working_velocity(months=12):
    cutoff = timezone.now() - timedelta(days=months * 30)
    qs = (
        Case.objects.filter(status__name=RESOLVED_STATUS, updated_at__gte=cutoff)
        .annotate(month=TruncMonth('updated_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    return [{'month': item['month'].strftime('%Y-%m'), 'count': item['count']} for item in qs]


def get_avg_resolution_time():
    qs = (
        Case.objects.filter(status__name=RESOLVED_STATUS)
        .annotate(
            resolution_duration=ExpressionWrapper(
                F('updated_at') - F('created_at'),
                output_field=DurationField(),
            )
        )
        .values('category__name')
        .annotate(avg_resolution=Avg('resolution_duration'))
        .order_by('category__name')
    )
    result = []
    for item in qs:
        td = item['avg_resolution']
        avg_days = round(td.total_seconds() / 86400, 2) if td else 0.0
        result.append({'category': item['category__name'], 'avg_days': avg_days})
    return result


def get_opened_vs_closed(months=12):
    cutoff = timezone.now() - timedelta(days=months * 30)

    opened = {
        item['month']: item['count']
        for item in (
            Case.objects.filter(created_at__gte=cutoff)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(count=Count('id'))
        )
    }
    closed = {
        item['month']: item['count']
        for item in (
            Case.objects.filter(status__name__in=CLOSED_STATUSES, updated_at__gte=cutoff)
            .annotate(month=TruncMonth('updated_at'))
            .values('month')
            .annotate(count=Count('id'))
        )
    }

    all_months = sorted(set(opened.keys()) | set(closed.keys()))
    return [
        {
            'month': m.strftime('%Y-%m'),
            'opened': opened.get(m, 0),
            'closed': closed.get(m, 0),
        }
        for m in all_months
    ]


def get_cases_per_user():
    User = get_user_model()
    users = (
        User.objects.filter(groups__name__in=['student', 'professor'], is_active=True)
        .prefetch_related('groups')
        .annotate(
            active_cases=Count(
                'case_assignments',
                filter=Q(case_assignments__case__status__name__in=ACTIVE_STATUSES),
                distinct=True,
            )
        )
        .distinct()
        .order_by('-active_cases', 'username')
    )
    result = []
    for user in users:
        role = next((g.name for g in user.groups.all() if g.name in ('student', 'professor')), None)
        result.append({
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': role,
            'active_cases': user.active_cases,
        })
    return result


def get_unassigned_cases():
    return (
        Case.objects.filter(status__name__in=ACTIVE_STATUSES)
        .exclude(pk__in=CaseAssignment.objects.values('case_id'))
        .count()
    )


def get_cancellation_rate():
    total = Case.objects.count()
    canceled = Case.objects.filter(status__name='canceled').count()
    return {
        'total': total,
        'canceled': canceled,
        'rate': round(canceled / total, 4) if total > 0 else 0.0,
    }


def get_document_expiration():
    today = timezone.now().date()
    threshold = today + timedelta(days=7)
    return {
        'expired': Document.objects.filter(is_expired=True).count(),
        'expiring_soon': Document.objects.filter(
            is_expired=False,
            expiration_date__isnull=False,
            expiration_date__gte=today,
            expiration_date__lte=threshold,
        ).count(),
    }
