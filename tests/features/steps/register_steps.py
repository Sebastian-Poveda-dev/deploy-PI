import json
import os
import subprocess
import time
from pathlib import Path

from behave import given, then, when

from pages.register_page import RegisterPage


PROJECT_DIR = Path(__file__).resolve().parents[3]
BACKEND_PYTHON = PROJECT_DIR / "backend" / "venv" / "Scripts" / "python.exe"


def unique_registration_data():
    suffix = str(int(time.time() * 1000))[-9:]
    return {
        "first_name": "Prueba",
        "last_name": f"Automatizada {suffix}",
        "email": f"beneficiario{suffix}@example.com",
        "identification_number": f"88{suffix}",
        "phone_number": "3001234567",
        "residence_address": "Calle 1 # 2-03",
    }


def backend_extra_info(identification_number):
    code = (
        "import json;"
        "from django.contrib.auth import get_user_model;"
        "User=get_user_model();"
        f"u=User.objects.get(identification_number='{identification_number}');"
        "print(json.dumps(u.extra_info or {}, ensure_ascii=False))"
    )
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
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return json.loads(lines[-1]) if lines else {}


@given("el visitante esta en la pagina de registro")
def step_open_register(context):
    context.register_page = RegisterPage(context.driver)
    context.register_page.open()


@when("registra un beneficiario nuevo con todos los campos obligatorios")
def step_register_required(context):
    data = unique_registration_data()
    context.created_registration = data
    context.register_page.fill_required_fields(data)
    context.register_page.submit()


@when("intenta registrarse sin campos obligatorios")
def step_register_empty(context):
    context.register_page.submit()


@then("ve errores de validacion del registro")
def step_register_validation_errors(context):
    assert context.register_page.has_text("Completa los campos obligatorios"), context.register_page.visible_text()


@when('registra un beneficiario con identificacion existente "{identification_number}"')
def step_register_existing_id(context, identification_number):
    data = unique_registration_data()
    data["identification_number"] = identification_number
    context.created_registration = data
    context.register_page.fill_required_fields(data)
    context.register_page.submit()


@then("ve un error del backend por identificacion existente")
def step_backend_duplicate_error(context):
    text = context.register_page.error_message()
    assert text, "Expected backend validation error to be visible"


@when('registra un beneficiario nuevo con el campo adicional "{key}" igual a "{value}"')
def step_register_with_extra_field(context, key, value):
    data = unique_registration_data()
    context.created_registration = data
    context.created_extra_field = (key, value)
    context.register_page.fill_required_fields(data)
    context.register_page.fill_optional_defaults()
    context.register_page.add_extra_field(key, value)
    context.register_page.submit()


@then('el beneficiario registrado conserva el campo adicional "{key}" igual a "{value}"')
def step_verify_extra_field_saved(context, key, value):
    extra_info = backend_extra_info(context.created_registration["identification_number"])
    assert extra_info.get(key) == value, extra_info


@when("agrega y elimina un campo adicional antes de registrar")
def step_add_remove_extra_field(context):
    context.register_page.add_extra_field("campo_temporal", "valor temporal")
    context.register_page.remove_last_extra_field()


@then("no quedan campos adicionales visibles")
def step_no_extra_fields_visible(context):
    assert context.register_page.extra_fields_count() == 0


@when("completa y envia el registro sin campos adicionales")
def step_register_without_extra_fields(context):
    data = unique_registration_data()
    context.created_registration = data
    context.register_page.fill_required_fields(data)
    context.register_page.submit()


@then("el beneficiario registrado no conserva campos adicionales")
def step_verify_no_extra_fields(context):
    assert backend_extra_info(context.created_registration["identification_number"]) == {}
