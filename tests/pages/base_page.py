import os
import unicodedata

from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


BASE_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


def strip_accents(value):
    normalized = unicodedata.normalize("NFKD", value or "")
    return "".join(ch for ch in normalized if not unicodedata.combining(ch)).lower()


class BasePage:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open_path(self, path):
        self.driver.get(f"{BASE_URL}{path}")

    def wait_for_url_contains(self, fragment):
        self.wait.until(EC.url_contains(fragment))

    def wait_until_ready(self):
        self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")

    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def click(self, locator):
        element = self.find_clickable(locator)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        try:
            element.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", element)

    def fill(self, locator, value):
        field = self.find_visible(locator)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)
        field.clear()
        field.send_keys(value)

    def select_first_real_option(self, locator):
        select = Select(self.find_visible(locator))
        for option in select.options:
            if option.get_attribute("value"):
                select.select_by_value(option.get_attribute("value"))
                return option.text
        raise AssertionError("No selectable option found")

    def select_by_visible_text_contains(self, locator, expected_text):
        select = Select(self.find_visible(locator))
        expected = strip_accents(expected_text)
        for option in select.options:
            if expected in strip_accents(option.text):
                select.select_by_visible_text(option.text)
                return option.text
        raise AssertionError(f"No option containing '{expected_text}' found")

    def visible_text(self):
        return self.find_visible((By.TAG_NAME, "body")).text

    def has_text(self, expected_text, timeout=10):
        expected = strip_accents(expected_text)
        wait = WebDriverWait(self.driver, timeout)
        try:
            return wait.until(lambda _: expected in strip_accents(self.visible_text()))
        except TimeoutException:
            return False

    def button_by_text(self, text):
        return (
            By.XPATH,
            f"//button[normalize-space()='{text}' or contains(normalize-space(), '{text}')]",
        )

    def link_by_text(self, text):
        return (
            By.XPATH,
            f"//a[normalize-space()='{text}' or contains(normalize-space(), '{text}')]",
        )

    def input_by_id(self, field_id):
        return (By.ID, field_id)

    def table_rows(self):
        def rows_are_stable(driver):
            try:
                rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
                return rows if rows else False
            except StaleElementReferenceException:
                return False

        return self.wait.until(rows_are_stable)
