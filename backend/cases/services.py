from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

from .models import Case, CaseAssignment, CaseLog, CaseProgressStatus, CaseStatus

APPROVAL_ALLOWED_ROLES = {'admin', 'advisor', 'professor'}
APPROVAL_PRIVILEGED_ROLES = {'admin', 'advisor'}

REJECTION_ALLOWED_ROLES = {'student', 'professor'}
STATUS_PENDING = 'pending_authorization'
STATUS_ACTIVE = 'active'

ROLE_STATUS_MAP = {
    'admin': 'active',
    'advisor': 'active',
    'professor': 'active',
    'student': 'pending_authorization',
}

CASE_LOG_ALLOWED_ROLES = {'admin', 'advisor', 'professor', 'student'}
CASE_LOG_PRIVILEGED_ROLES = {'admin', 'advisor'}

CASE_UPDATE_ALLOWED_ROLES = {'admin', 'advisor', 'professor', 'student'}
CASE_UPDATE_PRIVILEGED_ROLES = {'admin', 'advisor'}
CASE_UPDATE_ALLOWED_FIELDS = {'description', 'category', 'subclinic'}

WORKLOAD_ACTIVE_STATUSES = {'active', 'pending_authorization', 'in_progress'}


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


def _pick_student_for_case(category, excluded_user_ids=None):
    excluded_user_ids = excluded_user_ids or []
    candidates = list(_users_with_workload_for_role('student').exclude(pk__in=excluded_user_ids))
    if not candidates:
        raise ValueError('Cannot create case: no active students are available for assignment.')

    def student_score(student):
        # Matching the preferred category gives a small boost without ignoring workload balance.
        preference_bonus = 0.5 if student.favorite_category_id == category.id else 0.0
        return (student.workload - preference_bonus, student.workload, student.id)

    return min(candidates, key=student_score)


def reassign_case(case, excluded_user, actor=None):
    """
    Reassigns a case to a new student, excluding the current one
    and ensuring the current professor isn't picked as the new student.
    """
    with transaction.atomic():
        # Get all current assigned users to exclude them from the new assignment pick
        current_assigned_ids = list(case.users.values_list('pk', flat=True))
        
        # 1. Remove the excluded user's assignment
        CaseAssignment.objects.filter(case=case, user=excluded_user).delete()
        
        # 2. Pick a new student, excluding everyone currently or previously assigned
        new_student = _pick_student_for_case(case.category, excluded_user_ids=current_assigned_ids)
        
        # 3. Create the new assignment
        CaseAssignment.objects.create(case=case, user=new_student)
        
        # 4. Log the reassignment
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
    """
    from cases.models import CaseCancellationRequest

    role = user.groups.values_list('name', flat=True).first()
    is_privileged = role in {'admin', 'advisor'}
    is_assigned_professor = request.case.users.filter(pk=user.pk, groups__name='professor').exists()

    if not is_privileged and not is_assigned_professor:
        raise PermissionError('Only the assigned professor or an admin can approve this request.')

    if request.status != CaseCancellationRequest.PENDING:
        raise ValueError('Only pending requests can be approved.')

    with transaction.atomic():
        request.status = CaseCancellationRequest.APPROVED
        request.reviewed_by = user
        request.reviewed_at = timezone.now()
        request.save()

        # Reassign the case, passing the reviewer as the actor
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
    """
    from cases.models import CaseCancellationRequest

    role = user.groups.values_list('name', flat=True).first()
    is_privileged = role in {'admin', 'advisor'}
    is_assigned_professor = request.case.users.filter(pk=user.pk, groups__name='professor').exists()

    if not is_privileged and not is_assigned_professor:
        raise PermissionError('Only the assigned professor or an admin can reject this request.')

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


def _pick_professor_for_case(excluded_user_ids=None):
    excluded_user_ids = excluded_user_ids or []
    professor = (
        _users_with_workload_for_role('professor')
        .exclude(pk__in=excluded_user_ids)
        .order_by('workload', 'id')
        .first()
    )
    if professor is None:
        raise ValueError('Cannot create case: no active professors are available for assignment.')
    return professor


def create_case(user, description, category, subclinic, beneficiary):
    """
    Create a case on behalf of a user and auto-assign one student and one professor.

        status is determined by the user's role:
      admin / advisor / professor → active
    student                    → pending_authorization
      beneficiary                → PermissionError (not allowed)
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
            assigned_professor = _pick_professor_for_case(excluded_user_ids=[user.pk])
        elif role == 'professor':
            assigned_student = _pick_student_for_case(category)
            assigned_professor = user
        else:
            assigned_student = _pick_student_for_case(category)
            assigned_professor = _pick_professor_for_case(excluded_user_ids=[assigned_student.pk])

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

        CaseAssignment.objects.bulk_create(
            [
                CaseAssignment(case=case, user=assigned_student),
                CaseAssignment(case=case, user=assigned_professor),
            ],
            ignore_conflicts=True,
        )

        CaseLog.objects.create(
            case=case,
            user=user,
            content=(
                f'Case created by {user.username}. '
                f'Assigned student: {assigned_student.username}; '
                f'assigned professor: {assigned_professor.username}.'
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
      assigned user (non-beneficiary) → allowed
      beneficiary / unassigned non-privileged → PermissionError

    Only description, category, and subclinic may be changed.
    All other keys in data are silently ignored.
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
      professor assigned to the case → allowed
      professor not assigned / student / beneficiary → PermissionError

    Raises ValueError if the case is not in pending_authorization status.
    """
    role = user.groups.values_list('name', flat=True).first()

    if role not in APPROVAL_ALLOWED_ROLES:
        raise PermissionError(f"Users with role '{role}' cannot approve cases.")

    is_privileged = role in APPROVAL_PRIVILEGED_ROLES
    is_assigned = case.users.filter(pk=user.pk).exists()

    if not is_privileged and not is_assigned:
        raise PermissionError(f"User '{user.username}' is not assigned to this case.")

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


def reject_case_assignment(case, user):
    """
    Remove the user's assignment from a case.

    Access rules:
      professor assigned to the case → allowed
      admin / advisor → allowed
      student → PermissionError (must use cancellation request)
      user not assigned to the case → PermissionError (unless privileged)
    """
    role = user.groups.values_list('name', flat=True).first()
    is_privileged = role in {'admin', 'advisor'}

    if role == 'student':
        raise PermissionError('Students must use the "Request Reassignment" process instead of rejecting the case directly.')

    if not is_privileged:
        assignment = CaseAssignment.objects.filter(case=case, user=user).first()
        if assignment is None:
            raise PermissionError(f"User '{user.username}' is not assigned to this case.")
        
        if role == 'professor':
            has_student = case.users.filter(groups__name='student').exists()
            remaining_professors = case.users.filter(groups__name='professor').exclude(pk=user.pk).count()
            if has_student and remaining_professors == 0:
                raise PermissionError(
                    'Cannot reject assignment: there is a student assigned to this case '
                    'and no other professor would remain.'
                )
        assignment.delete()
    else:
        # Admin can remove anyone, but they need to specify who? 
        # Actually this service was designed for self-rejection.
        # Let's keep it simple for now.
        CaseAssignment.objects.filter(case=case, user=user).delete()

    CaseLog.objects.create(
        case=case,
        user=user,
        content=f'User {user.username} removed from the case assignment',
    )


PROGRESS_STATUS_PRIVILEGED_ROLES = {'admin', 'advisor'}
PROGRESS_STATUS_ASSIGNED_ROLES = {'professor', 'student'}


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
