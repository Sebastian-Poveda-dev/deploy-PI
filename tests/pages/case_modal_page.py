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

    def wait_until_details_closed(self, case_id):
        self.wait.until(EC.invisibility_of_element_located((By.XPATH, f"//h2[contains(normalize-space(), 'Caso #{case_id}')]")))

    def details_text(self):
        modal = self.find_visible((By.XPATH, "//div[contains(@class, 'max-w-2xl') or contains(@class, 'max-w-xl')]"))
        return modal.text

    def status_matches(self, expected_statuses):
        text = self.details_text()
        return any(status in text for status in expected_statuses)

    def wait_for_status(self, expected_statuses):
        self.wait.until(lambda _: self.status_matches(expected_statuses))

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

    def immediate_resolution_fields_are_visible(self):
        self.find_visible(self.IMMEDIATE_RESOLUTION)
        self.find_visible(self.ATTENDED_BY)
        return True

    def fill_immediate_resolution(self, resolution):
        self.fill(self.IMMEDIATE_RESOLUTION, resolution)

    def select_first_attended_by(self):
        return self.select_first_real_option(self.ATTENDED_BY)

    def create_immediate_case(self, description, resolution):
        self.fill(self.DESCRIPTION, description)
        self.select_first_sala()
        self.wait_for_process_enabled()
        self.select_first_process()
        self.select_first_beneficiary()
        self.fill_immediate_resolution(resolution)
        self.click(self.CREATE_BUTTON)
        self.wait.until(EC.invisibility_of_element_located((By.XPATH, "//h2[normalize-space()='Crear Caso']")))

    def click_action(self, text):
        self.click(self.button_by_text(text))

    def confirm_action(self):
        self.click(self.CONFIRM_BUTTON)

    def approve_case(self):
        self.click_action("Aprobar Caso")
        self.confirm_action()

    def reject_case(self):
        self.click_action("Rechazar Caso")
        self.confirm_action()

    def request_reassignment(self, reason, case_id):
        self.click_action("Solicitar Reasignaci")
        self.fill_reassignment_reason(reason)
        self.confirm_action()
        self.wait_until_details_closed(case_id)

    def pending_reassignment_is_visible(self, reason):
        text = self.details_text()
        return "Solicitud de Reasignaci" in text and "Pendiente" in text and reason in text

    def fill_reassignment_reason(self, reason):
        self.fill((By.XPATH, "//textarea[contains(@placeholder, 'motivo')]"), reason)

    def select_cancellation_reason(self, reason_text):
        option = self.find_visible((By.XPATH, f"//label[.//span[contains(normalize-space(), '{reason_text}')]]//input[@type='radio']"))
        option.click()

    def cancel_case_with_reason(self, reason_text):
        self.click_action("Cerrar Caso")
        self.select_cancellation_reason(reason_text)
        self.confirm_action()

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
