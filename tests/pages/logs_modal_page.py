from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LogsModalPage(BasePage):
    TITLE = (By.XPATH, "//h3[contains(normalize-space(), 'Seguimiento del Caso')]")

    def wait_until_open(self):
        return self.find_visible(self.TITLE)

    def wait_until_open_for_case(self, case_id):
        return self.find_visible((
            By.XPATH,
            f"//h3[contains(normalize-space(), 'Seguimiento del Caso #{case_id}')]",
        ))

    def modal_text(self):
        modal = self.find_visible((
            By.XPATH,
            "//h3[contains(normalize-space(), 'Seguimiento del Caso')]/ancestor::div[contains(@class, 'max-w-2xl')]",
        ))
        return modal.text

    def has_log(self, expected_text):
        self.wait.until(lambda _: expected_text in self.modal_text())
        return True
