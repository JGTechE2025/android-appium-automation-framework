from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class BasePage:
    """
    所有 Page Object 的父類別。
    統一管理等待、點擊、輸入等基本操作，子類別直接繼承使用。
    """

    DEFAULT_TIMEOUT = 10

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, self.DEFAULT_TIMEOUT)

    def wait_for_element(self, locator, timeout=None):
        t = timeout or self.DEFAULT_TIMEOUT
        try:
            return WebDriverWait(self.driver, t).until(
                EC.presence_of_element_located(locator)
            )
        except TimeoutException:
            raise TimeoutException(f"找不到元素 {locator}，已等待 {t} 秒")

    def wait_for_element_clickable(self, locator, timeout=None):
        t = timeout or self.DEFAULT_TIMEOUT
        return WebDriverWait(self.driver, t).until(
            EC.element_to_be_clickable(locator)
        )

    def wait_for_element_visible(self, locator, timeout=None):
        t = timeout or self.DEFAULT_TIMEOUT
        return WebDriverWait(self.driver, t).until(
            EC.visibility_of_element_located(locator)
        )

    def click(self, locator):
        self.wait_for_element_clickable(locator).click()

    def input_text(self, locator, text):
        element = self.wait_for_element_clickable(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator):
        return self.wait_for_element_visible(locator).text

    def is_element_displayed(self, locator, timeout=5):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return element.is_displayed()
        except (TimeoutException, NoSuchElementException):
            return False

    def hide_keyboard(self):
        try:
            self.driver.hide_keyboard()
        except Exception:
            pass
