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
    IMMEDIATE_CHECKBOX = (By.XPATH, "//p[contains(normalize-space(), 'Resoluci') and contains(normalize-space(), 'inmediata')]/ancestor::label//input[@type='checkbox']")
    IMMEDIATE_RESOLUTION = (By.XPATH, "//label[contains(normalize-space(), 'Resoluci')]/following-sibling::textarea")
    ATTENDED_BY = (By.XPATH, "//label[normalize-space()='Atendido por']/following-sibling::select")
    CONFIRM_BUTTON = (By.XPATH, "//button[normalize-space()='Confirmar']")

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

    def enable_immediate_resolution(self):
        checkbox = self.find_visible(self.IMMEDIATE_CHECKBOX)
        if not checkbox.is_selected():
            checkbox.click()
        self.find_visible(self.IMMEDIATE_RESOLUTION)

    def fill_immediate_resolution(self, resolution):
        self.fill(self.IMMEDIATE_RESOLUTION, resolution)

    def select_first_attended_by(self):
        return self.select_first_real_option(self.ATTENDED_BY)

    def click_action(self, text):
        self.click(self.button_by_text(text))

    def confirm_action(self):
        self.click(self.CONFIRM_BUTTON)

    def fill_reassignment_reason(self, reason):
        self.fill((By.XPATH, "//textarea[contains(@placeholder, 'motivo')]"), reason)

    def select_cancellation_reason(self, reason_text):
        option = self.find_visible((By.XPATH, f"//label[.//span[contains(normalize-space(), '{reason_text}')]]//input[@type='radio']"))
        option.click()

    def fill_other_cancellation_reason(self, reason):
        self.fill((By.XPATH, "//textarea[contains(@placeholder, 'cancelaci')]"), reason)

    def action_error_text(self):
        return self.find_visible((By.XPATH, "//p[contains(@class, 'text-red-500')]")).text

    def toggle_more_info(self):
        self.click((By.XPATH, "//button[contains(normalize-space(), 'informaci')]"))

    def start_edit_beneficiary(self):
        self.click((By.XPATH, "//button[contains(@title, 'Editar beneficiario') or contains(normalize-space(), 'Editar')]"))

    def fill_beneficiary_edit_field(self, label, value):
        self.fill((By.XPATH, f"//label[normalize-space()='{label}']/following-sibling::input"), value)

    def add_beneficiary_extra_field(self, key, value):
        self.click(self.button_by_text("+ Agregar campo"))
        keys = self.driver.find_elements(By.XPATH, "//input[@placeholder='Nombre del campo']")
        values = self.driver.find_elements(By.XPATH, "//input[@placeholder='Valor']")
        keys[-1].clear()
        keys[-1].send_keys(key)
        values[-1].clear()
        values[-1].send_keys(value)

    def save_beneficiary(self):
        self.click((By.XPATH, "//form//button[normalize-space()='Guardar']"))
