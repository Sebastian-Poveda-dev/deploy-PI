from behave import then, when

from pages.permissions_page import PermissionsPage


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
