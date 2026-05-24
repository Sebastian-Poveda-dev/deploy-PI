from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from pages.base_page import BasePage


class CaseModalPage(BasePage):
    DESCRIPTION = (By.XPATH, "//textarea[@placeholder='Describe el caso...']")
    SALA = (By.XPATH, "//label[normalize-space()='Sala']/following-sibling::select")
    PROCESO = (By.XPATH, "//label[normalize-space()='Proceso']/following-sibling::select")
    BENEFICIARY = (By.XPATH, "//label[normalize-space()='Beneficiario']/following-sibling::select")
    CREATE_BUTTON = (By.XPATH, "//form//button[normalize-space()='Crear Caso']")

    def wait_for_details(self, case_id):
        self.find_visible((By.XPATH, f"//h2[contains(normalize-space(), 'Caso #{case_id}')]"))

    def details_text(self):
        modal = self.find_visible((By.XPATH, "//div[contains(@class, 'max-w-2xl') or contains(@class, 'max-w-xl')]"))
        return modal.text

    def process_is_disabled(self):
        return self.find_visible(self.PROCESO).get_attribute("disabled") is not None

    def select_first_sala(self):
        self.wait.until(lambda _: len([o for o in Select(self.find_visible(self.SALA)).options if o.get_attribute("value")]) > 0)
        return self.select_first_real_option(self.SALA)

    def wait_for_process_enabled(self):
        self.wait.until(lambda _: self.find_visible(self.PROCESO).get_attribute("disabled") is None)
        self.wait.until(lambda _: len([o for o in Select(self.find_visible(self.PROCESO)).options if o.get_attribute("value")]) > 0)

    def select_first_process(self):
        return self.select_first_real_option(self.PROCESO)

    def select_first_beneficiary(self):
        self.wait.until(lambda _: len([o for o in Select(self.find_visible(self.BENEFICIARY)).options if o.get_attribute("value")]) > 0)
        return self.select_first_real_option(self.BENEFICIARY)

    def create_case(self, description):
        self.fill(self.DESCRIPTION, description)
        self.select_first_sala()
        self.wait_for_process_enabled()
        self.select_first_process()
        self.select_first_beneficiary()
        self.click(self.CREATE_BUTTON)
        self.wait.until(EC.invisibility_of_element_located((By.XPATH, "//h2[normalize-space()='Crear Caso']")))

    def submit_empty_case(self):
        self.click(self.CREATE_BUTTON)

    def validation_text(self):
        return self.visible_text()

    def current_process_options(self):
        return [option.text for option in Select(self.find_visible(self.PROCESO)).options]
