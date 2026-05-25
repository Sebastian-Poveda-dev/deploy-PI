from behave import then, when

from pages.case_modal_page import CaseModalPage
from pages.cases_page import CasesPage
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from pages.permissions_page import PermissionsPage


@when("el beneficiario seed abre la pagina de casos")
def step_beneficiary_opens_cases(context):
    context.login_page = LoginPage(context.driver)
    context.login_page.open()
    context.login_page.login_as("jperez", "ben1234")
    DashboardPage(context.driver).wait_for_url_contains("/dashboard/cases")
    context.cases_page = CasesPage(context.driver)


@then("no ve la tabla de casos de staff")
def step_staff_cases_table_absent(context):
    assert context.cases_page.staff_cases_table_is_absent()


@then("no ve el boton para crear casos")
def step_create_case_button_absent(context):
    assert context.cases_page.create_case_button_is_absent()


@then("el student no ve el boton cerrar caso en el modal")
def step_student_close_case_absent(context):
    context.case_modal = getattr(context, "case_modal", CaseModalPage(context.driver))
    assert not context.case_modal.close_case_button_is_visible()


@when("el student intenta abrir la pagina de permisos")
def step_student_opens_permissions(context):
    context.login_page = LoginPage(context.driver)
    context.login_page.open()
    context.login_page.login_as("s.vargas", "student1234")
    DashboardPage(context.driver).wait_for_url_contains("/dashboard")
    context.permissions_page = PermissionsPage(context.driver)
    context.permissions_page.open()


@then("no puede acceder a la pagina de permisos")
def step_permissions_denied(context):
    assert context.permissions_page.permission_denied_or_redirected()


@when("el advisor intenta administrar usuarios")
def step_advisor_opens_permissions(context):
    context.login_page = LoginPage(context.driver)
    context.login_page.open()
    context.login_page.login_as("a.torres", "advisor1234")
    DashboardPage(context.driver).wait_for_url_contains("/dashboard")
    context.permissions_page = PermissionsPage(context.driver)
    context.permissions_page.open()


@then("el advisor no puede crear usuarios")
def step_advisor_cannot_create_users(context):
    assert (
        context.permissions_page.permission_denied_or_redirected()
        or context.permissions_page.create_user_button_is_absent()
    )
