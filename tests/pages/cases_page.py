from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage, strip_accents


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

    def wait_for_new_first_case(self, previous_count):
        self.wait.until(lambda _: len(self.table_rows()) > previous_count)
        return self.first_case_snapshot()

    def open_first_case(self):
        row = self.wait_for_table()[0]
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row)
        self.driver.execute_script("arguments[0].click();", row)

    def open_case_by_id(self, case_id):
        self.wait_for_table()
        row = self.find_visible((By.XPATH, f"//tbody/tr[td[1][normalize-space()='#{case_id}']]"))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row)
        self.driver.execute_script("arguments[0].click();", row)

    def assignment_text_for_case(self, case_id):
        row = self.find_visible((By.XPATH, f"//tbody/tr[td[1][normalize-space()='#{case_id}']]"))
        cells = row.find_elements(By.TAG_NAME, "td")
        return cells[6].text.strip()

    def case_assignment_includes(self, case_id, text):
        return text in self.assignment_text_for_case(case_id)

    def wait_for_case_assignment_includes(self, case_id, text):
        return self.wait.until(lambda _: self.case_assignment_includes(case_id, text))

    def wait_for_case_assignment_excludes(self, case_id, text):
        def assignment_removed(_):
            rows = self.driver.find_elements(By.XPATH, f"//tbody/tr[td[1][normalize-space()='#{case_id}']]")
            if not rows:
                return True
            cells = rows[0].find_elements(By.TAG_NAME, "td")
            return text not in cells[6].text

        return self.wait.until(assignment_removed)

    def filter_by_beneficiary(self, beneficiary):
        self.click(self.FILTERS_BUTTON)
        self.fill(self.FILTER_BENEFICIARY, beneficiary)
        self.click(self.APPLY_FILTERS)

    def filter_by_assigned_user(self, username):
        self.click(self.FILTERS_BUTTON)
        self.fill((By.XPATH, "//label[contains(normalize-space(), 'Persona Asignada')]/following-sibling::input"), username)
        self.click(self.APPLY_FILTERS)

    def visible_row_texts(self):
        rows = self.driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        return [row.text for row in rows]

    def open_create_modal(self):
        self.click(self.button_by_text("Crear Caso"))

    def open_case_by_status(self, status_text):
        row = self.find_visible((By.XPATH, f"//tbody/tr[td[contains(normalize-space(), '{status_text}')]]"))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row)
        self.driver.execute_script("arguments[0].click();", row)

    def open_case_by_assigned_user(self, username):
        row = self.find_visible((By.XPATH, f"//tbody/tr[td[contains(normalize-space(), '{username}')]]"))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row)
        self.driver.execute_script("arguments[0].click();", row)

    def wait_for_beneficiary_cases(self):
        self.find_visible((By.XPATH, "//h1[contains(normalize-space(), 'Estado de mi caso')]"))
        self.wait.until(lambda _: "Cargando estado del caso" not in self.visible_text())

    def beneficiary_case_cards(self):
        self.wait_for_beneficiary_cases()
        return self.driver.find_elements(By.XPATH, "//button[.//*[contains(normalize-space(), 'Estado actual')]]")

    def beneficiary_status_text(self):
        self.wait_for_beneficiary_cases()
        return self.visible_text()

    def has_beneficiary_case_status(self):
        return bool(self.beneficiary_case_cards()) and "Estado actual" in self.beneficiary_status_text()

    def beneficiary_status_view_is_visible(self):
        text = strip_accents(self.beneficiary_status_text())
        return "estado de mi caso" in text and (
            "estado actual" in text or "no tiene casos registrados" in text
        )

    def staff_cases_table_is_absent(self, timeout=3):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: not driver.find_elements(By.CSS_SELECTOR, "table")
            )
            return True
        except TimeoutException:
            return False

    def create_case_button_is_absent(self):
        return not self.driver.find_elements(*self.button_by_text("Crear Caso"))

    def staff_table_headers_are_absent(self):
        page_text = self.visible_text()
        staff_headers = (
            "Beneficiario",
            "Usuarios asignados",
            "Categoría",
            "Persona Asignada",
        )
        return self.staff_cases_table_is_absent() and all(
            header not in page_text for header in staff_headers
        )
