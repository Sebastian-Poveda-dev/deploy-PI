from behave import given, then, when

from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage


@given("el usuario esta en la pagina de login")
def step_open_login(context):
    context.login_page = LoginPage(context.driver)
    context.login_page.open()


@when('ingresa el usuario "{username}" y la contrasena "{password}"')
def step_enter_credentials(context, username, password):
    context.login_page.login_as(username, password)


@then('es redirigido a "{path}"')
def step_redirected_to(context, path):
    DashboardPage(context.driver).wait_for_url_contains(path)


@then('ve contenido autenticado para "{role}"')
def step_authenticated_content(context, role):
    page = DashboardPage(context.driver)
    if role == "beneficiary":
        assert page.has_text("Estado de mi caso") or page.has_text("caso"), page.visible_text()
    else:
        assert page.has_text("Bienvenido"), page.visible_text()


@then("ve un mensaje de error de autenticacion")
def step_auth_error(context):
    message = context.login_page.error_message()
    assert "incorrect" in message.lower() or "no fue posible" in message.lower()


@then("permanece en la pagina de login")
def step_stays_login(context):
    assert "/login" in context.driver.current_url


@given("el visitante no tiene sesion iniciada")
def step_clear_session(context):
    context.driver.delete_all_cookies()


@when('intenta acceder a la ruta protegida "{path}"')
def step_open_protected_route(context, path):
    DashboardPage(context.driver).open_path(path)


@then("es redirigido al login")
def step_redirected_login(context):
    DashboardPage(context.driver).wait_for_url_contains("/login")


@then("permanece en la ruta protegida")
def step_stays_on_protected_route(context):
    assert "/dashboard/cases" in context.driver.current_url


@then("ve un error de carga de casos")
def step_cases_load_error(context):
    page = DashboardPage(context.driver)
    assert page.has_text("No fue posible cargar los casos"), page.visible_text()


@given("existe una sesion iniciada como admin")
def step_login_admin(context):
    context.login_page = LoginPage(context.driver)
    context.login_page.open()
    context.login_page.login_as("admin", "admin1234")
    DashboardPage(context.driver).wait_for_url_contains("/dashboard")
