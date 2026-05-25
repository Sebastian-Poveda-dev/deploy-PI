from behave import given, then, when

from pages.dashboard_page import DashboardPage
from pages.cases_page import CasesPage
from pages.login_page import LoginPage
from pages.permissions_page import PermissionsPage
from features.steps.test_data_helpers import ensure_beneficiary_case


def role_access_pages(context):
    context.cases_page = CasesPage(context.driver)
    context.permissions_page = PermissionsPage(context.driver)
    return context.cases_page, context.permissions_page


@given("existe una sesion iniciada como beneficiario jperez")
def step_login_beneficiary_jperez(context):
    ensure_beneficiary_case("jperez")
    context.login_page = LoginPage(context.driver)
    context.login_page.open()
    context.login_page.login_as("jperez", "ben1234")
    DashboardPage(context.driver).wait_for_url_contains("/dashboard")


@when("el beneficiario abre su vista de casos")
def step_beneficiary_opens_own_cases(context):
    context.cases_page = CasesPage(context.driver)
    context.cases_page.open()
    context.cases_page.wait_for_beneficiary_cases()


@then("no ve la tabla completa de casos de staff")
def step_beneficiary_does_not_see_staff_cases_table(context):
    assert context.cases_page.staff_table_headers_are_absent(), context.cases_page.visible_text()


@then("ve la vista de estado de sus propios casos")
def step_beneficiary_sees_own_status_view(context):
    assert context.cases_page.beneficiary_status_view_is_visible(), context.cases_page.visible_text()
