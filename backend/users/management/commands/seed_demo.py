"""
Management command: seed_demo

Usage:
    python manage.py seed_demo            # seed without touching existing data
    python manage.py seed_demo --flush    # wipe all user/case/document data first, then seed

Creates:
    - 1 admin
    - 1 advisor per sala (6 total)
    - 8 students
    - 10 beneficiaries (basic registration fields + cédula)
    - 15 cases across salas with logs
    - ~20 documents (urgent / near-expiry / sin vencimiento)
    - 3 pending reassignment requests (not yet approved)
"""

from datetime import date, timedelta

from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

ADMIN = {
    'username': 'admin',
    'password': 'admin1234',
    'first_name': 'Administrador',
    'last_name': 'Sistema',
    'email': 'admin@consultorio.edu.co',
    'phone_number': '6013200001',
    'identification_number': '79000001',
}

# One advisor per sala — category must match the sala name exactly
ADVISORS = [
    {
        'username': 'a.torres', 'password': 'advisor1234',
        'first_name': 'Andrés', 'last_name': 'Torres',
        'email': 'a.torres@consultorio.edu.co',
        'phone_number': '3101000001', 'identification_number': '79100001',
        'sala': 'Civil',
    },
    {
        'username': 'm.garcia', 'password': 'advisor1234',
        'first_name': 'María', 'last_name': 'García',
        'email': 'm.garcia@consultorio.edu.co',
        'phone_number': '3101000002', 'identification_number': '52100002',
        'sala': 'Laboral',
    },
    {
        'username': 'j.rodriguez', 'password': 'advisor1234',
        'first_name': 'Julián', 'last_name': 'Rodríguez',
        'email': 'j.rodriguez@consultorio.edu.co',
        'phone_number': '3101000003', 'identification_number': '79100003',
        'sala': 'Penal',
    },
    {
        'username': 'c.lopez', 'password': 'advisor1234',
        'first_name': 'Carolina', 'last_name': 'López',
        'email': 'c.lopez@consultorio.edu.co',
        'phone_number': '3101000004', 'identification_number': '52100004',
        'sala': 'Familia',
    },
    {
        'username': 'l.martinez', 'password': 'advisor1234',
        'first_name': 'Laura', 'last_name': 'Martínez',
        'email': 'l.martinez@consultorio.edu.co',
        'phone_number': '3101000005', 'identification_number': '52100005',
        'sala': 'Derecho público',
    },
    {
        'username': 'p.hernandez', 'password': 'advisor1234',
        'first_name': 'Pablo', 'last_name': 'Hernández',
        'email': 'p.hernandez@consultorio.edu.co',
        'phone_number': '3101000006', 'identification_number': '79100006',
        'sala': 'Derecho público - Migrantes',
    },
]

STUDENTS = [
    {
        'username': 's.vargas', 'password': 'student1234',
        'first_name': 'Santiago', 'last_name': 'Vargas',
        'email': 's.vargas@universidad.edu.co',
        'phone_number': '3201000001', 'identification_number': '1020000001',
    },
    {
        'username': 'd.moreno', 'password': 'student1234',
        'first_name': 'Daniela', 'last_name': 'Moreno',
        'email': 'd.moreno@universidad.edu.co',
        'phone_number': '3201000002', 'identification_number': '1020000002',
    },
    {
        'username': 'v.castillo', 'password': 'student1234',
        'first_name': 'Valentina', 'last_name': 'Castillo',
        'email': 'v.castillo@universidad.edu.co',
        'phone_number': '3201000003', 'identification_number': '1020000003',
    },
    {
        'username': 'f.reyes', 'password': 'student1234',
        'first_name': 'Felipe', 'last_name': 'Reyes',
        'email': 'f.reyes@universidad.edu.co',
        'phone_number': '3201000004', 'identification_number': '1020000004',
    },
    {
        'username': 'n.romero', 'password': 'student1234',
        'first_name': 'Natalia', 'last_name': 'Romero',
        'email': 'n.romero@universidad.edu.co',
        'phone_number': '3201000005', 'identification_number': '1020000005',
    },
    {
        'username': 'e.silva', 'password': 'student1234',
        'first_name': 'Esteban', 'last_name': 'Silva',
        'email': 'e.silva@universidad.edu.co',
        'phone_number': '3201000006', 'identification_number': '1020000006',
    },
    {
        'username': 'k.gutierrez', 'password': 'student1234',
        'first_name': 'Karen', 'last_name': 'Gutiérrez',
        'email': 'k.gutierrez@universidad.edu.co',
        'phone_number': '3201000007', 'identification_number': '1020000007',
    },
    {
        'username': 'r.mendoza', 'password': 'student1234',
        'first_name': 'Ricardo', 'last_name': 'Mendoza',
        'email': 'r.mendoza@universidad.edu.co',
        'phone_number': '3201000008', 'identification_number': '1020000008',
    },
]

BENEFICIARIES = [
    {
        'username': 'jperez', 'password': 'ben1234',
        'first_name': 'Juan', 'last_name': 'Pérez',
        'email': 'jperez@gmail.com', 'phone_number': '3001000001',
        'identification_number': '1001234567', 'residence_address': 'Cra 7 # 45-12, Bogotá',
    },
    {
        'username': 'mlopez', 'password': 'ben1234',
        'first_name': 'María', 'last_name': 'López',
        'email': 'mlopez@hotmail.com', 'phone_number': '3002000002',
        'identification_number': '1002345678', 'residence_address': 'Calle 80 # 23-10, Bogotá',
    },
    {
        'username': 'crodriguez', 'password': 'ben1234',
        'first_name': 'Carlos', 'last_name': 'Rodríguez',
        'email': 'crodriguez@yahoo.com', 'phone_number': '3003000003',
        'identification_number': '1003456789', 'residence_address': 'Av. Caracas # 32-55, Bogotá',
    },
    {
        'username': 'amartinez', 'password': 'ben1234',
        'first_name': 'Ana', 'last_name': 'Martínez',
        'email': 'amartinez@gmail.com', 'phone_number': '3004000004',
        'identification_number': '1004567890', 'residence_address': 'Cra 15 # 67-30, Bogotá',
    },
    {
        'username': 'lgarcia', 'password': 'ben1234',
        'first_name': 'Luis', 'last_name': 'García',
        'email': 'lgarcia@gmail.com', 'phone_number': '3005000005',
        'identification_number': '1005678901', 'residence_address': 'Calle 100 # 14-23, Bogotá',
    },
    {
        'username': 'shernandez', 'password': 'ben1234',
        'first_name': 'Sofía', 'last_name': 'Hernández',
        'email': 'shernandez@hotmail.com', 'phone_number': '3006000006',
        'identification_number': '1006789012', 'residence_address': 'Cra 30 # 12-45, Bogotá',
    },
    {
        'username': 'mtorres', 'password': 'ben1234',
        'first_name': 'Miguel', 'last_name': 'Torres',
        'email': 'mtorres@gmail.com', 'phone_number': '3007000007',
        'identification_number': '1007890123', 'residence_address': 'Calle 63 # 9-42, Bogotá',
    },
    {
        'username': 'cramirez', 'password': 'ben1234',
        'first_name': 'Claudia', 'last_name': 'Ramírez',
        'email': 'cramirez@yahoo.com', 'phone_number': '3008000008',
        'identification_number': '1008901234', 'residence_address': 'Cra 50 # 20-10, Bogotá',
    },
    {
        'username': 'acastillo', 'password': 'ben1234',
        'first_name': 'Andrés', 'last_name': 'Castillo',
        'email': 'acastillo@gmail.com', 'phone_number': '3009000009',
        'identification_number': '1009012345', 'residence_address': 'Calle 26 # 40-60, Bogotá',
    },
    {
        'username': 'pmoreno', 'password': 'ben1234',
        'first_name': 'Patricia', 'last_name': 'Moreno',
        'email': 'pmoreno@hotmail.com', 'phone_number': '3000000010',
        'identification_number': '1000123456', 'residence_address': 'Cra 13 # 55-22, Bogotá',
    },
]

# (sala, subclinic_name, description, creator_role, extra_logs, set_in_progress)
CASES = [
    (
        'Laboral', 'Proceso',
        'Despido sin justa causa tras 8 años de servicio en empresa de manufactura.',
        'admin',
        ['Se adjuntaron liquidación y contrato laboral.', 'Empleador no respondió citación.'],
        True,
    ),
    (
        'Laboral', 'Tutela',
        'Empleador no paga salario desde hace tres meses a trabajadora en estado de embarazo.',
        'student',
        ['Se radicó tutela ante juzgado civil.'],
        False,
    ),
    (
        'Laboral', 'Liquidación + concepto',
        'Trabajador solicita revisión de liquidación final de contrato a término fijo.',
        'admin',
        ['Se verificó cálculo de prestaciones sociales.'],
        True,
    ),
    (
        'Civil', 'Proceso',
        'Incumplimiento de contrato de compraventa de inmueble por parte del vendedor.',
        'admin',
        ['Se notificó al demandado.', 'Audiencia inicial programada para el mes siguiente.'],
        True,
    ),
    (
        'Civil', 'Tutela',
        'Arrendatario solicita amparo ante desalojo arbitrario sin proceso judicial.',
        'student',
        [],
        False,
    ),
    (
        'Civil', 'Cobro pre-jurídico',
        'Cobro de deuda por servicios profesionales prestados y no cancelados.',
        'admin',
        ['Carta de cobro enviada al deudor.'],
        False,
    ),
    (
        'Penal', 'Concepto + denuncia',
        'Víctima de hurto calificado solicita orientación para denuncia y reparación.',
        'admin',
        ['Se interpuso denuncia ante la Fiscalía.'],
        True,
    ),
    (
        'Penal', 'Derecho de petición',
        'Ciudadano solicita información sobre proceso penal en su contra sin acceso a expediente.',
        'student',
        [],
        False,
    ),
    (
        'Familia', 'Proceso',
        'Madre solicita regulación de cuota alimentaria para dos hijos menores de edad.',
        'admin',
        ['Padres citados a audiencia de conciliación.', 'Acuerdo parcial alcanzado.'],
        True,
    ),
    (
        'Familia', 'Tutela',
        'Abuelos solicitan amparo del derecho de visita a nietos tras separación de los padres.',
        'student',
        ['Se documentaron visitas negadas.'],
        False,
    ),
    (
        'Familia', 'Concepto + DP',
        'Persona solicita orientación sobre proceso de adopción de sobrino huérfano.',
        'admin',
        [],
        False,
    ),
    (
        'Derecho público', 'Tutela',
        'Paciente con enfermedad crónica a quien EPS niega medicamento de alto costo.',
        'admin',
        ['Tutela radicada. Juez ordenó entrega provisional del medicamento.'],
        True,
    ),
    (
        'Derecho público', 'Derecho de petición',
        'Ciudadano solicita respuesta a petición enviada hace 6 meses a entidad pública.',
        'student',
        [],
        False,
    ),
    (
        'Derecho público - Migrantes', 'Solicitud de refugio',
        'Familia venezolana solicita orientación para proceso de regularización migratoria.',
        'admin',
        ['Se inició trámite de solicitud de refugio ante Cancillería.'],
        True,
    ),
    (
        'Derecho público - Migrantes', 'Tutela',
        'Migrante sin documentos es negado en servicio de urgencias hospitalarias.',
        'student',
        ['Se presentó tutela por violación del derecho a la salud.'],
        False,
    ),
]

# Documents: (case_index_0based, name, description, expiry_offset_days or None)
# Negative offset = already expired, None = no expiry
DOCUMENTS = [
    (0, 'Contrato laboral', 'Contrato original firmado por ambas partes.', None),
    (0, 'Carta de despido', 'Comunicación de terminación sin justa causa.', 45),
    (0, 'Liquidación de prestaciones', 'Cálculo de liquidación final del empleador.', 8),
    (1, 'Prueba de embarazo', 'Certificado médico de estado de gestación.', 2),
    (1, 'Historial de pagos', 'Extractos bancarios de los últimos 6 meses.', None),
    (2, 'Contrato a término fijo', 'Contrato de trabajo con cláusulas de renovación.', None),
    (3, 'Promesa de compraventa', 'Documento notariado de la promesa de venta.', 2),
    (3, 'Escritura pública', 'Escritura del inmueble objeto de controversia.', None),
    (4, 'Contrato de arrendamiento', 'Contrato vigente de arrendamiento del inmueble.', 8),
    (6, 'Denuncia penal', 'Copia de la denuncia radicada ante la Fiscalía.', None),
    (7, 'Solicitud de información', 'Derecho de petición enviado a la entidad.', 2),
    (8, 'Acta de audiencia', 'Acta de audiencia de conciliación alimentaria.', 15),
    (8, 'Registro civil de los menores', 'Registros civiles de nacimiento de los hijos.', None),
    (11, 'Historia clínica', 'Historial médico del paciente con diagnóstico.', None),
    (11, 'Negación de servicio EPS', 'Comunicación de la EPS negando el medicamento.', 8),
    (12, 'Derecho de petición original', 'Copia del DP enviado hace 6 meses.', 2),
    (13, 'Formulario solicitud refugio', 'Formulario diligenciado para solicitud de refugio.', None),
    (13, 'Pasaportes familia', 'Copias de documentos de identidad de todos los integrantes.', 15),
    (14, 'Carnet de urgencias', 'Documento de atención de urgencias negada.', None),
    (14, 'Tutela radicada', 'Copia de la tutela presentada ante el juzgado.', 2),
]

# Progress statuses: (case_index_0based, [labels in chronological order])
PROGRESS_STATUSES = [
    (0, [
        'Entrevista inicial con el cliente realizada.',
        'Documentos laborales recibidos y verificados.',
        'Demanda laboral radicada ante el juzgado.',
    ]),
    (2, [
        'Revisión de contrato a término fijo completada.',
        'Cálculo de prestaciones sociales verificado.',
    ]),
    (3, [
        'Revisión de promesa de compraventa realizada.',
        'Notificación al demandado enviada.',
        'Audiencia inicial programada.',
    ]),
    (6, [
        'Denuncia radicada ante la Fiscalía.',
        'Número de radicado asignado al proceso.',
    ]),
    (8, [
        'Entrevista con la madre y los hijos realizada.',
        'Citación enviada al padre para audiencia de conciliación.',
        'Audiencia realizada — acuerdo parcial alcanzado.',
        'Acta de conciliación suscrita por ambas partes.',
    ]),
    (11, [
        'Tutela radicada ante el juzgado civil.',
        'Juez admitió la tutela y ordenó respuesta a la EPS en 48 horas.',
        'EPS entregó medicamento provisionalmente por orden judicial.',
    ]),
    (13, [
        'Entrevista inicial con la familia realizada.',
        'Formulario de solicitud de refugio diligenciado.',
        'Solicitud radicada ante la Cancillería.',
    ]),
]

# Pending reassignment requests: (case_index_0based, reason)
PENDING_REASSIGNMENTS = [
    (1, 'Mi carga académica aumentó significativamente este semestre y no puedo atender el caso con la dedicación requerida.'),
    (7, 'Tengo un conflicto de interés potencial con el demandado en este proceso penal.'),
    (14, 'Me encuentro en período de prácticas externas y no dispongo del tiempo para el seguimiento del caso.'),
]


class Command(BaseCommand):
    help = 'Crea datos de demostración realistas: admin, asesores por sala, estudiantes, beneficiarios, casos y documentos.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Elimina todos los usuarios, casos y documentos existentes antes de sembrar los datos.',
        )
        parser.add_argument(
            '--if-empty',
            action='store_true',
            help='Solo siembra datos si la base de datos está vacía (sin usuarios). Útil en el start command de producción.',
        )

    def handle(self, *args, **options):
        if options['if_empty']:
            from users.models import User
            if User.objects.exists():
                self.stdout.write(self.style.WARNING('Base de datos ya tiene usuarios — seed omitido.'))
                return

        if options['flush']:
            self._flush()

        self._ensure_lookup_data()
        users = self._create_users()
        cases = self._create_cases(users)
        self._create_progress_statuses(cases)
        self._create_documents(cases, users)
        self._create_cancellation_requests(cases, users)

        self._print_credentials()

    # ------------------------------------------------------------------
    # Flush
    # ------------------------------------------------------------------

    def _flush(self):
        from django.contrib.sessions.models import Session
        from documents.models import Document
        from cases.models import Case
        from communications.models import Message, ConversationParticipant, Conversation
        from django.apps import apps
        from django.conf import settings

        User = apps.get_model(settings.AUTH_USER_MODEL)

        self.stdout.write(self.style.WARNING('Eliminando datos existentes...'))

        Session.objects.all().delete()
        Message.objects.all().delete()
        ConversationParticipant.objects.all().delete()
        Conversation.objects.all().delete()
        Document.objects.all().delete()
        Case.objects.all().delete()
        deleted, _ = User.objects.all().delete()
        self.stdout.write(self.style.WARNING(f'  {deleted} usuario(s) eliminado(s).'))

    # ------------------------------------------------------------------
    # Lookup data (groups, statuses, categories, subclinics)
    # ------------------------------------------------------------------

    def _ensure_lookup_data(self):
        from cases.models import CaseStatus, Category, Subclinic

        for role in ('admin', 'advisor', 'student', 'beneficiary'):
            Group.objects.get_or_create(name=role)

        for status in ('active', 'pending_authorization', 'in_progress', 'finished', 'inactive', 'canceled'):
            CaseStatus.objects.get_or_create(name=status)

        salas_and_procesos = {
            'Civil': ['Proceso', 'Cobro pre-jurídico', 'Tutela', 'Derecho de petición', 'Concepto + DP', 'Queja', 'Memorial', 'Concepto', 'Clínica empresarial'],
            'Laboral': ['Proceso', 'Liquidación + concepto', 'Tutela', 'Derecho de petición', 'Concepto', 'Queja', 'Memorial'],
            'Penal': ['Proceso', 'Derecho de petición', 'Concepto + denuncia', 'Concepto', 'Memorial'],
            'Familia': ['Proceso', 'Concepto + DP', 'Derecho de petición', 'Tutela', 'Memorial', 'Queja', 'Cobro pre-jurídico', 'Concepto'],
            'Derecho público': ['Proceso', 'Concepto + DP', 'Derecho de petición', 'Tutela', 'Memorial', 'Queja', 'Cobro pre-jurídico', 'Concepto'],
            'Derecho público - Migrantes': ['Solicitud de refugio', 'Solicitud de refugio + DP', 'Solicitud de refugio + Tutela', 'Trámite salvoconducto', 'Tutela', 'Concepto + DP', 'Derecho de petición', 'Concepto'],
        }
        for sala_name, procesos in salas_and_procesos.items():
            cat, _ = Category.objects.get_or_create(name=sala_name)
            for proceso in procesos:
                Subclinic.objects.get_or_create(name=proceso, category=cat)

        self.stdout.write('  Datos de referencia listos.')

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------

    def _create_users(self):
        from django.apps import apps
        from django.conf import settings
        from cases.models import Category

        User = apps.get_model(settings.AUTH_USER_MODEL)

        self.stdout.write('\nCreando usuarios...')
        created = {}

        def make_user(data, role, category_name=None):
            username = data['username']
            if User.objects.filter(username=username).exists():
                self.stdout.write(f"  Omitido  '{username}' (ya existe)")
                return User.objects.get(username=username)

            user = User.objects.create_user(
                username=username,
                password=data['password'],
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                email=data.get('email', ''),
                phone_number=data.get('phone_number', ''),
                identification_number=data.get('identification_number', ''),
                residence_address=data.get('residence_address', ''),
            )
            group = Group.objects.get(name=role)
            user.groups.add(group)

            if category_name:
                cat = Category.objects.filter(name=category_name).first()
                if cat:
                    user.category = cat
                    user.save(update_fields=['category'])

            self.stdout.write(self.style.SUCCESS(f"  Creado   '{username}' ({role})"))
            return user

        created['admin'] = make_user(ADMIN, 'admin')

        created['advisors'] = []
        for adv in ADVISORS:
            u = make_user(adv, 'advisor', category_name=adv['sala'])
            created['advisors'].append(u)

        created['students'] = []
        for stu in STUDENTS:
            u = make_user(stu, 'student')
            created['students'].append(u)

        created['beneficiaries'] = []
        for ben in BENEFICIARIES:
            u = make_user(ben, 'beneficiary')
            created['beneficiaries'].append(u)

        return created

    # ------------------------------------------------------------------
    # Cases
    # ------------------------------------------------------------------

    def _create_cases(self, users):
        from django.apps import apps
        from django.conf import settings
        from cases.models import Case, CaseStatus, Category, Subclinic
        from cases.services import create_case, create_case_log

        User = apps.get_model(settings.AUTH_USER_MODEL)

        self.stdout.write('\nCreando casos...')

        admin = users['admin']
        students = users['students']
        beneficiaries = users['beneficiaries']
        created_cases = []

        for i, (sala_name, subclinic_name, description, creator_role, extra_logs, set_in_progress) in enumerate(CASES):
            category = Category.objects.filter(name=sala_name).first()
            subclinic = Subclinic.objects.filter(name=subclinic_name, category=category).first()
            if not category or not subclinic:
                self.stdout.write(self.style.WARNING(f'  Caso {i+1}: sala o subclinica no encontrada, omitido.'))
                created_cases.append(None)
                continue

            beneficiary = beneficiaries[i % len(beneficiaries)]

            if creator_role == 'student':
                creator = students[i % len(students)]
            else:
                creator = admin

            try:
                with transaction.atomic():
                    case = create_case(creator, description, category, subclinic, beneficiary=beneficiary)

                    if set_in_progress:
                        in_progress = CaseStatus.objects.get(name='in_progress')
                        Case.objects.filter(pk=case.pk).update(status=in_progress)
                        case.refresh_from_db()

                    for log_text in extra_logs:
                        # Log authored by the assigned advisor of this case
                        assigned = case.users.filter(groups__name='advisor').first() or creator
                        create_case_log(assigned, case, log_text)

                created_cases.append(case)
                self.stdout.write(self.style.SUCCESS(
                    f'  Caso #{case.id:>3} — {sala_name} / {subclinic_name} [{case.status.name}]'
                ))
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f'  Error en caso {i+1}: {exc}'))
                created_cases.append(None)

        return created_cases

    # ------------------------------------------------------------------
    # Progress statuses
    # ------------------------------------------------------------------

    def _create_progress_statuses(self, cases):
        from cases.models import CaseProgressStatus

        self.stdout.write('\nCreando estados de progreso...')
        count = 0

        for case_idx, labels in PROGRESS_STATUSES:
            if case_idx >= len(cases) or cases[case_idx] is None:
                continue

            case = cases[case_idx]
            author = case.users.filter(groups__name='advisor').first() \
                or case.users.filter(groups__name='student').first() \
                or case.created_by

            for label in labels:
                CaseProgressStatus.objects.create(case=case, label=label, created_by=author)
                count += 1

            self.stdout.write(self.style.SUCCESS(
                f'  Caso #{case.id} — {len(labels)} estado(s) de progreso agregado(s).'
            ))

        self.stdout.write(f'  {count} estado(s) de progreso creado(s) en total.')

    # ------------------------------------------------------------------
    # Documents
    # ------------------------------------------------------------------

    def _create_documents(self, cases, users):
        from documents.models import Document

        self.stdout.write('\nCreando documentos...')
        today = date.today()
        admin = users['admin']
        count = 0

        for case_idx, name, description, expiry_offset in DOCUMENTS:
            if case_idx >= len(cases) or cases[case_idx] is None:
                continue

            case = cases[case_idx]
            expiration_date = (today + timedelta(days=expiry_offset)) if expiry_offset is not None else None

            uploader = case.users.filter(groups__name__in=['advisor', 'student']).first() or admin

            slug = name.lower().replace(' ', '_').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
            filename = f'{slug}.pdf'

            dummy_content = f'%PDF-1.4\n% Documento de demostración: {name}\n% Caso #{case.id}\n'.encode()

            doc = Document(
                name=name,
                description=description,
                case=case,
                uploaded_by=uploader,
                expiration_date=expiration_date,
            )
            doc.file.save(filename, ContentFile(dummy_content), save=True)

            if expiry_offset is None:
                label = 'sin vencimiento'
            elif expiry_offset <= 3:
                label = f'URGENTE (vence en {expiry_offset}d)'
            elif expiry_offset <= 10:
                label = f'próximo a vencer ({expiry_offset}d)'
            else:
                label = f'vence en {expiry_offset}d'

            self.stdout.write(self.style.SUCCESS(f'  Doc: "{name}" → Caso #{case.id} [{label}]'))
            count += 1

        self.stdout.write(f'  {count} documento(s) creado(s).')

    # ------------------------------------------------------------------
    # Pending reassignment requests
    # ------------------------------------------------------------------

    def _create_cancellation_requests(self, cases, users):
        from cases.models import CaseCancellationRequest

        self.stdout.write('\nCreando solicitudes de reasignación pendientes...')
        count = 0

        for case_idx, reason in PENDING_REASSIGNMENTS:
            if case_idx >= len(cases) or cases[case_idx] is None:
                continue

            case = cases[case_idx]
            student = case.users.filter(groups__name='student').first()
            if not student:
                continue

            if CaseCancellationRequest.objects.filter(case=case, status=CaseCancellationRequest.PENDING).exists():
                continue

            CaseCancellationRequest.objects.create(
                case=case,
                requested_by=student,
                reason=reason,
                status=CaseCancellationRequest.PENDING,
            )
            self.stdout.write(self.style.SUCCESS(
                f'  Solicitud pendiente: Caso #{case.id} por {student.username}'
            ))
            count += 1

        self.stdout.write(f'  {count} solicitud(es) creada(s).')

    # ------------------------------------------------------------------
    # Credentials summary
    # ------------------------------------------------------------------

    def _print_credentials(self):
        self.stdout.write('\n' + '─' * 55)
        self.stdout.write(self.style.SUCCESS('Datos de demostración listos.\n'))
        self.stdout.write('Credenciales:')
        self.stdout.write(f"  {'Rol':<12} {'Usuario':<20} Contraseña")
        self.stdout.write('  ' + '─' * 48)
        self.stdout.write(f"  {'admin':<12} {'admin':<20} admin1234")
        for adv in ADVISORS:
            self.stdout.write(f"  {'advisor':<12} {adv['username']:<20} advisor1234  ({adv['sala']})")
        for stu in STUDENTS:
            self.stdout.write(f"  {'student':<12} {stu['username']:<20} student1234")
        self.stdout.write(f"  {'beneficiario':<12} jperez … pmoreno    ben1234")
        self.stdout.write('─' * 55 + '\n')
