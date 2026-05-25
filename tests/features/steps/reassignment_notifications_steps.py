"""
Step definitions for reassignment notification scenarios will live here.

The concrete scenarios 31-34 are intentionally not implemented in this
base-infrastructure pass.
"""

from pages.dashboard_notifications_page import DashboardNotificationsPage


def dashboard_notifications_page(context):
    context.dashboard_notifications_page = DashboardNotificationsPage(context.driver)
    return context.dashboard_notifications_page
