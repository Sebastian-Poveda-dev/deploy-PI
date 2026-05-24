from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from pages.base_page import BasePage


class PermissionsPage(BasePage):
    CREATE_TITLE = (By.XPATH, "//h2[normalize-space()='Crear Usuario']")
    EDIT_TITLE = (By.XPATH, "//h2[contains(normalize-space(), 'Editar')]")

    def open(self):
        self.open_path("/dashboard/permissions")

    def wait_for_table(self):
        self.find_visible((By.XPATH, "//h1[normalize-space()='Permisos']"))
        return self.table_rows()

    def table_headers(self):
        self.wait_for_table()
        return [
            header.text.strip()
            for header in self.driver.find_elements(By.CSS_SELECTOR, "thead th")
        ]

    def has_table_headers(self, expected_headers):
        headers = self.table_headers()
        return all(expected in headers for expected in expected_headers)

    def has_users(self, usernames):
        return all(self.user_exists(username) for username in usernames)

    def user_exists(self, username):
        return bool(self.row_for_user(username))

    def wait_for_user(self, username):
        return self.wait.until(lambda _: self.row_for_user(username))

    def user_has_role(self, username, role):
        return self.user_columns(username)["role"] == role

    def user_has_sala(self, username):
        sala = self.user_columns(username)["sala"]
        return bool(sala and sala != "—")

    def user_has_sala_text(self, username, sala):
        return self.user_columns(username)["sala"] == sala

    def user_has_status(self, username, status):
        return self.user_columns(username)["status"] == status

    def open_create_modal(self):
        self.click(self.button_by_text("Crear Usuario"))
        self.find_visible(self.CREATE_TITLE)

    def create_modal_is_open(self):
        return bool(self.find_visible(self.CREATE_TITLE))

    def sala_required_error_is_visible(self):
        text = self.visible_text()
        return "Selecciona una sala legal" in text or ("sala" in text.lower() and "legal" in text.lower())

    def open_edit_modal_for_user(self, username):
        row = self.row_for_user(username)
        button = row.find_element(By.XPATH, ".//button[contains(normalize-space(), 'Editar')]")
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        button.click()
        self.find_visible(self.EDIT_TITLE)

    def row_for_user(self, username):
        self.wait_for_table()
        return self.find_visible((
            By.XPATH,
            f"//tbody/tr[td[2][normalize-space()='{username}']]",
        ))

    def user_row_text(self, username):
        return self.row_for_user(username).text

    def user_columns(self, username):
        cells = self.row_for_user(username).find_elements(By.TAG_NAME, "td")
        return {
            "name": cells[0].text.strip(),
            "username": cells[1].text.strip(),
            "role": cells[2].text.strip(),
            "sala": cells[3].text.strip(),
            "status": cells[4].text.strip(),
        }

    def fill_create_user(self, data):
        field_map = {
            "first_name": "Nombre",
            "last_name": "Apellido",
            "phone_number": "Telefono",
            "email": "Correo",
            "username": "Usuario",
        }
        for key, label in field_map.items():
            if key in data:
                self.fill((By.XPATH, f"//label[contains(normalize-space(), '{label}')]/following-sibling::input"), data[key])
        if "identification_number" in data:
            self.fill((By.XPATH, "//label[contains(normalize-space(), 'dula')]/following-sibling::input"), data["identification_number"])
        if "password" in data:
            password = self.find_visible((By.XPATH, "//input[@type='password']"))
            password.clear()
            password.send_keys(data["password"])
        if "role" in data:
            self.select_role(data["role"])
        if "sala" in data:
            self.select_sala_by_text(data["sala"])

    def select_role(self, role_text):
        role_select = self.find_visible((By.XPATH, "//label[normalize-space()='Rol']/following-sibling::select"))
        Select(role_select).select_by_visible_text(role_text)

    def select_sala_by_text(self, sala_text):
        self.select_by_visible_text_contains(
            (By.XPATH, "//label[normalize-space()='Sala Legal']/following-sibling::select"),
            sala_text,
        )

    def select_first_sala(self):
        return self.select_first_real_option(
            (By.XPATH, "//label[normalize-space()='Sala Legal']/following-sibling::select")
        )

    def submit_modal(self):
        self.click((By.XPATH, "//form//button[normalize-space()='Crear' or normalize-space()='Guardar']"))

    def set_active_checkbox(self, active):
        checkbox = self.find_visible((By.ID, "is_active"))
        if checkbox.is_selected() != active:
            checkbox.click()

    def deactivate_user(self, username):
        self.open_edit_modal_for_user(username)
        self.set_active_checkbox(False)
        self.submit_modal()
        self.wait.until(lambda _: self.user_has_status(username, "Inactivo"))
