from datetime import date

from django.core.management.base import BaseCommand

from documents.services import verify_document_expirations


class Command(BaseCommand):
    help = 'Verify document expirations and create notifications for matching events.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--today',
            type=date.fromisoformat,
            help='Optional reference date in YYYY-MM-DD format.',
        )
        parser.add_argument(
            '--alert-days',
            type=int,
            help='Optional alert range override in days.',
        )

    def handle(self, *args, **options):
        notifications = verify_document_expirations(
            today=options.get('today'),
            alert_days=options.get('alert_days'),
        )
        self.stdout.write(
            self.style.SUCCESS(f'Created {len(notifications)} notification(s).')
        )
