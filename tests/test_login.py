import allure
import pytest
from pages.login_page import LoginPage
from pages.home_page import HomePage


# ── 測試資料 ──────────────────────────────────────────────────────────────────

VALID_USERNAME  = "bob@example.com"
VALID_PASSWORD  = "10203040"
LOCKED_USERNAME = "alice@example.com"
WRONG_PASSWORD  = "wrongpassword"
WRONG_USERNAME  = "invalid@example.com"


# ── Test Suite ────────────────────────────────────────────────────────────────

@allure.feature("登入功能")
@allure.story("Login Screen")
class TestLogin:
    """
    登入功能測試套件
    App：Sauce Labs My Demo App RN（com.saucelabs.mydemoapp.rn）
    測試環境：Android 13 / Android Studio 模擬器 emulator-5554
    """

    @allure.title("TC001 - 正確帳號密碼登入成功")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_TC001_login_with_valid_credentials(self, driver):
        with allure.step("輸入正確帳號密碼並登入"):
            LoginPage(driver).login(VALID_USERNAME, VALID_PASSWORD)

        with allure.step("驗證成功進入首頁"):
            home = HomePage(driver)
            assert home.is_home_page_displayed(), \
                "登入後應顯示首頁（購物車圖示），但沒有找到"

    @allure.title("TC002 - 密碼錯誤顯示錯誤訊息")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_TC002_login_with_wrong_password(self, driver):
        with allure.step("輸入正確帳號與錯誤密碼"):
            login = LoginPage(driver)
            login.login(VALID_USERNAME, WRONG_PASSWORD)

        with allure.step("驗證顯示錯誤訊息，停留在登入頁"):
            assert login.is_generic_error_displayed(), \
                "密碼錯誤時應顯示錯誤訊息"
            assert login.is_login_button_displayed(), \
                "應仍停留在登入頁"

    @allure.title("TC003 - 帳號密碼皆空白")
    @allure.severity(allure.severity_level.NORMAL)
    def test_TC003_login_with_empty_credentials(self, driver):
        with allure.step("不輸入任何資料直接點擊登入"):
            login = LoginPage(driver)
            login.tap_login_button()

        with allure.step("驗證顯示帳號必填錯誤"):
            assert login.is_username_error_displayed(), \
                "帳號空白時應顯示帳號錯誤訊息"

    @allure.title("TC004 - 只填帳號，密碼空白")
    @allure.severity(allure.severity_level.NORMAL)
    def test_TC004_login_without_password(self, driver):
        with allure.step("輸入帳號，密碼留空"):
            login = LoginPage(driver)
            login.enter_username(VALID_USERNAME)
            login.tap_login_button()

        with allure.step("驗證顯示密碼必填錯誤"):
            assert login.is_password_error_displayed(), \
                "密碼空白時應顯示密碼錯誤訊息"

    @allure.title("TC005 - 只填密碼，帳號空白")
    @allure.severity(allure.severity_level.NORMAL)
    def test_TC005_login_without_username(self, driver):
        with allure.step("密碼填寫，帳號留空"):
            login = LoginPage(driver)
            login.enter_password(VALID_PASSWORD)
            login.tap_login_button()

        with allure.step("驗證顯示帳號必填錯誤"):
            assert login.is_username_error_displayed(), \
                "帳號空白時應顯示帳號錯誤訊息"

    @allure.title("TC006 - 鎖定帳號登入")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_TC006_login_with_locked_account(self, driver):
        with allure.step("使用鎖定帳號登入"):
            login = LoginPage(driver)
            login.login(LOCKED_USERNAME, VALID_PASSWORD)

        with allure.step("驗證顯示鎖定錯誤訊息"):
            assert login.is_generic_error_displayed(), \
                "鎖定帳號登入時應顯示錯誤訊息"

    @allure.title("TC007 - 不存在的帳號")
    @allure.severity(allure.severity_level.NORMAL)
    def test_TC007_login_with_nonexistent_user(self, driver):
        with allure.step("使用不存在帳號登入"):
            login = LoginPage(driver)
            login.login(WRONG_USERNAME, WRONG_PASSWORD)

        with allure.step("驗證顯示登入失敗錯誤"):
            assert login.is_generic_error_displayed(), \
                "不存在帳號登入時應顯示錯誤訊息"

    @allure.title("TC008 - 登入成功後登出回到登入頁")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_TC008_logout_after_successful_login(self, driver):
        """
        登出流程共四步驟：
          點 Log Out → 確認彈窗點 LOG OUT → 成功彈窗點 OK → 回到登入頁
        驗證策略：確認登入頁的 Login button 出現。
        """
        login = LoginPage(driver)
        home  = HomePage(driver)

        with allure.step("登入成功進入首頁"):
            login.login(VALID_USERNAME, VALID_PASSWORD)
            assert home.is_home_page_displayed(), \
                "前置條件失敗：未能進入首頁"

        with allure.step("執行登出"):
            home.logout()

        with allure.step("驗證登出成功（回到登入頁）"):
            assert login.is_login_button_displayed(), \
                "登出後應回到登入頁，登入按鈕應出現"
