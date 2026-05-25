from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage


class DashboardNotificationsPage(BasePage):
    REASSIGNMENT_PANEL = (
        By.XPATH,
        "//*[contains(normalize-space(), 'Solicitudes de reasignaci')]",
    )

    def open(self):
        self.open_path("/dashboard")

    def wait_for_reassignment_panel(self):
        return self.find_visible(self.REASSIGNMENT_PANEL)

    def notification_for_case(self, case_id):
        self.wait_for_reassignment_panel()
        return self.find_visible((
            By.XPATH,
            f"//*[contains(normalize-space(), 'Caso #{case_id}')]/ancestor::div[contains(@class, 'amber-50')]",
        ))

    def notification_text_for_case(self, case_id):
        return self.notification_for_case(case_id).text

    def has_notification_for_case(self, case_id, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda _: self.notification_for_case(case_id)
            )
            return True
        except TimeoutException:
            return False

    def dismiss_notification_for_case(self, case_id):
        notification = self.notification_for_case(case_id)
        button = notification.find_element(By.XPATH, ".//button[contains(normalize-space(), 'Descartar')]")
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        button.click()

    def open_case_from_notification(self, case_id):
        notification = self.notification_for_case(case_id)
        button = notification.find_element(By.XPATH, ".//button[contains(normalize-space(), 'Ver caso')]")
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        button.click()

    def wait_until_notification_absent(self, case_id):
        self.wait.until(EC.invisibility_of_element_located((
            By.XPATH,
            f"//*[contains(normalize-space(), 'Caso #{case_id}')]/ancestor::div[contains(@class, 'amber-50')]",
        )))
