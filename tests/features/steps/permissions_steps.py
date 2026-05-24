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


@when("crea un usuario advisor con sala asignada")
def step_create_advisor_with_sala(context):
    suffix = unique_suffix()
    context.created_advisor_username = f"advisor_selenium_{suffix}"
    context.permissions_page.open_create_modal()
    context.permissions_page.fill_create_user({
        "first_name": "Advisor",
        "last_name": "Con Sala",
        "username": context.created_advisor_username,
        "password": "advisor1234",
        "role": "Asesor",
    })
    context.created_advisor_sala = context.permissions_page.select_first_sala()
    context.permissions_page.submit_modal()
    context.permissions_page.wait_for_user(context.created_advisor_username)


@then("el usuario advisor creado aparece en la tabla")
def step_created_advisor_visible(context):
    assert context.permissions_page.user_exists(context.created_advisor_username)


@then("el usuario advisor creado muestra rol Asesor")
def step_created_advisor_role(context):
    assert context.permissions_page.user_has_role(context.created_advisor_username, "Asesor")


@then("el usuario advisor creado muestra la sala asignada")
def step_created_advisor_sala(context):
    assert context.permissions_page.user_has_sala_text(
        context.created_advisor_username,
        context.created_advisor_sala,
    )


@when("crea un usuario temporal activo")
def step_create_active_temp_user(context):
    suffix = unique_suffix()
    context.temp_permissions_username = f"student_selenium_{suffix}"
    context.permissions_page.open_create_modal()
    context.permissions_page.fill_create_user({
        "first_name": "Student",
        "last_name": "Temporal",
        "username": context.temp_permissions_username,
        "password": "student1234",
        "role": "Estudiante",
    })
    context.permissions_page.submit_modal()
    context.permissions_page.wait_for_user(context.temp_permissions_username)


@when("desactiva el usuario temporal desde el modal de edicion")
def step_deactivate_temp_user(context):
    context.permissions_page.deactivate_user(context.temp_permissions_username)


@then("el usuario temporal aparece como inactivo en la tabla")
def step_temp_user_inactive(context):
    assert context.permissions_page.user_has_status(context.temp_permissions_username, "Inactivo")


@when("cambia el rol del usuario temporal a advisor")
def step_change_temp_user_to_advisor(context):
    context.permissions_page.change_user_role_to_advisor(context.temp_permissions_username)


@then("el usuario temporal muestra rol Asesor en la tabla")
def step_temp_user_role_advisor(context):
    assert context.permissions_page.user_has_role(context.temp_permissions_username, "Asesor")
