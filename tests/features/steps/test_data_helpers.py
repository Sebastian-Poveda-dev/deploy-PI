import json
import os
import subprocess
import time
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[3]
BACKEND_PYTHON = PROJECT_DIR / "backend" / "venv" / "Scripts" / "python.exe"


def unique_suffix():
    return str(int(time.time() * 1000))[-9:]


def run_django_shell(code):
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    result = subprocess.run(
        [str(BACKEND_PYTHON), "manage.py", "shell", "-c", code],
        cwd=PROJECT_DIR / "backend",
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def run_django_shell_json(code):
    output = run_django_shell(code)
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return json.loads(lines[-1]) if lines else None


def ensure_pending_case_for_advisor(advisor_username):
    code = f"""
import json
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from cases.models import Case, CaseAssignment, CaseLog, CaseStatus, Category, Subclinic

User = get_user_model()
advisor = User.objects.get(username={advisor_username!r})
pending_status = CaseStatus.objects.get(name='pending_authorization')
case = (
    Case.objects
    .filter(status=pending_status, assignments__user=advisor)
    .order_by('-id')
    .first()
)

if case is None:
    beneficiary_group = Group.objects.get(name='beneficiary')
    beneficiary = User.objects.filter(groups=beneficiary_group).order_by('id').first()
    if beneficiary is None:
        beneficiary = User.objects.create_user(
            username='beneficiario_selenium',
            password='ben1234',
            first_name='Beneficiario',
            last_name='Selenium',
            identification_number='990000001',
            phone_number='3000000001',
            residence_address='Direccion Selenium',
        )
        beneficiary.groups.add(beneficiary_group)

    category = advisor.category or Category.objects.order_by('id').first()
    if category is None:
        category = Category.objects.create(name='Civil')
    subclinic = Subclinic.objects.filter(category=category).order_by('id').first()
    if subclinic is None:
        subclinic = Subclinic.objects.create(name='Proceso', category=category)

    creator = User.objects.filter(groups__name='admin').order_by('id').first() or advisor
    case = Case.objects.create(
        description='Caso pendiente Selenium para aprobar por advisor',
        created_by=creator,
        category=category,
        subclinic=subclinic,
        status=pending_status,
        beneficiary=beneficiary,
    )
    CaseAssignment.objects.get_or_create(case=case, user=advisor)

    student = User.objects.filter(groups__name='student', is_active=True).order_by('id').first()
    if student is not None:
        CaseAssignment.objects.get_or_create(case=case, user=student)

    CaseLog.objects.create(
        case=case,
        user=creator,
        content=f'Caso pendiente preparado para prueba Selenium con advisor {{advisor.username}}.',
    )

print(json.dumps({{
    'id': case.id,
    'description': case.description,
    'advisor': advisor.username,
    'status': case.status.name,
}}, ensure_ascii=False))
"""
    return run_django_shell_json(code)


def create_assigned_case_for_advisor(advisor_username):
    suffix = unique_suffix()
    code = f"""
import json
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from cases.models import Case, CaseAssignment, CaseLog, CaseStatus, Category, Subclinic

User = get_user_model()
advisor = User.objects.get(username={advisor_username!r})
active_status = CaseStatus.objects.get(name='active')

beneficiary_group = Group.objects.get(name='beneficiary')
beneficiary = User.objects.filter(groups=beneficiary_group).order_by('id').first()
if beneficiary is None:
    beneficiary = User.objects.create_user(
        username='beneficiario_selenium_rechazo',
        password='ben1234',
        first_name='Beneficiario',
        last_name='Rechazo',
        identification_number='990000002',
        phone_number='3000000002',
        residence_address='Direccion Selenium',
    )
    beneficiary.groups.add(beneficiary_group)

category = advisor.category or Category.objects.order_by('id').first()
if category is None:
    category = Category.objects.create(name='Civil')
subclinic = Subclinic.objects.filter(category=category).order_by('id').first()
if subclinic is None:
    subclinic = Subclinic.objects.create(name='Proceso', category=category)

creator = User.objects.filter(groups__name='admin').order_by('id').first() or advisor
case = Case.objects.create(
    description='Caso asignado Selenium para rechazo {suffix}',
    created_by=creator,
    category=category,
    subclinic=subclinic,
    status=active_status,
    beneficiary=beneficiary,
)
CaseAssignment.objects.get_or_create(case=case, user=advisor)

student = User.objects.filter(groups__name='student', is_active=True).order_by('id').first()
if student is not None:
    CaseAssignment.objects.get_or_create(case=case, user=student)

CaseLog.objects.create(
    case=case,
    user=creator,
    content=f'Caso preparado para rechazo de asignacion por {{advisor.username}}.',
)

print(json.dumps({{
    'id': case.id,
    'description': case.description,
    'advisor': advisor.username,
    'advisor_last_name': advisor.last_name,
    'status': case.status.name,
}}, ensure_ascii=False))
"""
    return run_django_shell_json(code)


def create_assigned_case_for_student(student_username):
    suffix = unique_suffix()
    code = f"""
import json
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from cases.models import Case, CaseAssignment, CaseLog, CaseStatus, Category, Subclinic

User = get_user_model()
student = User.objects.get(username={student_username!r})
active_status = CaseStatus.objects.get(name='active')

advisor = User.objects.filter(groups__name='advisor', is_active=True).order_by('id').first()
category = (advisor.category if advisor and advisor.category_id else None) or Category.objects.order_by('id').first()
if category is None:
    category = Category.objects.create(name='Civil')

if advisor is None:
    advisor = User.objects.create_user(
        username='advisor_selenium_reasignacion',
        password='advisor1234',
        first_name='Advisor',
        last_name='Selenium',
    )
    advisor.groups.add(Group.objects.get(name='advisor'))
    advisor.category = category
    advisor.save(update_fields=['category'])

beneficiary_group = Group.objects.get(name='beneficiary')
beneficiary = User.objects.filter(groups=beneficiary_group).order_by('id').first()
if beneficiary is None:
    beneficiary = User.objects.create_user(
        username='beneficiario_selenium_reasignacion',
        password='ben1234',
        first_name='Beneficiario',
        last_name='Reasignacion',
        identification_number='990000003',
        phone_number='3000000003',
        residence_address='Direccion Selenium',
    )
    beneficiary.groups.add(beneficiary_group)

subclinic = Subclinic.objects.filter(category=category).order_by('id').first()
if subclinic is None:
    subclinic = Subclinic.objects.create(name='Proceso', category=category)

creator = User.objects.filter(groups__name='admin').order_by('id').first() or advisor
case = Case.objects.create(
    description='Caso asignado Selenium para solicitud de reasignacion {suffix}',
    created_by=creator,
    category=category,
    subclinic=subclinic,
    status=active_status,
    beneficiary=beneficiary,
)
CaseAssignment.objects.get_or_create(case=case, user=student)
CaseAssignment.objects.get_or_create(case=case, user=advisor)

CaseLog.objects.create(
    case=case,
    user=creator,
    content=f'Caso preparado para solicitud de reasignacion por {{student.username}}.',
)

print(json.dumps({{
    'id': case.id,
    'description': case.description,
    'student': student.username,
    'status': case.status.name,
}}, ensure_ascii=False))
"""
    return run_django_shell_json(code)
