from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

from .models import Case, CaseAssignment, CancellationRequestNotification, CaseLog, CaseProgressStatus, CaseStatus

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
            content=f'Caso reasignado de {excluded_user.username} a {new_student.username}.'
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
            content=f'Solicitud de reasignación aprobada por {user.username}. Caso reasignado.'
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
        content=f'Solicitud de reasignación rechazada por {user.username}.'
    )

    return request


def create_case(
    user, description, category, subclinic, beneficiary,
    is_immediate=False, immediate_resolution='', attended_by=None,
):
    """
    Create a case on behalf of a user and auto-assign one student.

    If is_immediate=True the case is created directly in 'finished' status
    with no auto-assignment. attended_by records who resolved it on the spot.
    """
    role = user.groups.values_list('name', flat=True).first()

    if role not in ROLE_STATUS_MAP:
        raise PermissionError(f"Users with role '{role}' cannot create cases.")

    if beneficiary is None:
        raise ValueError('A beneficiary is required to create a case.')

    if not beneficiary.groups.filter(name='beneficiary').exists():
        raise ValueError('Selected user must belong to the beneficiary group.')

    if is_immediate:
        case_status = CaseStatus.objects.get(name='finished')
        with transaction.atomic():
            case = Case(
                description=description,
                created_by=user,
                category=category,
                subclinic=subclinic,
                status=case_status,
                beneficiary=beneficiary,
                is_immediate=True,
                immediate_resolution=immediate_resolution.strip(),
                attended_by=attended_by,
            )
            case.full_clean()
            case.save()

            attended_label = attended_by.username if attended_by else 'sin especificar'
            CaseLog.objects.create(
                case=case,
                user=user,
                content=(
                    f'Caso de resolución inmediata creado por {user.username}. '
                    f'Atendido por: {attended_label}. '
                    f'Resolución: {immediate_resolution.strip()}'
                ),
            )
        return case

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
                f'Caso creado por {user.username}. '
                f'Estudiante asignado: {assigned_student.username}. '
                f'Asesor asignado: {assigned_advisor.username}.'
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
        content=f'Caso actualizado por {user.username}.',
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
        content=f'Caso aprobado por {user.username}.',
    )

    return case


CANCEL_CASE_ALLOWED_ROLES = {'admin', 'advisor'}


def cancel_case(case, user, reason, reason_other=None):
    """
    Cancel a case with a predefined reason.
    Only admins and advisors are allowed.
    """
    from .models import Case as CaseModel

    role = user.groups.values_list('name', flat=True).first()
    if role not in CANCEL_CASE_ALLOWED_ROLES:
        raise PermissionError(f"Users with role '{role}' cannot cancel cases.")

    valid_reasons = {choice[0] for choice in CaseModel.CANCELLATION_REASON_CHOICES}
    if reason not in valid_reasons:
        raise ValueError(f"Invalid cancellation reason: '{reason}'.")

    if reason == CaseModel.CANCELLATION_REASON_OTRO:
        if not reason_other or not reason_other.strip():
            raise ValueError('Se requiere una descripción cuando la razón es "Otro".')
    else:
        reason_other = None

    canceled_status = CaseStatus.objects.get(name='canceled')

    with transaction.atomic():
        case.status = canceled_status
        case.cancellation_reason = reason
        case.cancellation_reason_other = reason_other.strip() if reason_other else None
        case.save()

        reason_display = dict(CaseModel.CANCELLATION_REASON_CHOICES).get(reason, reason)
        log_content = f'Caso cancelado por {user.username}. Razón: {reason_display}.'
        if reason_other:
            log_content += f' Detalle: {reason_other.strip()}'

        CaseLog.objects.create(case=case, user=user, content=log_content)

    return case


def manual_reassign_case(admin_user, case, new_student_id=None, new_advisor_id=None):
    """
    Manually reassign the student and/or advisor on a case. Admin only.
    Providing None for either ID leaves that assignment untouched.
    """
    User = get_user_model()

    role = admin_user.groups.values_list('name', flat=True).first()
    if role != 'admin':
        raise PermissionError('Only admins can manually reassign cases.')

    if new_student_id is None and new_advisor_id is None:
        raise ValueError('At least one of new_student_id or new_advisor_id must be provided.')

    with transaction.atomic():
        log_parts = []

        if new_student_id is not None:
            new_student = User.objects.filter(pk=new_student_id, groups__name='student', is_active=True).first()
            if new_student is None:
                raise ValueError('El estudiante seleccionado no existe o no está activo.')
            current_student_ids = list(
                case.assignments.filter(user__groups__name='student').values_list('user_id', flat=True)
            )
            case.assignments.filter(user__groups__name='student').delete()
            CaseAssignment.objects.create(case=case, user=new_student)
            old_names = list(User.objects.filter(pk__in=current_student_ids).values_list('username', flat=True))
            old_label = ', '.join(old_names) if old_names else 'ninguno'
            log_parts.append(f'Estudiante reasignado de {old_label} a {new_student.username}')

        if new_advisor_id is not None:
            new_advisor = User.objects.filter(pk=new_advisor_id, groups__name='advisor', is_active=True).first()
            if new_advisor is None:
                raise ValueError('El asesor seleccionado no existe o no está activo.')
            current_advisor_ids = list(
                case.assignments.filter(user__groups__name='advisor').values_list('user_id', flat=True)
            )
            case.assignments.filter(user__groups__name='advisor').delete()
            CaseAssignment.objects.create(case=case, user=new_advisor)
            old_names = list(User.objects.filter(pk__in=current_advisor_ids).values_list('username', flat=True))
            old_label = ', '.join(old_names) if old_names else 'ninguno'
            log_parts.append(f'Asesor reasignado de {old_label} a {new_advisor.username}')

        CaseLog.objects.create(
            case=case,
            user=admin_user,
            content=f'Reasignación manual por {admin_user.username}. {". ".join(log_parts)}.',
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
    return CancellationRequestNotification.objects.filter(
        recipient=user,
        cancellation_request__status='pending',
    )


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
        content=f'El usuario {user.username} fue removido de la asignación del caso.',
    )


PROGRESS_STATUS_PRIVILEGED_ROLES = {'admin', 'advisor'}
PROGRESS_STATUS_ASSIGNED_ROLES = {'student'}


def _assert_can_access_progress_statuses(user, case):
    role = user.groups.values_list('name', flat=True).first()
    if role in PROGRESS_STATUS_PRIVILEGED_ROLES:
        return
    if role in PROGRESS_STATUS_ASSIGNED_ROLES:
        if case.assignments.filter(user=user).exists():
            return
        raise PermissionError('Debes estar asignado al caso para acceder a los estados de progreso.')
    raise PermissionError('No tienes permiso para acceder a los estados de progreso.')


def get_case_progress_statuses(user, case):
    _assert_can_access_progress_statuses(user, case)
    return case.progress_statuses.all()


def add_case_progress_status(user, case, label):
    _assert_can_access_progress_statuses(user, case)
    return CaseProgressStatus.objects.create(case=case, label=label, created_by=user)
