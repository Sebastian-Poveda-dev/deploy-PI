from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CasesPage(BasePage):
    FILTERS_BUTTON = (By.XPATH, "//button[contains(normalize-space(), 'Filtros')]")
    FILTER_ID = (By.XPATH, "//label[contains(normalize-space(), 'ID del Caso')]/following-sibling::input")
    FILTER_BENEFICIARY = (By.XPATH, "//label[contains(normalize-space(), 'Beneficiario')]/following-sibling::input")
    APPLY_FILTERS = (By.XPATH, "//button[normalize-space()='Aplicar']")
    EMPTY_MESSAGE = (By.XPATH, "//*[contains(text(), 'No hay casos') or contains(text(), 'No tienes casos')]")

    def open(self):
        self.open_path("/dashboard/cases")

    def wait_for_table(self):
        self.find_visible((By.XPATH, "//h1[contains(normalize-space(), 'Casos')]"))
        return self.table_rows()

    def first_case_snapshot(self):
        row = self.wait_for_table()[0]
        cells = row.find_elements(By.TAG_NAME, "td")
        return {
            "id": cells[0].text.replace("#", "").strip(),
            "status": cells[1].text.strip(),
            "category": cells[2].text.strip(),
            "beneficiary": cells[3].text.strip(),
            "created_at": cells[4].text.strip(),
            "assigned": cells[6].text.strip(),
        }

    def open_first_case(self):
        row = self.wait_for_table()[0]
        row.click()

    def filter_by_beneficiary(self, beneficiary):
        self.click(self.FILTERS_BUTTON)
        self.fill(self.FILTER_BENEFICIARY, beneficiary)
        self.click(self.APPLY_FILTERS)

    def visible_row_texts(self):
        rows = self.driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        return [row.text for row in rows]

    def open_create_modal(self):
        self.click(self.button_by_text("Crear Caso"))
