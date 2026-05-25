"""
Step definitions for beneficiary tracking scenarios will live here.

The concrete scenarios 35-37 are intentionally not implemented in this
base-infrastructure pass.
"""

from pages.beneficiary_tracking_page import BeneficiaryTrackingPage


def beneficiary_tracking_page(context):
    context.beneficiary_tracking_page = BeneficiaryTrackingPage(context.driver)
    return context.beneficiary_tracking_page
