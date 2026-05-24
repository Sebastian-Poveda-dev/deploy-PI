from behave import then, when

from pages.permissions_page import PermissionsPage
from features.steps.test_data_helpers import unique_suffix


@when("abre la pagina de permisos")
def step_open_permissions(context):
    context.permissions_page = PermissionsPage(context.driver)
    context.permissions_page.open()
    context.permissions_page.wait_for_table()


@then("la tabla de permisos muestra sus columnas principales")
def step_permissions_table_headers(context):
    assert context.permissions_page.has_table_headers([
        "Nombre",
        "Usuario",
        "Rol",
        "Sala",
        "Estado",
        "Acciones",
    ])


@then("la tabla de permisos muestra los usuarios seed")
def step_permissions_seed_users(context):
    assert context.permissions_page.has_users(["admin", "a.torres", "s.vargas"])


@then('el usuario "{username}" muestra rol "{role}" y una sala')
def step_user_role_and_sala(context, username, role):
    assert context.permissions_page.user_has_role(username, role)
    assert context.permissions_page.user_has_sala(username)


@then('el usuario "{username}" muestra rol "{role}"')
def step_user_role(context, username, role):
    assert context.permissions_page.user_has_role(username, role)


@when("intenta crear un usuario advisor sin seleccionar sala")
def step_create_advisor_without_sala(context):
    suffix = unique_suffix()
    context.new_permissions_username = f"advisor_sin_sala_{suffix}"
    context.permissions_page.open_create_modal()
    context.permissions_page.fill_create_user({
        "first_name": "Advisor",
        "last_name": "Sin Sala",
        "username": context.new_permissions_username,
        "password": "advisor1234",
        "role": "Asesor",
    })
    context.permissions_page.submit_modal()


@then("ve error de validacion por sala legal requerida")
def step_sala_validation_error(context):
    assert context.permissions_page.sala_required_error_is_visible()


@then("el modal de crear usuario sigue abierto")
def step_create_user_modal_still_open(context):
    assert context.permissions_page.create_modal_is_open()
