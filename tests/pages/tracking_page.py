from selenium.webdriver.common.by import By

from pages.base_page import BasePage, strip_accents


class TrackingPage(BasePage):
    IDENTIFICATION = (By.ID, "identification_number")
    SUBMIT = (By.XPATH, "//button[contains(normalize-space(), 'Consultar estado')]")
    RESULTS = (
        By.XPATH,
        "//*[contains(normalize-space(), 'Caso 1') or contains(normalize-space(), 'No tiene casos') or contains(normalize-space(), 'No se encontraron') or contains(normalize-space(), 'no encontrado')]",
    )

    def open(self):
        self.open_path("/track")

    def search_by_identification(self, identification_number):
        self.fill(self.IDENTIFICATION, identification_number)
        self.click(self.SUBMIT)
        self.find_visible(self.RESULTS)

    def results_text(self):
        return self.visible_text()

    def has_cases(self):
        text = self.results_text()
        return "Caso 1" in text and "Progreso del caso" in text

    def has_status(self, status_text):
        return strip_accents(status_text) in strip_accents(self.results_text())

    def has_not_found_message(self):
        text = strip_accents(self.results_text())
        return (
            "no se encontraron" in text
            or "no encontrado" in text
            or "no tiene casos registrados" in text
        )
