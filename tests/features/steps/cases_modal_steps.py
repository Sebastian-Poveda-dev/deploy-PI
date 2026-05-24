import time

from behave import then, when

from pages.case_modal_page import CaseModalPage
from pages.cases_page import CasesPage


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
