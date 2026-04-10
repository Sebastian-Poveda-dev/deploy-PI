from .models import Case, CaseAssignment, CaseLog, CaseStatus

ROLE_STATUS_MAP = {
    'admin': 'active',
    'advisor': 'active',
    'professor': 'active',
    'student': 'pending_authorization',
}


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
