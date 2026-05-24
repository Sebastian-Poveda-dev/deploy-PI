from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LoginPage(BasePage):
    USERNAME = (By.ID, "username")
    PASSWORD = (By.ID, "password")
    ERROR = (By.CSS_SELECTOR, "[role='alert'], .text-\\[\\#D92D20\\]")

    def open(self):
        self.open_path("/login")

    def login_as(self, username, password):
        self.fill(self.USERNAME, username)
        self.fill(self.PASSWORD, password)
        self.click(self.button_by_text("Ingresar"))

    def error_message(self):
        return self.find_visible(self.ERROR).text
