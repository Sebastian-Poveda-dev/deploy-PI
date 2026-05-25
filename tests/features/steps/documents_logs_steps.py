from behave import given, then, when

from pages.case_modal_page import CaseModalPage
from pages.cases_page import CasesPage
from pages.dashboard_page import DashboardPage
from pages.documents_modal_page import DocumentsModalPage
from pages.login_page import LoginPage
from pages.logs_modal_page import LogsModalPage
from features.steps.test_data_helpers import (
    create_active_case_for_cancellation,
    create_case_with_document,
    create_case_with_log,
    ensure_upload_fixture_file,
    unique_suffix,
)


def documents_modal_page(context):
    context.documents_modal_page = DocumentsModalPage(context.driver)
    return context.documents_modal_page


def logs_modal_page(context):
    context.logs_modal_page = LogsModalPage(context.driver)
    return context.logs_modal_page


@given("existe un caso preparado con un documento asociado")
def step_case_with_document(context):
    context.document_case = create_case_with_document()


@given("existe un caso activo preparado para subir documentos")
def step_active_case_for_document_upload(context):
    context.document_case = create_active_case_for_cancellation()


@given("existe un caso preparado con historial de seguimiento")
def step_case_with_log(context):
    context.log_case = create_case_with_log()


@given("el admin inicia sesion para revisar documentos")
def step_login_admin_for_documents(context):
    context.login_page = LoginPage(context.driver)
    context.login_page.open()
    context.login_page.login_as("admin", "admin1234")
    DashboardPage(context.driver).wait_for_url_contains("/dashboard")


@when("abre la pagina de casos para documentos")
def step_open_cases_for_documents(context):
    context.cases_page = CasesPage(context.driver)
    context.cases_page.open()


@when("abre el caso preparado para documentos")
def step_open_prepared_document_case(context):
    context.cases_page.open_case_by_id(context.document_case["id"])
    context.case_modal = CaseModalPage(context.driver)
    context.case_modal.wait_for_details(context.document_case["id"])


@when("abre el modal de documentos del caso")
def step_open_documents_modal(context):
    context.case_modal.open_documents()
    documents_modal_page(context).wait_until_open()


@then("el modal de documentos del caso preparado esta abierto")
def step_documents_modal_open_for_case(context):
    context.documents_modal_page.wait_until_open_for_case(context.document_case["id"])


@then("el documento preparado aparece en la lista")
def step_prepared_document_visible(context):
    assert context.documents_modal_page.has_document(context.document_case["document_name"])


@when("sube un documento desde el modal de documentos del caso")
def step_upload_document_from_modal(context):
    context.uploaded_document_name = f"Documento subido Selenium {unique_suffix()}"
    context.uploaded_document_description = "Documento cargado desde Selenium"
    context.upload_fixture_path = ensure_upload_fixture_file()
    context.documents_modal_page.upload_document(
        context.uploaded_document_name,
        context.uploaded_document_description,
        context.upload_fixture_path,
    )


@then("el documento subido aparece en la lista de documentos")
def step_uploaded_document_visible(context):
    assert context.documents_modal_page.has_document(context.uploaded_document_name)


@when("abre el caso preparado para seguimiento")
def step_open_prepared_log_case(context):
    context.cases_page.open_case_by_id(context.log_case["id"])
    context.case_modal = CaseModalPage(context.driver)
    context.case_modal.wait_for_details(context.log_case["id"])


@when("abre el modal de seguimiento del caso")
def step_open_logs_modal(context):
    context.case_modal.open_logs()
    logs_modal_page(context).wait_until_open()


@then("el modal de seguimiento del caso preparado esta abierto")
def step_logs_modal_open_for_case(context):
    context.logs_modal_page.wait_until_open_for_case(context.log_case["id"])


@then("el historial preparado aparece en el modal de seguimiento")
def step_prepared_log_visible(context):
    assert context.logs_modal_page.has_log(context.log_case["log_content"])
