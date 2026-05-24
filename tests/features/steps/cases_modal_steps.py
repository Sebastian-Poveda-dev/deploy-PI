import time

from behave import given, then, when

from pages.dashboard_page import DashboardPage
from pages.case_modal_page import CaseModalPage
from pages.cases_page import CasesPage
from pages.login_page import LoginPage
from features.steps.test_data_helpers import create_assigned_case_for_advisor, ensure_pending_case_for_advisor


@given('existe un caso pendiente asignado al advisor "{advisor_username}"')
def step_pending_case_for_advisor(context, advisor_username):
    context.pending_advisor_case = ensure_pending_case_for_advisor(advisor_username)


@given('existe un caso asignado al advisor "{advisor_username}"')
def step_assigned_case_for_advisor(context, advisor_username):
    context.assigned_advisor_case = create_assigned_case_for_advisor(advisor_username)


@given('existe una sesion iniciada como advisor "{advisor_username}"')
def step_login_advisor(context, advisor_username):
    context.login_page = LoginPage(context.driver)
    context.login_page.open()
    context.login_page.login_as(advisor_username, "advisor1234")
    DashboardPage(context.driver).wait_for_url_contains("/dashboard")


@when("prepara el modal para crear un caso con resolucion inmediata")
def step_prepare_immediate_case_modal(context):
    context.cases_page = getattr(context, "cases_page", CasesPage(context.driver))
    context.previous_case_count = len(context.cases_page.wait_for_table())
    context.cases_page.open_create_modal()
    context.case_modal = CaseModalPage(context.driver)
    context.case_modal.enable_immediate_resolution()


@then("ve los campos extra de resolucion inmediata")
def step_immediate_fields_are_visible(context):
    assert context.case_modal.immediate_resolution_fields_are_visible()


@when("completa y crea el caso con resolucion inmediata")
def step_create_immediate_case(context):
    suffix = int(time.time())
    context.created_immediate_case_description = f"Caso inmediato Selenium {suffix}"
    context.created_immediate_resolution = f"Orientacion juridica resuelta en consulta {suffix}"
    context.case_modal.create_immediate_case(
        context.created_immediate_case_description,
        context.created_immediate_resolution,
    )


@then("el caso con resolucion inmediata aparece en la tabla")
def step_immediate_case_appears_in_table(context):
    context.created_immediate_case = context.cases_page.wait_for_new_first_case(
        context.previous_case_count
    )
    context.cases_page.open_first_case()
    modal = CaseModalPage(context.driver)
    modal.wait_for_details(context.created_immediate_case["id"])
    details = modal.details_text()
    assert context.created_immediate_case_description in details, details


@then("el caso con resolucion inmediata queda cerrado o finalizado")
def step_immediate_case_is_closed(context):
    status = context.created_immediate_case["status"]
    assert status in {"INACTIVE", "Inactivo", "Finalizado", "finished", "FINISHED"}, status


@when("abre el caso pendiente asignado al advisor")
def step_open_pending_advisor_case(context):
    context.cases_page = getattr(context, "cases_page", CasesPage(context.driver))
    context.cases_page.open_case_by_id(context.pending_advisor_case["id"])
    context.case_modal = CaseModalPage(context.driver)
    context.case_modal.wait_for_details(context.pending_advisor_case["id"])


@then("el caso pendiente muestra estado pendiente")
def step_pending_case_shows_pending_status(context):
    assert context.case_modal.status_matches({"PENDING", "Pendiente"})


@when("aprueba el caso pendiente desde el modal")
def step_approve_pending_case(context):
    context.case_modal.approve_case()


@then("el caso aprobado muestra estado activo")
def step_approved_case_shows_active_status(context):
    context.case_modal.wait_for_status({"ACTIVE", "Activo"})
    assert context.case_modal.status_matches({"ACTIVE", "Activo"})


@when("abre el caso asignado al advisor")
def step_open_assigned_advisor_case(context):
    context.cases_page = getattr(context, "cases_page", CasesPage(context.driver))
    context.cases_page.open_case_by_id(context.assigned_advisor_case["id"])
    context.case_modal = CaseModalPage(context.driver)
    context.case_modal.wait_for_details(context.assigned_advisor_case["id"])


@when("rechaza su asignacion desde el modal")
def step_reject_advisor_assignment(context):
    context.case_modal.reject_case()


@then("el advisor ya no aparece como usuario asignado del caso")
def step_advisor_assignment_removed(context):
    advisor_marker = context.assigned_advisor_case["advisor_last_name"] or context.assigned_advisor_case["advisor"]
    assert context.cases_page.wait_for_case_assignment_excludes(
        context.assigned_advisor_case["id"],
        advisor_marker,
    )
