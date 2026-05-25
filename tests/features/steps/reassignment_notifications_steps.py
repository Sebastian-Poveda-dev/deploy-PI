import time

from behave import given, then, when

from pages.case_modal_page import CaseModalPage
from pages.cases_page import CasesPage
from pages.dashboard_notifications_page import DashboardNotificationsPage
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from features.steps.test_data_helpers import create_active_case_for_reassignment_request


def dashboard_notifications_page(context):
    context.dashboard_notifications_page = DashboardNotificationsPage(context.driver)
    return context.dashboard_notifications_page


@given("existe un caso activo asignado a s.vargas y a.torres para solicitar reasignacion")
def step_active_case_for_student_reassignment(context):
    context.reassignment_case = create_active_case_for_reassignment_request(
        student_username="s.vargas",
        advisor_username="a.torres",
    )


@when("el student s.vargas solicita la reasignacion del caso preparado")
def step_student_requests_reassignment(context):
    context.login_page = LoginPage(context.driver)
    context.login_page.open()
    context.login_page.login_as("s.vargas", "student1234")
    DashboardPage(context.driver).wait_for_url_contains("/dashboard")

    context.cases_page = CasesPage(context.driver)
    context.cases_page.open()
    context.cases_page.open_case_by_id(context.reassignment_case["id"])

    context.case_modal = CaseModalPage(context.driver)
    context.case_modal.wait_for_details(context.reassignment_case["id"])
    context.reassignment_reason = f"Motivo unico Selenium reasignacion {int(time.time() * 1000)}"
    context.case_modal.request_reassignment(
        context.reassignment_reason,
        context.reassignment_case["id"],
    )


@when("inicia sesion como advisor a.torres para revisar notificaciones")
def step_login_advisor_for_reassignment_notifications(context):
    context.driver.delete_all_cookies()
    context.login_page = LoginPage(context.driver)
    context.login_page.open()
    context.login_page.login_as("a.torres", "advisor1234")
    DashboardPage(context.driver).wait_for_url_contains("/dashboard")


@then("ve el panel de solicitudes de reasignacion pendientes")
def step_reassignment_panel_visible(context):
    page = dashboard_notifications_page(context)
    page.open()
    page.wait_for_reassignment_panel()


@then("ve la notificacion de reasignacion relacionada con el caso preparado")
def step_reassignment_notification_visible(context):
    page = dashboard_notifications_page(context)
    case_id = context.reassignment_case["id"]
    assert page.has_notification_for_case(case_id), page.visible_text()
    assert str(case_id) in page.notification_text_for_case(case_id)
