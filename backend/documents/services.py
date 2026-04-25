from datetime import date

from django.conf import settings
from django.db import transaction
from django.http import FileResponse

from cases.models import CaseLog
from documents.models import Document, DocumentExpirationNotification

DOCUMENT_PRIVILEGED_ROLES = {'admin', 'advisor'}
DOCUMENT_FORBIDDEN_ROLES = {'beneficiary'}

# Keep backwards-compatible aliases used by upload_document
UPLOAD_PRIVILEGED_ROLES = DOCUMENT_PRIVILEGED_ROLES
UPLOAD_FORBIDDEN_ROLES = DOCUMENT_FORBIDDEN_ROLES


@transaction.atomic
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
        content=f"User {user.username} uploaded document '{name}'",
    )

    return document


def get_case_documents(case, user):
    """
    Return all documents associated with a case.

    Access rules:
      admin / advisor → always allowed
      assigned user (non-beneficiary) → allowed
      beneficiary / unassigned non-privileged → PermissionError
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
      admin / advisor → always allowed
      assigned user (non-beneficiary) → allowed
      beneficiary / unassigned non-privileged → PermissionError
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

    Current recipients:
      assigned students on the case

    Generated events:
      upcoming -> expiration date is within the configured alert range
      expired  -> expiration date is before today
    """
    today = today or date.today()
    alert_days = (
        settings.DOCUMENT_EXPIRATION_ALERT_DAYS
        if alert_days is None
        else alert_days
    )

    created_notifications = []
    documents = Document.objects.filter(expiration_date__isnull=False).select_related('case')

    for document in documents:
        recipients = list(document.case.users.filter(groups__name='student').distinct())
        if not recipients:
            continue

        if document.expiration_date < today:
            if not document.is_expired:
                document.is_expired = True
                document.save(update_fields=['is_expired'])

            for recipient in recipients:
                notification, created = DocumentExpirationNotification.objects.get_or_create(
                    document=document,
                    recipient=recipient,
                    event_type=DocumentExpirationNotification.EVENT_EXPIRED,
                    defaults={
                        'message': (
                            f"Document '{document.name}' expired on "
                            f"{document.expiration_date}."
                        )
                    },
                )
                if created:
                    created_notifications.append(notification)
            continue

        days_until_expiration = (document.expiration_date - today).days
        if days_until_expiration > alert_days:
            continue

        for recipient in recipients:
            notification, created = DocumentExpirationNotification.objects.get_or_create(
                document=document,
                recipient=recipient,
                event_type=DocumentExpirationNotification.EVENT_UPCOMING,
                defaults={
                    'message': (
                        f"Document '{document.name}' expires on "
                        f"{document.expiration_date}."
                    )
                },
            )
            if created:
                created_notifications.append(notification)

    return created_notifications
