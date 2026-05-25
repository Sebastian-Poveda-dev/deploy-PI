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
        "//*[contains(normalize-space(), 'Caso 1') or contains(normalize-space(), 'Progreso del caso') or contains(normalize-space(), 'No tiene casos') or contains(normalize-space(), 'No se encontraron') or contains(normalize-space(), 'no encontrado') or contains(normalize-space(), 'No fue posible')]",
    )

    def open(self):
        self.open_public_tracking()

    def public_form_is_available(self, timeout=3):
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(lambda _: self.driver.find_elements(*self.IDENTIFICATION))
            wait.until(lambda _: self.driver.find_elements(*self.SEARCH_BUTTON))
            return True
        except TimeoutException:
            return False

    def open_public_tracking(self):
        for path in ("/track", "/"):
            self.open_path(path)
            if self.public_form_is_available():
                return
        raise AssertionError("No se encontro el formulario publico de seguimiento")

    def wait_for_public_form(self):
        self.find_visible(self.IDENTIFICATION)
        self.find_clickable(self.SEARCH_BUTTON)

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
        try:
            WebDriverWait(self.driver, 2).until(
                lambda _: "Consultando..." in self.visible_text()
            )
        except TimeoutException:
            pass
        self.wait.until(lambda _: "Consultando..." not in self.visible_text())
        self.wait.until(lambda _: self.has_tracking_result())

    def has_tracking_result(self):
        text = strip_accents(self.results_text())
        return (
            "caso 1" in text
            or "progreso del caso" in text
            or "no tiene casos" in text
            or "no se encontraron" in text
            or "no encontrado" in text
            or "no fue posible" in text
        )

    def results_text(self):
        return self.visible_text()

    def has_cases(self):
        text = strip_accents(self.results_text())
        return "caso 1" in text or "progreso del caso" in text

    def has_status_or_progress(self):
        text = strip_accents(self.results_text())
        statuses = [strip_accents(status) for status in self.STATUS_TEXTS]
        return "progreso del caso" in text or any(status in text for status in statuses)

    def has_not_found_message(self):
        text = strip_accents(self.results_text())
        return (
            "no se encontraron" in text
            or "no encontrado" in text
            or "no tiene casos registrados" in text
            or "no tiene casos" in text
            or "no fue posible consultar" in text
        )
