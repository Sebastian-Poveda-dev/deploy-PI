from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage, strip_accents


class BeneficiaryTrackingPage(BasePage):
    DASHBOARD_TITLE = (By.XPATH, "//h1[contains(normalize-space(), 'Estado de mi caso')]")
    CASE_CARD = (By.XPATH, "//button[.//*[contains(normalize-space(), 'Estado actual')]]")
    STATUS_TEXTS = (
        "ACTIVE",
        "PENDING",
        "INACTIVE",
        "CANCELLED",
        "IN_PROGRESS",
        "Activo",
        "Pendiente",
        "Inactivo",
        "Cancelado",
        "En progreso",
    )
    IDENTIFICATION = (By.ID, "identification_number")
    SEARCH_BUTTON = (By.XPATH, "//button[contains(normalize-space(), 'Consultar estado')]")
    RESULT_CONTAINER = (
        By.XPATH,
        "//*[contains(normalize-space(), 'Caso 1') or contains(normalize-space(), 'No tiene casos') or contains(normalize-space(), 'No se encontraron') or contains(normalize-space(), 'no encontrado')]",
    )

    def open(self):
        self.open_path("/track")

    def wait_for_authenticated_dashboard(self):
        self.wait_for_url_contains("/dashboard/cases")
        self.find_visible(self.DASHBOARD_TITLE)
        self.wait.until(lambda _: "Cargando estado del caso" not in self.visible_text())

    def is_authenticated_cases_route(self):
        return "/dashboard/cases" in self.driver.current_url

    def staff_table_is_absent(self, timeout=3):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: not driver.find_elements(By.CSS_SELECTOR, "table")
            )
            return True
        except TimeoutException:
            return False

    def has_case_status(self):
        self.wait_for_authenticated_dashboard()
        text = self.visible_text()
        has_card = bool(self.driver.find_elements(*self.CASE_CARD))
        has_status = any(status in text for status in self.STATUS_TEXTS)
        return has_card and has_status

    def search(self, identification_number):
        self.fill(self.IDENTIFICATION, identification_number)
        self.click(self.SEARCH_BUTTON)
        self.find_visible(self.RESULT_CONTAINER)

    def results_text(self):
        return self.visible_text()

    def has_cases(self):
        text = self.results_text()
        return "Caso 1" in text and "Progreso del caso" in text

    def has_not_found_message(self):
        text = strip_accents(self.results_text())
        return (
            "no se encontraron" in text
            or "no encontrado" in text
            or "no tiene casos registrados" in text
        )
