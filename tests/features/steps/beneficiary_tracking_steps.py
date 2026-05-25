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


@given('existe un caso asociado a la cedula "{identification_number}"')
def step_ensure_case_for_identification(context, identification_number):
    context.beneficiary_case = ensure_beneficiary_case("jperez")
    assert context.beneficiary_case["identification_number"] == identification_number


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


@when("abre la pagina de seguimiento publico")
def step_open_public_tracking(context):
    beneficiary_tracking_page(context).open()
    context.beneficiary_tracking_page.wait_for_public_form()


@when('consulta el seguimiento publico con la cedula "{identification_number}"')
def step_search_public_tracking(context, identification_number):
    context.beneficiary_tracking_page.search(identification_number)


@then("el seguimiento publico de beneficiario muestra casos asociados")
def step_public_tracking_shows_cases(context):
    assert context.beneficiary_tracking_page.has_cases(), context.beneficiary_tracking_page.results_text()


@then("el seguimiento publico de beneficiario muestra estado o progreso del caso")
def step_public_tracking_shows_status_or_progress(context):
    assert context.beneficiary_tracking_page.has_status_or_progress(), context.beneficiary_tracking_page.results_text()


@then("el seguimiento publico de beneficiario muestra mensaje de no encontrado")
def step_public_tracking_shows_not_found(context):
    assert context.beneficiary_tracking_page.has_not_found_message(), context.beneficiary_tracking_page.results_text()
