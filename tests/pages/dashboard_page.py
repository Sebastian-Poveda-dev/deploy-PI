from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class DashboardPage(BasePage):
    CASE_COUNTERS = (By.XPATH, "//*[contains(text(), 'Activo') or contains(text(), 'Pendiente') or contains(text(), 'ACTIVE') or contains(text(), 'PENDING')]")

    def open(self):
        self.open_path("/dashboard")

    def open_cases(self):
        self.open_path("/dashboard/cases")

    def is_loaded(self):
        return self.has_text("Bienvenido")

    def case_counter_text(self):
        return " ".join(element.text for element in self.driver.find_elements(*self.CASE_COUNTERS))
