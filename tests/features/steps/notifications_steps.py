from behave import given, then, when

from pages.case_modal_page import CaseModalPage
from pages.cases_page import CasesPage
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from pages.notifications_page import NotificationsPage
from features.steps.test_data_helpers import create_case_with_pending_reassignment


@given('existe una solicitud de reasignacion pendiente para el advisor "{advisor_username}"')
def step_pending_reassignment_for_advisor(context, advisor_username):
    context.pending_reassignment_case = create_case_with_pending_reassignment(
        advisor_username=advisor_username,
    )


@when('inicia sesion como advisor de la solicitud "{advisor_username}"')
def step_login_reassignment_advisor(context, advisor_username):
    context.login_page = LoginPage(context.driver)
    context.login_page.open()
    context.login_page.login_as(advisor_username, "advisor1234")
    DashboardPage(context.driver).wait_for_url_contains("/dashboard")


@when("abre el panel de notificaciones de reasignacion")
def step_open_reassignment_notifications(context):
    context.notifications_page = NotificationsPage(context.driver)
    context.notifications_page.open()
    context.notifications_page.wait_for_reassignment_panel()


@then("ve la notificacion de reasignacion del caso preparado")
def step_reassignment_notification_visible(context):
    case_id = context.pending_reassignment_case["id"]
    assert context.notifications_page.has_notification_for_case(case_id)
    assert context.pending_reassignment_case["student"] in context.notifications_page.notification_text_for_case(case_id)


@when("marca como leida la notificacion de reasignacion")
def step_dismiss_reassignment_notification(context):
    context.notifications_page.dismiss_notification(context.pending_reassignment_case["id"])


@then("la notificacion de reasignacion preparada desaparece")
def step_reassignment_notification_absent(context):
    context.notifications_page.wait_until_notification_absent(context.pending_reassignment_case["id"])


@when("abre el caso desde la notificacion de reasignacion")
def step_open_case_from_reassignment_notification(context):
    context.notifications_page.open_case_from_notification(context.pending_reassignment_case["id"])
    context.cases_page = CasesPage(context.driver)
    context.case_modal = CaseModalPage(context.driver)
    context.case_modal.wait_for_details(context.pending_reassignment_case["id"])


@when("aprueba la solicitud de reasignacion preparada desde el modal")
def step_approve_prepared_reassignment(context):
    context.case_modal.approve_reassignment()


@when("rechaza la solicitud de reasignacion preparada desde el modal")
def step_reject_prepared_reassignment(context):
    context.case_modal.reject_reassignment()


@then("el caso preparado conserva el advisor asignado")
def step_prepared_case_keeps_advisor(context):
    context.cases_page.open()
    assignment = context.cases_page.assignment_text_for_case(context.pending_reassignment_case["id"])
    advisor_marker = context.pending_reassignment_case["advisor_last_name"] or context.pending_reassignment_case["advisor"]
    assert advisor_marker in assignment, assignment
