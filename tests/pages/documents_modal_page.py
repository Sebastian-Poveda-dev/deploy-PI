from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class DocumentsModalPage(BasePage):
    TITLE = (By.XPATH, "//h3[contains(normalize-space(), 'Documentos del Caso')]")

    def wait_until_open(self):
        return self.find_visible(self.TITLE)

    def modal_text(self):
        modal = self.find_visible((
            By.XPATH,
            "//h3[contains(normalize-space(), 'Documentos del Caso')]/ancestor::div[contains(@class, 'max-w-2xl')]",
        ))
        return modal.text

    def has_document(self, document_name):
        self.wait.until(lambda _: document_name in self.modal_text())
        return True

    def upload_document(self, name, description, file_path):
        self.fill((
            By.XPATH,
            "//h3[contains(normalize-space(), 'Documentos del Caso')]/ancestor::div[contains(@class, 'max-w-2xl')]//input[@placeholder='Ej. Contrato laboral']",
        ), name)
        self.fill((
            By.XPATH,
            "//h3[contains(normalize-space(), 'Documentos del Caso')]/ancestor::div[contains(@class, 'max-w-2xl')]//input[contains(@placeholder, 'descripci')]",
        ), description)
        file_input = self.find((
            By.XPATH,
            "//h3[contains(normalize-space(), 'Documentos del Caso')]/ancestor::div[contains(@class, 'max-w-2xl')]//input[@type='file']",
        ))
        file_input.send_keys(str(file_path))
        self.click((
            By.XPATH,
            "//h3[contains(normalize-space(), 'Documentos del Caso')]/ancestor::div[contains(@class, 'max-w-2xl')]//button[normalize-space()='Subir documento']",
        ))
        self.has_document(name)
