import time

from behave import given, then, when

from pages.case_modal_page import CaseModalPage
from pages.cases_page import CasesPage


@given("abre la pagina de casos")
@when("abre la pagina de casos")
def step_open_cases(context):
    context.cases_page = CasesPage(context.driver)
    context.cases_page.open()


@then("la tabla de casos carga sin errores")
def step_cases_table_loaded(context):
    rows = context.cases_page.wait_for_table()
    assert rows, "Expected at least one case row"
    assert "No fue posible cargar" not in context.cases_page.visible_text()


@then("los estados activos y pendientes aparecen segun los casos cargados")
def step_statuses_match_loaded_cases(context):
    rows = context.cases_page.wait_for_table()
    status_text = " ".join(row.text for row in rows)
    assert "ACTIVE" in status_text or "IN_PROGRESS" in status_text, status_text
    assert "PENDING" in status_text, status_text


@when("filtra la tabla por el beneficiario de la primera fila")
def step_filter_by_first_beneficiary(context):
    snapshot = context.cases_page.first_case_snapshot()
    context.expected_beneficiary_filter = snapshot["beneficiary"]
    context.cases_page.filter_by_beneficiary(snapshot["beneficiary"])


@then("la tabla muestra solo casos que coinciden con el filtro")
def step_filtered_rows_match(context):
    expected = context.expected_beneficiary_filter
    rows = context.cases_page.visible_row_texts()
    assert rows, "Expected filtered rows"
    assert all(expected in row for row in rows), rows


@when("abre el primer caso de la tabla")
def step_open_first_case(context):
    context.selected_case = context.cases_page.first_case_snapshot()
    context.cases_page.open_first_case()


@then("el modal del caso muestra la informacion correcta")
def step_case_modal_shows_data(context):
    modal = CaseModalPage(context.driver)
    modal.wait_for_details(context.selected_case["id"])
    details = modal.details_text()
    assert context.selected_case["category"] in details
    assert context.selected_case["beneficiary"] in details


@when("crea un caso nuevo desde el modal")
def step_create_case(context):
    context.created_case_description = f"Caso automatizado Selenium {int(time.time())}"
    context.cases_page.open_create_modal()
    CaseModalPage(context.driver).create_case(context.created_case_description)


@then("el caso nuevo aparece en la tabla")
def step_created_case_in_table(context):
    context.cases_page.wait_for_table()
    context.cases_page.open_first_case()
    details = CaseModalPage(context.driver).details_text()
    assert context.created_case_description in details, details


@when("intenta crear un caso sin campos obligatorios")
def step_submit_empty_case(context):
    context.cases_page.open_create_modal()
    CaseModalPage(context.driver).submit_empty_case()


@then("ve errores de validacion del caso")
def step_case_validation_errors(context):
    text = CaseModalPage(context.driver).validation_text()
    assert "requerida" in text.lower() or "selecciona" in text.lower(), text


@when("abre el modal de creacion de caso")
def step_open_create_modal(context):
    context.cases_page.open_create_modal()
    context.case_modal = CaseModalPage(context.driver)


@then("el selector de proceso esta deshabilitado")
def step_process_disabled(context):
    assert context.case_modal.process_is_disabled()


@when("selecciona una sala")
def step_select_sala(context):
    context.case_modal.select_first_sala()


@then("el selector de proceso queda habilitado")
def step_process_enabled(context):
    context.case_modal.wait_for_process_enabled()
    assert not context.case_modal.process_is_disabled()
