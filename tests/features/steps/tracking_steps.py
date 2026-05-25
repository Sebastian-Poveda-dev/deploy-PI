from behave import given, then, when

from pages.cases_page import CasesPage
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from pages.tracking_page import TrackingPage
from features.steps.test_data_helpers import ensure_beneficiary_case


@given("existe un caso visible para el beneficiario seed")
def step_seed_beneficiary_case(context):
    context.beneficiary_case = ensure_beneficiary_case("jperez")


@when("el beneficiario seed inicia sesion para consultar sus casos")
def step_login_seed_beneficiary(context):
    context.login_page = LoginPage(context.driver)
    context.login_page.open()
    context.login_page.login_as("jperez", "ben1234")
    DashboardPage(context.driver).wait_for_url_contains("/dashboard/cases")
    context.cases_page = CasesPage(context.driver)


@then("ve el estado de sus casos en el dashboard")
def step_beneficiary_sees_case_status(context):
    assert context.cases_page.has_beneficiary_case_status()


@when('consulta el seguimiento publico con cedula "{identification_number}"')
def step_public_tracking_search(context, identification_number):
    context.tracking_page = TrackingPage(context.driver)
    context.tracking_page.open()
    context.tracking_page.search_by_identification(identification_number)


@then("el seguimiento publico muestra casos asociados")
def step_public_tracking_shows_cases(context):
    assert context.tracking_page.has_cases(), context.tracking_page.results_text()


@then("el seguimiento publico muestra mensaje de no encontrado")
def step_public_tracking_not_found(context):
    assert context.tracking_page.has_not_found_message(), context.tracking_page.results_text()
