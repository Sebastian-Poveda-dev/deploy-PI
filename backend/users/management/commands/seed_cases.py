from django.core.management.base import BaseCommand

from cases.models import Category, Subclinic, CaseStatus
from cases.services import create_case, create_case_log
from django.apps import apps
from django.conf import settings

User = apps.get_model(settings.AUTH_USER_MODEL)

SUBCLINICS = ['civil', 'laboral', 'penal', 'familia']

SEED_CASES = [
    {
        'created_by': 'student',
        'professor': 'professor',
        'description': 'Despido sin justa causa después de 5 años de servicio.',
        'category': 'laboral',
        'subclinic': 'laboral',
        'logs': [
            ('student', 'Solicito revisión del contrato laboral.'),
        ],
    },
    {
        'created_by': 'student',
        'professor': 'professor',
        'description': 'Acoso laboral por parte de supervisor inmediato.',
        'category': 'laboral',
        'subclinic': 'laboral',
        'logs': [
            ('student', 'Presento evidencia del acoso.'),
        ],
    },
    {
        'created_by': 'admin',
        'professor': None,
        'description': 'Disputa por herencia entre hermanos tras fallecimiento del padre.',
        'category': 'penal',
        'subclinic': 'civil',
        'logs': [
            ('admin', 'Caso registrado.'),
        ],
    },
    {
        'created_by': 'professor',
        'professor': None,
        'description': 'Custodia de menores en proceso de separación conyugal.',
        'category': 'laboral',
        'subclinic': 'familia',
        'logs': [
            ('professor', 'Se inicia análisis del caso familiar.'),
        ],
    },
    {
        'created_by': 'student',
        'professor': 'professor',
        'description': 'Incumplimiento de contrato de arrendamiento comercial.',
        'category': 'penal',
        'subclinic': 'civil',
        'logs': [],
    },
]


class Command(BaseCommand):
    help = 'Create seed cases for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete all existing cases before creating seed data',
        )

    def handle(self, *args, **options):
        from cases.models import Case

        if options['flush']:
            deleted, _ = Case.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {deleted} existing case(s).'))

        # Ensure subclinics exist
        for name in SUBCLINICS:
            Subclinic.objects.get_or_create(name=name)
        self.stdout.write('Subclinics ready.')

        created = 0
        for data in SEED_CASES:
            creator = User.objects.filter(username=data['created_by']).first()
            if not creator:
                self.stdout.write(
                    self.style.WARNING(f"  Skipped — user '{data['created_by']}' not found. Run seed_users first.")
                )
                continue

            category = Category.objects.get(name=data['category'])
            subclinic = Subclinic.objects.get(name=data['subclinic'])

            professor = None
            if data.get('professor'):
                professor = User.objects.filter(username=data['professor']).first()
                if not professor:
                    self.stdout.write(
                        self.style.WARNING(f"  Skipped — professor '{data['professor']}' not found.")
                    )
                    continue

            beneficiary = User.objects.filter(groups__name='beneficiary').order_by('id').first()
            if not beneficiary:
                self.stdout.write(
                    self.style.WARNING("  Skipped — no beneficiary user found. Run seed_users first.")
                )
                continue

            case = create_case(
                creator,
                data['description'],
                category,
                subclinic,
                beneficiary=beneficiary,
                professor=professor,
            )

            for username, content in data['logs']:
                user = User.objects.filter(username=username).first()
                if user:
                    create_case_log(user, case, content)

            self.stdout.write(
                self.style.SUCCESS(f"  Created  case #{case.id} by '{creator.username}' [{case.status.name}]")
            )
            created += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Done — {created} case(s) created.'))
