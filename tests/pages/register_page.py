from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class RegisterPage(BasePage):
    ERROR = (By.CSS_SELECTOR, ".text-red-600")
    EXTRA_FIELD_KEY = (By.XPATH, "//input[@placeholder='Nombre del campo']")
    EXTRA_FIELD_VALUE = (By.XPATH, "//input[@placeholder='Valor']")

    def open(self):
        self.open_path("/register")

    def fill_required_fields(self, data):
        self.fill(self.input_by_id("first_name"), data["first_name"])
        self.fill(self.input_by_id("last_name"), data["last_name"])
        self.fill(self.input_by_id("email"), data["email"])
        self.fill(self.input_by_id("identification_number"), data["identification_number"])
        self.fill(self.input_by_id("phone_number"), data["phone_number"])
        self.fill(self.input_by_id("residence_address"), data["residence_address"])

    def fill_optional_defaults(self):
        self.select_by_visible_text_contains(self.input_by_id("document_type"), "Cedula")
        self.fill(self.input_by_id("expedition_place"), "Cali")
        self.fill(self.input_by_id("neighborhood"), "San Fernando")
        self.fill(self.input_by_id("city"), "Cali")
        self.fill(self.input_by_id("department"), "Valle del Cauca")
        self.select_by_visible_text_contains(self.input_by_id("stratum"), "3")
        self.select_by_visible_text_contains(self.input_by_id("reception_medium"), "Presencial")
        self.fill(self.input_by_id("how_they_found_out"), "Pagina web")
        self.select_by_visible_text_contains(self.input_by_id("marital_status"), "Soltero")
        self.select_by_visible_text_contains(self.input_by_id("education_level"), "Universitario")
        self.fill(self.input_by_id("occupation"), "Independiente")

    def add_extra_field(self, key, value):
        self.click(self.button_by_text("+ Agregar campo"))
        keys = self.driver.find_elements(*self.EXTRA_FIELD_KEY)
        values = self.driver.find_elements(*self.EXTRA_FIELD_VALUE)
        keys[-1].send_keys(key)
        values[-1].send_keys(value)

    def remove_last_extra_field(self):
        remove_buttons = self.driver.find_elements(By.XPATH, "//button[@title='Eliminar campo']")
        remove_buttons[-1].click()

    def extra_fields_count(self):
        return len(self.driver.find_elements(*self.EXTRA_FIELD_KEY))

    def submit(self):
        self.click(self.button_by_text("Registrarme"))

    def error_message(self):
        return self.find_visible(self.ERROR).text
