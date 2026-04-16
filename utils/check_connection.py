"""
utils/check_connection.py - Appium 連線檢查工具

用途：在跑測試之前，快速確認 Appium Server 和模擬器都正常連線。
這不是測試檔案，不會被 pytest 收集執行。

使用方式：
  python utils/check_connection.py
"""

import sys
from appium import webdriver
from appium.options.android import UiAutomator2Options


APPIUM_URL  = "http://127.0.0.1:4723"
APP_PACKAGE = "com.saucelabs.mydemoapp.rn"


def check_connection():
    print("🔍 檢查 Appium 連線...\n")

    options = UiAutomator2Options()
    options.platform_name   = "Android"
    options.device_name     = "emulator-5554"
    options.app_package     = APP_PACKAGE
    options.app_activity    = ".MainActivity"
    options.no_reset        = True
    options.full_reset      = False

    try:
        driver = webdriver.Remote(APPIUM_URL, options=options)

        print(f"✅ Appium Server 連線成功：{APPIUM_URL}")
        print(f"✅ 模擬器連線成功：{driver.capabilities.get('deviceName', 'unknown')}")
        print(f"✅ Android 版本：{driver.capabilities.get('platformVersion', 'unknown')}")
        print(f"✅ App Package：{APP_PACKAGE}")
        print("\n🎉 環境一切正常，可以開始執行測試！")

        driver.quit()
        return True

    except Exception as e:
        print(f"❌ 連線失敗：{e}")
        print("\n請確認：")
        print("  1. Appium Server 是否已啟動（執行 appium）")
        print("  2. Android Studio 模擬器是否已開啟")
        print("  3. adb devices 是否看得到 emulator-5554")
        return False


if __name__ == "__main__":
    success = check_connection()
    sys.exit(0 if success else 1)
