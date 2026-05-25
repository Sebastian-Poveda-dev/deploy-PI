from behave import given, then, when

from pages.case_modal_page import CaseModalPage
from pages.cases_page import CasesPage
from features.steps.test_data_helpers import (
    create_case_with_document,
    create_case_with_log,
    ensure_upload_fixture_file,
    unique_suffix,
)


@given("existe un caso con documento asociado")
def step_case_with_document(context):
    context.document_case = create_case_with_document()


@given("existe un caso con historial de seguimiento")
def step_case_with_log(context):
    context.log_case = create_case_with_log()


@when("abre el modal de documentos del caso preparado")
def step_open_prepared_case_documents(context):
    context.cases_page = getattr(context, "cases_page", CasesPage(context.driver))
    context.cases_page.open()
    context.cases_page.open_case_by_id(context.document_case["id"])
    context.case_modal = CaseModalPage(context.driver)
    context.case_modal.wait_for_details(context.document_case["id"])
    context.case_modal.open_documents()


@then("el modal de documentos muestra el archivo asociado")
def step_document_modal_shows_file(context):
    assert context.case_modal.document_is_visible(context.document_case["document_name"])


@when("sube un documento desde el modal de documentos")
def step_upload_document_from_modal(context):
    context.uploaded_document_name = f"Documento subido Selenium {unique_suffix()}"
    context.upload_fixture_path = ensure_upload_fixture_file()
    context.case_modal.upload_document(
        context.uploaded_document_name,
        "Documento cargado durante prueba Selenium",
        context.upload_fixture_path,
    )


@then("el documento subido aparece en la lista del modal")
def step_uploaded_document_visible(context):
    assert context.case_modal.document_is_visible(context.uploaded_document_name)


@when("abre el modal de seguimiento del caso preparado")
def step_open_prepared_case_logs(context):
    context.cases_page = getattr(context, "cases_page", CasesPage(context.driver))
    context.cases_page.open()
    context.cases_page.open_case_by_id(context.log_case["id"])
    context.case_modal = CaseModalPage(context.driver)
    context.case_modal.wait_for_details(context.log_case["id"])
    context.case_modal.open_logs()


@then("el modal de seguimiento muestra el historial preparado")
def step_log_modal_shows_history(context):
    assert context.case_modal.log_is_visible(context.log_case["log_content"])
