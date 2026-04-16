from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class LoginPage(BasePage):
    """
    登入頁面 Page Object。
    元素定位優先使用 Accessibility ID（content-desc），
    穩定性優於 XPath，也更貼近使用者角度。
    """

    # ── Locators ──────────────────────────────────────────────────────────────
    # 來源：Appium Inspector 掃描 com.saucelabs.mydemoapp.rn 取得

    USERNAME_FIELD      = (AppiumBy.ACCESSIBILITY_ID, "Username input field")
    PASSWORD_FIELD      = (AppiumBy.ACCESSIBILITY_ID, "Password input field")
    LOGIN_BUTTON        = (AppiumBy.ACCESSIBILITY_ID, "Login button")

    USERNAME_ERROR_TEXT = (AppiumBy.XPATH,
                           '//android.view.ViewGroup[@content-desc="Username-error-message"]'
                           '//android.widget.TextView')
    PASSWORD_ERROR_TEXT = (AppiumBy.XPATH,
                           '//android.view.ViewGroup[@content-desc="Password-error-message"]'
                           '//android.widget.TextView')
    GENERIC_ERROR_TEXT  = (AppiumBy.XPATH,
                           '//android.view.ViewGroup[@content-desc="generic-error-message"]'
                           '//android.widget.TextView')

    # ── Actions ───────────────────────────────────────────────────────────────

    def enter_username(self, username: str):
        self.input_text(self.USERNAME_FIELD, username)

    def enter_password(self, password: str):
        self.input_text(self.PASSWORD_FIELD, password)
        self.hide_keyboard()

    def tap_login_button(self):
        self.click(self.LOGIN_BUTTON)

    def login(self, username: str, password: str):
        """完整登入流程：輸入帳號 → 輸入密碼 → 點擊登入"""
        self.enter_username(username)
        self.enter_password(password)
        self.tap_login_button()

    # ── Assertions Helpers ────────────────────────────────────────────────────

    def get_username_error(self) -> str:
        return self.get_text(self.USERNAME_ERROR_TEXT)

    def get_password_error(self) -> str:
        return self.get_text(self.PASSWORD_ERROR_TEXT)

    def get_generic_error(self) -> str:
        return self.get_text(self.GENERIC_ERROR_TEXT)

    def is_username_error_displayed(self) -> bool:
        return self.is_element_displayed(self.USERNAME_ERROR_TEXT)

    def is_password_error_displayed(self) -> bool:
        return self.is_element_displayed(self.PASSWORD_ERROR_TEXT)

    def is_generic_error_displayed(self) -> bool:
        return self.is_element_displayed(self.GENERIC_ERROR_TEXT)

    def is_login_button_displayed(self) -> bool:
        return self.is_element_displayed(self.LOGIN_BUTTON)
