from selenium.webdriver.common.by import By

from pages.base_page import BasePage, strip_accents


class BeneficiaryTrackingPage(BasePage):
    IDENTIFICATION = (By.ID, "identification_number")
    SEARCH_BUTTON = (By.XPATH, "//button[contains(normalize-space(), 'Consultar estado')]")
    RESULT_CONTAINER = (
        By.XPATH,
        "//*[contains(normalize-space(), 'Caso 1') or contains(normalize-space(), 'No tiene casos') or contains(normalize-space(), 'No se encontraron') or contains(normalize-space(), 'no encontrado')]",
    )

    def open(self):
        self.open_path("/track")

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
