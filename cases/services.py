from .models import Case, CaseAssignment, CaseLog, CaseStatus

ROLE_STATUS_MAP = {
    'admin': 'active',
    'advisor': 'active',
    'professor': 'active',
    'student': 'pending_authorization',
}

CASE_LOG_ALLOWED_ROLES = {'admin', 'advisor', 'professor', 'student'}
CASE_LOG_PRIVILEGED_ROLES = {'admin', 'advisor'}


def create_case(user, description, category, subclinic):
    """
    Create a case on behalf of a user.

    Status is determined by the user's role:
      admin / advisor / professor → active
      student                    → pending_authorization
      beneficiary                → PermissionError (not allowed)
    """
    role = user.groups.values_list('name', flat=True).first()

    if role not in ROLE_STATUS_MAP:
        raise PermissionError(f"Users with role '{role}' cannot create cases.")

    status = CaseStatus.objects.get(name=ROLE_STATUS_MAP[role])

    case = Case.objects.create(
        description=description,
        created_by=user,
        category=category,
        subclinic=subclinic,
        status=status,
    )

    CaseAssignment.objects.create(case=case, user=user)

    CaseLog.objects.create(
        case=case,
        user=user,
        content=f'Case created by {user.username}',
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


def get_case_logs(case):
    return case.logs.order_by('created_at', 'pk')
