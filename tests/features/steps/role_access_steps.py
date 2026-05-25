"""
Step definitions for role access scenarios will live here.

The concrete scenarios 41-44 are intentionally not implemented in this
base-infrastructure pass.
"""

from pages.cases_page import CasesPage
from pages.permissions_page import PermissionsPage


def role_access_pages(context):
    context.cases_page = CasesPage(context.driver)
    context.permissions_page = PermissionsPage(context.driver)
    return context.cases_page, context.permissions_page
