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
        'description': 'Despido sin justa causa después de 5 años de servicio.',
        'category': 'laboral',
        'subclinic': 'laboral',
        'extra_users': ['professor', 'advisor'],
        'logs': [
            ('student', 'Solicito revisión del contrato laboral.'),
            ('professor', 'Se revisó el contrato. Hay fundamentos para proceder.'),
            ('advisor', 'Caso aprobado para continuar.'),
        ],
    },
    {
        'created_by': 'student',
        'description': 'Acoso laboral por parte de supervisor inmediato.',
        'category': 'laboral',
        'subclinic': 'laboral',
        'extra_users': ['professor'],
        'logs': [
            ('student', 'Presento evidencia del acoso.'),
            ('professor', 'Se analizará la documentación aportada.'),
        ],
    },
    {
        'created_by': 'admin',
        'description': 'Disputa por herencia entre hermanos tras fallecimiento del padre.',
        'category': 'penal',
        'subclinic': 'civil',
        'extra_users': ['student'],
        'logs': [
            ('admin', 'Caso registrado. Se asignó estudiante para seguimiento.'),
        ],
    },
    {
        'created_by': 'professor',
        'description': 'Custodia de menores en proceso de separación conyugal.',
        'category': 'laboral',
        'subclinic': 'familia',
        'extra_users': ['student', 'advisor'],
        'logs': [
            ('professor', 'Se inicia análisis del caso familiar.'),
            ('student', 'Revisando documentación de los menores.'),
        ],
    },
    {
        'created_by': 'student',
        'description': 'Incumplimiento de contrato de arrendamiento comercial.',
        'category': 'penal',
        'subclinic': 'civil',
        'extra_users': [],
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

            case = create_case(creator, data['description'], category, subclinic)

            for username in data['extra_users']:
                user = User.objects.filter(username=username).first()
                if user:
                    case.users.add(user)

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
