import logging
from datetime import date

from django.conf import settings
from django.core.cache import cache
from django.http import FileResponse

from cases.models import CaseLog
from documents.expiration_engine import DocumentExpirationVerificationService
from documents.models import Document, DocumentExpirationNotification

logger = logging.getLogger(__name__)

DOCUMENT_PRIVILEGED_ROLES = {'admin', 'advisor'}
DOCUMENT_FORBIDDEN_ROLES = {'beneficiary'}

# Keep backwards-compatible aliases used by upload_document
UPLOAD_PRIVILEGED_ROLES = DOCUMENT_PRIVILEGED_ROLES
UPLOAD_FORBIDDEN_ROLES = DOCUMENT_FORBIDDEN_ROLES
AUTO_CHECK_CACHE_KEY = 'documents:auto-expiration-check-lock'


def upload_document(case, user, file, name, description, expiration_date=None):
    """
    Upload a document associated with a case on behalf of a user.

    Access rules:
      admin / advisor -> always allowed
      assigned user (non-beneficiary) -> allowed
      beneficiary / unassigned non-privileged -> PermissionError
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
        content=f"User {user.username} uploaded document '{name}'",
    )

    return document


def get_case_documents(case, user):
    """
    Return all documents associated with a case.

    Access rules:
      admin / advisor -> always allowed
      assigned user (non-beneficiary) -> allowed
      beneficiary / unassigned non-privileged -> PermissionError
    """
    role = user.groups.values_list('name', flat=True).first()

    if role in DOCUMENT_FORBIDDEN_ROLES:
        raise PermissionError(f"Users with role '{role}' cannot view documents.")

    is_privileged = role in DOCUMENT_PRIVILEGED_ROLES
    is_assigned = case.users.filter(pk=user.pk).exists()

    if not is_privileged and not is_assigned:
        raise PermissionError(f"User '{user.username}' is not assigned to this case.")

    return case.documents.all()


def download_document(document_id, user):
    """
    Return a FileResponse for the requested document.

    Raises Document.DoesNotExist if no document matches document_id.

    Access rules:
      admin / advisor -> always allowed
      assigned user (non-beneficiary) -> allowed
      beneficiary / unassigned non-privileged -> PermissionError
    """
    document = Document.objects.get(pk=document_id)

    role = user.groups.values_list('name', flat=True).first()

    if role in DOCUMENT_FORBIDDEN_ROLES:
        raise PermissionError(f"Users with role '{role}' cannot download documents.")

    is_privileged = role in DOCUMENT_PRIVILEGED_ROLES
    is_assigned = document.case.users.filter(pk=user.pk).exists()

    if not is_privileged and not is_assigned:
        raise PermissionError(f"User '{user.username}' is not assigned to this case.")

    CaseLog.objects.create(
        case=document.case,
        user=user,
        content=f"User {user.username} downloaded document '{document.name}'",
    )

    filename = document.file.name.split('/')[-1]
    return FileResponse(document.file.open('rb'), as_attachment=True, filename=filename)


def verify_document_expirations(*, today=None, alert_days=None):
    """
    Verify documents with expiration dates and create one notification per event.
    """
    today = today or date.today()
    alert_days = (
        settings.DOCUMENT_EXPIRATION_ALERT_DAYS
        if alert_days is None
        else alert_days
    )

    documents = Document.objects.filter(expiration_date__isnull=False).select_related('case')
    service = DocumentExpirationVerificationService()
    return service.verify(documents=documents, today=today, alert_days=alert_days)


def run_automatic_document_expiration_check():
    interval_seconds = getattr(
        settings,
        'DOCUMENT_EXPIRATION_AUTO_CHECK_INTERVAL_SECONDS',
        300,
    )

    acquired = cache.add(AUTO_CHECK_CACHE_KEY, True, timeout=interval_seconds)
    if not acquired:
        return []

    try:
        return verify_document_expirations()
    except Exception:
        logger.exception('Automatic document expiration check failed.')
        return []


def get_user_document_notifications(user):
    return DocumentExpirationNotification.objects.filter(
        recipient=user,
    ).select_related('document', 'document__case').order_by('-created_at', '-id')
