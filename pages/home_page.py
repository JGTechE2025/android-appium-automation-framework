import time
import subprocess
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class HomePage(BasePage):
    """
    登入成功後的商品首頁 Page Object。
    """

    # ── Locators ──────────────────────────────────────────────────────────────

    MENU_BUTTON     = (AppiumBy.ACCESSIBILITY_ID, "open menu")
    CART_BUTTON     = (AppiumBy.ACCESSIBILITY_ID, "cart badge")
    LOGOUT_BUTTON   = (AppiumBy.ACCESSIBILITY_ID, "menu item log out")

    # 原生 Android Dialog 按鈕（resource-id 定位，比座標更穩定）
    DIALOG_CONFIRM  = (AppiumBy.ID, "android:id/button1")  # LOG OUT / OK 按鈕
    DIALOG_CANCEL   = (AppiumBy.ID, "android:id/button2")  # CANCEL 按鈕

    # ── Assertions Helpers ────────────────────────────────────────────────────

    def is_home_page_displayed(self) -> bool:
        return self.is_element_displayed(self.CART_BUTTON)

    def is_cart_icon_displayed(self) -> bool:
        return self.is_element_displayed(self.CART_BUTTON)

    def is_menu_button_displayed(self) -> bool:
        return self.is_element_displayed(self.MENU_BUTTON)

    # ── Actions ───────────────────────────────────────────────────────────────

    def open_menu(self):
        self.click(self.MENU_BUTTON)

    def logout(self):
        """
        完整登出流程（共四步驟）：
          1. adb tap 點擊漢堡選單
          2. adb tap 點擊 Log Out（觸發第一個確認彈窗）
          3. Element Click 點擊「LOG OUT」確認登出
          4. Element Click 點擊「OK」關閉登出成功彈窗
          → 最終停留在登入頁面

        說明：
        - 步驟 1、2 用 adb tap 繞過 React Native 重繪的 StaleElement 問題
        - 步驟 3、4 是原生 Android Dialog，DOM 穩定，直接用 Element Click
        - 兩個彈窗的確認按鈕都是 android:id/button1，共用同一個 locator

        座標來源：Appium Inspector XML（模擬器解析度 1080x2209）
          open menu:         bounds [53,141][158,246]   → (105, 193)
          menu item log out: bounds [0,1579][756,1739]  → (378, 1659)
        """
        # Step 1：點擊漢堡選單
        subprocess.run(["adb", "shell", "input", "tap", "105", "193"],
                       capture_output=True)
        time.sleep(1.5)

        # Step 2：點擊 Log Out（觸發確認彈窗）
        subprocess.run(["adb", "shell", "input", "tap", "378", "1659"],
                       capture_output=True)
        time.sleep(1.5)

        # Step 3：點擊確認彈窗的「LOG OUT」按鈕
        self.click(self.DIALOG_CONFIRM)
        time.sleep(1.5)

        # Step 4：點擊登出成功彈窗的「OK」按鈕
        self.click(self.DIALOG_CONFIRM)
        time.sleep(1.5)
