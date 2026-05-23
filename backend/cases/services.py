from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

from .models import Case, CaseAssignment, CancellationRequestNotification, CaseLog, CaseStatus

APPROVAL_ALLOWED_ROLES = {'admin', 'advisor'}

ROLE_STATUS_MAP = {
    'admin': 'active',
    'advisor': 'active',
    'student': 'pending_authorization',
}

CASE_LOG_ALLOWED_ROLES = {'admin', 'advisor', 'student'}
CASE_LOG_PRIVILEGED_ROLES = {'admin', 'advisor'}

CASE_UPDATE_ALLOWED_ROLES = {'admin', 'advisor', 'student'}
CASE_UPDATE_PRIVILEGED_ROLES = {'admin', 'advisor'}
CASE_UPDATE_ALLOWED_FIELDS = {'description', 'category', 'subclinic'}

WORKLOAD_ACTIVE_STATUSES = {'active', 'pending_authorization', 'in_progress'}

STATUS_PENDING = 'pending_authorization'
STATUS_ACTIVE = 'active'


def _users_with_workload_for_role(role_name):
    User = get_user_model()
    return (
        User.objects.filter(is_active=True, groups__name=role_name)
        .distinct()
        .annotate(
            workload=Count(
                'case_assignments',
                filter=Q(case_assignments__case__status__name__in=WORKLOAD_ACTIVE_STATUSES),
                distinct=True,
            )
        )
    )


def _pick_student_for_case(excluded_user_ids=None):
    excluded_user_ids = excluded_user_ids or []
    candidate = (
        _users_with_workload_for_role('student')
        .exclude(pk__in=excluded_user_ids)
        .order_by('workload', 'id')
        .first()
    )
    if candidate is None:
        raise ValueError('Cannot create case: no active students are available for assignment.')
    return candidate


def _pick_advisor_for_case(category, excluded_user_ids=None):
    excluded_user_ids = excluded_user_ids or []
    candidate = (
        _users_with_workload_for_role('advisor')
        .filter(category=category)
        .exclude(pk__in=excluded_user_ids)
        .order_by('workload', 'id')
        .first()
    )
    if candidate is None:
        raise ValueError(
            f"Cannot create case: no active advisors are available for category '{category.name}'."
        )
    return candidate


def reassign_case(case, excluded_user, actor=None):
    """
    Reassigns a case to a new student, excluding the current one.
    """
    with transaction.atomic():
        current_assigned_ids = list(case.users.values_list('pk', flat=True))

        CaseAssignment.objects.filter(case=case, user=excluded_user).delete()

        new_student = _pick_student_for_case(excluded_user_ids=current_assigned_ids)

        CaseAssignment.objects.create(case=case, user=new_student)

        log_user = actor or excluded_user
        CaseLog.objects.create(
            case=case,
            user=log_user,
            content=f'Case reassigned from {excluded_user.username} to {new_student.username}.'
        )

    return new_student


def approve_cancellation_request(request, user):
    """
    Approve a case cancellation request and trigger reassignment.
    Admins always allowed; advisors must be assigned to the case.
    """
    from cases.models import CaseCancellationRequest

    role = user.groups.values_list('name', flat=True).first()
    if role == 'advisor':
        if not request.case.users.filter(pk=user.pk).exists():
            raise PermissionError('Only the assigned advisor can approve this request.')
    elif role != 'admin':
        raise PermissionError('Only an admin or the assigned advisor can approve this request.')

    if request.status != CaseCancellationRequest.PENDING:
        raise ValueError('Only pending requests can be approved.')

    with transaction.atomic():
        request.status = CaseCancellationRequest.APPROVED
        request.reviewed_by = user
        request.reviewed_at = timezone.now()
        request.save()

        reassign_case(request.case, request.requested_by, actor=user)

        CaseLog.objects.create(
            case=request.case,
            user=user,
            content=f'Cancellation request approved by {user.username}. Case reassigned.'
        )

    return request


def reject_cancellation_request(request, user):
    """
    Reject a case cancellation request.
    Admins always allowed; advisors must be assigned to the case.
    """
    from cases.models import CaseCancellationRequest

    role = user.groups.values_list('name', flat=True).first()
    if role == 'advisor':
        if not request.case.users.filter(pk=user.pk).exists():
            raise PermissionError('Only the assigned advisor can reject this request.')
    elif role != 'admin':
        raise PermissionError('Only an admin or the assigned advisor can reject this request.')

    if request.status != CaseCancellationRequest.PENDING:
        raise ValueError('Only pending requests can be rejected.')

    request.status = CaseCancellationRequest.REJECTED
    request.reviewed_by = user
    request.reviewed_at = timezone.now()
    request.save()

    CaseLog.objects.create(
        case=request.case,
        user=user,
        content=f'Cancellation request rejected by {user.username}.'
    )

    return request


def create_case(user, description, category, subclinic, beneficiary):
    """
    Create a case on behalf of a user and auto-assign one student.

    status is determined by the user's role:
      admin / advisor → active
      student         → pending_authorization
      beneficiary     → PermissionError (not allowed)
    """
    role = user.groups.values_list('name', flat=True).first()

    if role not in ROLE_STATUS_MAP:
        raise PermissionError(f"Users with role '{role}' cannot create cases.")

    if beneficiary is None:
        raise ValueError('A beneficiary is required to create a case.')

    if not beneficiary.groups.filter(name='beneficiary').exists():
        raise ValueError('Selected user must belong to the beneficiary group.')

    status = CaseStatus.objects.get(name=ROLE_STATUS_MAP[role])

    with transaction.atomic():
        if role == 'student':
            assigned_student = user
        else:
            assigned_student = _pick_student_for_case()

        assigned_advisor = _pick_advisor_for_case(category)

        case = Case(
            description=description,
            created_by=user,
            category=category,
            subclinic=subclinic,
            status=status,
            beneficiary=beneficiary,
        )
        case.full_clean()
        case.save()

        CaseAssignment.objects.create(case=case, user=assigned_student)
        CaseAssignment.objects.create(case=case, user=assigned_advisor)

        CaseLog.objects.create(
            case=case,
            user=user,
            content=(
                f'Case created by {user.username}. '
                f'Assigned student: {assigned_student.username}. '
                f'Assigned advisor: {assigned_advisor.username}.'
            ),
        )

    return case


def create_case_log(user, case, content):
    role = user.groups.values_list('name', flat=True).first()

    if role not in CASE_LOG_ALLOWED_ROLES:
        raise PermissionError(f"Users with role '{role}' cannot create case logs.")

    if not content or not content.strip():
        raise ValueError('Case log content cannot be empty.')

    is_assigned = case.users.filter(pk=user.pk).exists()
    if role not in CASE_LOG_PRIVILEGED_ROLES and not is_assigned:
        raise PermissionError('User must be assigned to this case to create logs.')

    return CaseLog.objects.create(
        case=case,
        user=user,
        content=content.strip(),
    )


def get_case_logs(case, user):
    role = user.groups.values_list('name', flat=True).first()

    if role not in CASE_LOG_ALLOWED_ROLES:
        raise PermissionError(f"Users with role '{role}' cannot view case logs.")

    is_assigned = case.users.filter(pk=user.pk).exists()
    if role not in CASE_LOG_PRIVILEGED_ROLES and not is_assigned:
        raise PermissionError('User must be assigned to this case to view logs.')

    return case.logs.order_by('created_at', 'pk')


def update_case(case, user, data):
    """
    Update allowed fields of a case on behalf of a user.

    Access rules:
      admin / advisor → always allowed
      assigned student → allowed
      beneficiary / unassigned non-privileged → PermissionError

    Only description, category, and subclinic may be changed.
    """
    role = user.groups.values_list('name', flat=True).first()

    if role not in CASE_UPDATE_ALLOWED_ROLES:
        raise PermissionError(f"Users with role '{role}' cannot update cases.")

    is_privileged = role in CASE_UPDATE_PRIVILEGED_ROLES
    is_assigned = case.users.filter(pk=user.pk).exists()

    if not is_privileged and not is_assigned:
        raise PermissionError(f"User '{user.username}' is not assigned to this case.")

    for field, value in data.items():
        if field in CASE_UPDATE_ALLOWED_FIELDS:
            setattr(case, field, value)

    case.save()

    CaseLog.objects.create(
        case=case,
        user=user,
        content=f'Case updated by {user.username}',
    )

    return case


def approve_case(case, user):
    """
    Approve a case, transitioning its status from pending_authorization to active.

    Access rules:
      admin / advisor → always allowed
      student / beneficiary → PermissionError

    Raises ValueError if the case is not in pending_authorization status.
    """
    role = user.groups.values_list('name', flat=True).first()

    if role not in APPROVAL_ALLOWED_ROLES:
        raise PermissionError(f"Users with role '{role}' cannot approve cases.")

    if case.status.name != STATUS_PENDING:
        raise ValueError(
            f"Case cannot be approved because its status is '{case.status.name}', "
            f"not '{STATUS_PENDING}'."
        )

    case.status = CaseStatus.objects.get(name=STATUS_ACTIVE)
    case.save()

    CaseLog.objects.create(
        case=case,
        user=user,
        content=f'Case approved by {user.username}',
    )

    return case


def notify_advisors_of_cancellation_request(cancellation_request):
    """
    Create a notification for each advisor assigned to the case associated
    with the given cancellation request.
    """
    case = cancellation_request.case
    student = cancellation_request.requested_by
    advisors = case.users.filter(groups__name='advisor')

    for advisor in advisors:
        CancellationRequestNotification.objects.get_or_create(
            cancellation_request=cancellation_request,
            recipient=advisor,
            defaults={
                'message': (
                    f'El estudiante {student.username} ha solicitado la reasignación '
                    f'del caso #{case.pk}.'
                )
            },
        )


def get_cancellation_request_notifications(user):
    return CancellationRequestNotification.objects.filter(recipient=user)


def reject_case_assignment(case, user):
    """
    Remove the user's own assignment from a case.

    Students must use the cancellation request flow instead.
    Only admin / advisor can use this endpoint directly.
    """
    role = user.groups.values_list('name', flat=True).first()

    if role == 'student':
        raise PermissionError(
            'Students must use the "Request Reassignment" process instead of rejecting the case directly.'
        )

    if role not in {'admin', 'advisor'}:
        raise PermissionError(f"Users with role '{role}' cannot reject case assignments.")

    CaseAssignment.objects.filter(case=case, user=user).delete()

    CaseLog.objects.create(
        case=case,
        user=user,
        content=f'User {user.username} removed from the case assignment',
    )
