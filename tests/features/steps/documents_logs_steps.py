"""
Step definitions for documents and logs scenarios will live here.

The concrete scenarios 38-40 are intentionally not implemented in this
base-infrastructure pass.
"""

from pages.documents_modal_page import DocumentsModalPage
from pages.logs_modal_page import LogsModalPage


def documents_modal_page(context):
    context.documents_modal_page = DocumentsModalPage(context.driver)
    return context.documents_modal_page


def logs_modal_page(context):
    context.logs_modal_page = LogsModalPage(context.driver)
    return context.logs_modal_page
