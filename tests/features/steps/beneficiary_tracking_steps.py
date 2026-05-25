from behave import given, then, when

from pages.dashboard_page import DashboardPage
from pages.beneficiary_tracking_page import BeneficiaryTrackingPage
from pages.login_page import LoginPage
from features.steps.test_data_helpers import ensure_beneficiary_case


def beneficiary_tracking_page(context):
    context.beneficiary_tracking_page = BeneficiaryTrackingPage(context.driver)
    return context.beneficiary_tracking_page


@given("existe un caso asociado al beneficiario jperez")
def step_ensure_jperez_case(context):
    context.beneficiary_case = ensure_beneficiary_case("jperez")


@when("el beneficiario jperez inicia sesion")
def step_login_jperez(context):
    context.login_page = LoginPage(context.driver)
    context.login_page.open()
    context.login_page.login_as("jperez", "ben1234")
    DashboardPage(context.driver).wait_for_url_contains("/dashboard")
    beneficiary_tracking_page(context).wait_for_authenticated_dashboard()


@then("entra a la vista autenticada de sus casos")
def step_beneficiary_cases_route(context):
    assert context.beneficiary_tracking_page.is_authenticated_cases_route()


@then("no ve la tabla completa de staff")
def step_beneficiary_does_not_see_staff_table(context):
    assert context.beneficiary_tracking_page.staff_table_is_absent()


@then("ve el estado de sus casos")
def step_beneficiary_sees_case_status(context):
    assert context.beneficiary_tracking_page.has_case_status(), context.beneficiary_tracking_page.visible_text()
