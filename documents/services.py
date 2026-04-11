from cases.models import CaseLog
from documents.models import Document

UPLOAD_PRIVILEGED_ROLES = {'admin', 'advisor'}
UPLOAD_FORBIDDEN_ROLES = {'beneficiary'}


def upload_document(case, user, file, name, description, expiration_date=None):
    """
    Upload a document associated with a case on behalf of a user.

    Access rules:
      admin / advisor → always allowed
      assigned user (non-beneficiary) → allowed
      beneficiary / unassigned non-privileged → PermissionError
    """
    role = user.groups.values_list('name', flat=True).first()

    if role in UPLOAD_FORBIDDEN_ROLES:
        raise PermissionError(f"Users with role '{role}' cannot upload documents.")

    is_privileged = role in UPLOAD_PRIVILEGED_ROLES
    is_assigned = case.users.filter(pk=user.pk).exists()

    if not is_privileged and not is_assigned:
        raise PermissionError(f"User '{user.username}' is not assigned to this case.")

    document = Document.objects.create(
        case=case,
        uploaded_by=user,
        file=file,
        name=name,
        description=description,
        expiration_date=expiration_date,
    )

    CaseLog.objects.create(
        case=case,
        user=user,
        content=f'Document uploaded by {user.username}',
    )

    return document
