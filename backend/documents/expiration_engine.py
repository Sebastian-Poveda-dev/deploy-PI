from dataclasses import dataclass

from django.conf import settings
from django.contrib.auth import get_user_model

from cases.models import CaseLog
from documents.models import DocumentExpirationNotification

User = get_user_model()


@dataclass(frozen=True)
class DocumentExpirationEvent:
    event_type: str
    priority: str
    message: str
    log_message: str
    should_mark_expired: bool = False


class BaseExpirationRule:
    def build_event(self, *, document, today, alert_days, urgent_alert_days):
        raise NotImplementedError


class ExpiredDocumentRule(BaseExpirationRule):
    def build_event(self, *, document, today, alert_days, urgent_alert_days):
        if document.expiration_date >= today:
            return None

        return DocumentExpirationEvent(
            event_type=DocumentExpirationNotification.EVENT_EXPIRED,
            priority=DocumentExpirationNotification.PRIORITY_HIGH,
            message=(
                f"Document '{document.name}' expired on {document.expiration_date}."
            ),
            log_message=(
                f"Document '{document.name}' marked as expired on {document.expiration_date}."
            ),
            should_mark_expired=True,
        )


class UrgentUpcomingDocumentRule(BaseExpirationRule):
    def build_event(self, *, document, today, alert_days, urgent_alert_days):
        days_until_expiration = (document.expiration_date - today).days
        if days_until_expiration < 0 or days_until_expiration > urgent_alert_days:
            return None

        day_label = 'today' if days_until_expiration == 0 else f'in {days_until_expiration} day(s)'
        return DocumentExpirationEvent(
            event_type=DocumentExpirationNotification.EVENT_UPCOMING_URGENT,
            priority=DocumentExpirationNotification.PRIORITY_HIGH,
            message=(
                f"Urgent reminder: document '{document.name}' expires {day_label} "
                f"on {document.expiration_date}."
            ),
            log_message=(
                f"Urgent expiration reminder created for document '{document.name}' "
                f"with expiration date {document.expiration_date}."
            ),
        )


class UpcomingDocumentRule(BaseExpirationRule):
    def build_event(self, *, document, today, alert_days, urgent_alert_days):
        days_until_expiration = (document.expiration_date - today).days
        if days_until_expiration < 0 or days_until_expiration > alert_days:
            return None
        if days_until_expiration <= urgent_alert_days:
            return None

        return DocumentExpirationEvent(
            event_type=DocumentExpirationNotification.EVENT_UPCOMING,
            priority=DocumentExpirationNotification.PRIORITY_MEDIUM,
            message=(
                f"Document '{document.name}' expires on {document.expiration_date}."
            ),
            log_message=(
                f"Expiration notification created for document '{document.name}' "
                f"with expiration date {document.expiration_date}."
            ),
        )


class ExpirationRecipientResolver:
    def resolve(self, document):
        student_recipients = list(document.case.users.filter(groups__name='student').distinct())
        advisor_recipients = list(User.objects.filter(groups__name='advisor').distinct())
        admin_recipients = list(User.objects.filter(groups__name='admin').distinct())

        recipients_by_id = {}
        for recipient in student_recipients + advisor_recipients + admin_recipients:
            recipients_by_id[recipient.id] = recipient

        return list(recipients_by_id.values())


class NotificationPersistenceObserver:
    def persist(self, *, document, recipients, event):
        created_notifications = []

        for recipient in recipients:
            notification, created = DocumentExpirationNotification.objects.get_or_create(
                document=document,
                recipient=recipient,
                event_type=event.event_type,
                defaults={
                    'priority': event.priority,
                    'message': event.message,
                },
            )
            if created:
                created_notifications.append(notification)

        return created_notifications


class CaseLogObserver:
    def log(self, *, document, content):
        case_user = document.case.created_by
        if document.case.users.filter(groups__name='student').exists():
            case_user = document.case.users.filter(groups__name='student').first()

        CaseLog.objects.create(
            case=document.case,
            user=case_user,
            content=content,
        )


class DocumentExpirationVerificationService:
    def __init__(
        self,
        *,
        rules=None,
        recipient_resolver=None,
        notification_observer=None,
        case_log_observer=None,
    ):
        self.rules = rules or [
            ExpiredDocumentRule(),
            UrgentUpcomingDocumentRule(),
            UpcomingDocumentRule(),
        ]
        self.recipient_resolver = recipient_resolver or ExpirationRecipientResolver()
        self.notification_observer = notification_observer or NotificationPersistenceObserver()
        self.case_log_observer = case_log_observer or CaseLogObserver()

    def verify(self, *, documents, today, alert_days):
        urgent_alert_days = getattr(settings, 'DOCUMENT_EXPIRATION_URGENT_ALERT_DAYS', 1)
        created_notifications = []

        for document in documents:
            recipients = self.recipient_resolver.resolve(document)
            if not recipients:
                continue

            for rule in self.rules:
                event = rule.build_event(
                    document=document,
                    today=today,
                    alert_days=alert_days,
                    urgent_alert_days=urgent_alert_days,
                )
                if event is None:
                    continue

                if event.should_mark_expired and not document.is_expired:
                    document.is_expired = True
                    document.save(update_fields=['is_expired'])

                notifications_for_event = self.notification_observer.persist(
                    document=document,
                    recipients=recipients,
                    event=event,
                )
                if notifications_for_event:
                    created_notifications.extend(notifications_for_event)
                    self.case_log_observer.log(document=document, content=event.log_message)

                break

        return created_notifications
