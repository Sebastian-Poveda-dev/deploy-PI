from behave import given, then, when

from pages.case_modal_page import CaseModalPage
from pages.cases_page import CasesPage
from pages.dashboard_page import DashboardPage
from pages.documents_modal_page import DocumentsModalPage
from pages.login_page import LoginPage
from pages.logs_modal_page import LogsModalPage
from features.steps.test_data_helpers import create_case_with_document


def documents_modal_page(context):
    context.documents_modal_page = DocumentsModalPage(context.driver)
    return context.documents_modal_page


def logs_modal_page(context):
    context.logs_modal_page = LogsModalPage(context.driver)
    return context.logs_modal_page


@given("existe un caso preparado con un documento asociado")
def step_case_with_document(context):
    context.document_case = create_case_with_document()


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
