import os
import time
import subprocess
import logging
import smtplib
import pytest
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# ── 關鍵修正：必須先執行這行！ ────────────────────────────────────────────────
load_dotenv()


# ── 路徑與常數 ────────────────────────────────────────────────────────────────
# 1. 必須先取得目前檔案所在的目錄路徑 (先定義，後使用)
# 這樣無論專案資料夾名稱怎麼改，BASE_DIR 都會自動指向正確的實體路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. 使用 os.path.join 自動拼接路徑
# 確保在 Windows 或 Mac/Linux 都能正確處理斜線
APP_PATH = os.path.join(BASE_DIR, "apps", "sauce_labs.apk")

# App 相關配置
APP_PACKAGE    = "com.saucelabs.mydemoapp.rn"
APP_ACTIVITY   = ".MainActivity"

# Appium Server 連線位址
APPIUM_URL     = "http://localhost:4723"

# Gmail 設定（請填入你的 App Password，不是一般登入密碼）
# 使用 getenv
EMAIL_SENDER = os.getenv("GMAIL_SENDER")
EMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
EMAIL_RECEIVER = os.getenv("GMAIL_RECEIVER")

# ── 時間戳（每次執行唯一，所有產出物共用同一個時間戳）────────────────────────
RUN_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# ── 動態路徑（帶時間戳）──────────────────────────────────────────────────────
SCREENSHOT_DIR = os.path.join(BASE_DIR, "screenshots", RUN_TIMESTAMP)
ALLURE_DIR     = os.path.join(BASE_DIR, "allure-results", RUN_TIMESTAMP)
LOG_DIR        = os.path.join(BASE_DIR, "logs")
LOG_FILE       = os.path.join(LOG_DIR, f"{RUN_TIMESTAMP}.log")

for d in [SCREENSHOT_DIR, ALLURE_DIR, LOG_DIR]:
    os.makedirs(d, exist_ok=True)


# ── Logger 設定 ───────────────────────────────────────────────────────────────

def _setup_logger() -> logging.Logger:
    logger = logging.getLogger("appium_tests")
    logger.setLevel(logging.DEBUG)
    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(funcName)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 寫入帶時間戳的 log 檔
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)

    # 終端只顯示 WARNING 以上
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


logger = _setup_logger()


# ── pytest Session Hook：控制 alluredir + 執行後開報告 + 寄信 ─────────────────

def pytest_configure(config):
    """
    在 pytest 啟動時動態設定 alluredir，
    讓每次執行產生帶時間戳的獨立資料夾。
    """
    config.option.allure_report_dir = ALLURE_DIR
    logger.info(f"本次執行時間戳：{RUN_TIMESTAMP}")
    logger.info(f"Allure 結果目錄：{ALLURE_DIR}")
    logger.info(f"Log 檔案：{LOG_FILE}")
    print(f"\n📁 本次時間戳：{RUN_TIMESTAMP}")


def pytest_sessionfinish(session, exitstatus):
    """
    所有測試跑完後：
    1. 自動開啟 Allure 報告（瀏覽器）
    2. 寄送測試結果郵件到 Gmail
    """
    _open_allure_report()
    _send_email_report(session, exitstatus)


def _open_allure_report():
    """用 shell=True 確保 Scoop 安裝的 allure 能被找到"""
    print(f"\n🌐 開啟 Allure 報告：{ALLURE_DIR}")
    logger.info("開啟 Allure 報告")
    subprocess.Popen(
        f'allure serve "{ALLURE_DIR}"',
        shell=True,
        cwd=BASE_DIR
    )


def _send_email_report(session, exitstatus):
    """寄送測試結果摘要 + log 附件到 Gmail"""
    if not EMAIL_APP_PASSWORD:
        print("\n⚠️  未設定 GMAIL_PASSWORD，跳過寄信。請參考 README 設定 App Password。")
        logger.warning("GMAIL_PASSWORD 未設定，跳過寄信")
        return

    # 統計測試結果
    passed  = session.testscollected - session.testsfailed - getattr(session, 'skipped', 0)
    failed  = session.testsfailed
    total   = session.testscollected
    status  = "✅ 全部通過" if exitstatus == 0 else f"❌ {failed} 個失敗"

    subject = f"[自動化測試報告] {RUN_TIMESTAMP} - {status}"
    body = f"""
Android 自動化測試執行完成

執行時間：{RUN_TIMESTAMP}
測試結果：{status}
總計：{total} 個
通過：{passed} 個
失敗：{failed} 個

Allure 結果目錄：
{ALLURE_DIR}

Log 檔案：
{LOG_FILE}

---
此郵件由自動化測試框架自動發送
    """.strip()

    try:
        msg = MIMEMultipart()
        msg["From"]    = EMAIL_SENDER
        msg["To"]      = EMAIL_RECEIVER
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        # 附加 log 檔
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={RUN_TIMESTAMP}.log"
                )
                msg.attach(part)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_APP_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

        print(f"📧 測試報告已寄送至 {EMAIL_RECEIVER}")
        logger.info(f"測試報告已寄送至 {EMAIL_RECEIVER}")

    except Exception as e:
        print(f"⚠️  寄信失敗：{e}")
        logger.error(f"寄信失敗：{e}")


# ── pytest Hook：測試失敗自動截圖 ────────────────────────────────────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report  = outcome.get_result()

    if report.when == "call":
        if report.passed:
            logger.info(f"PASSED: {item.name}")
        elif report.failed:
            logger.error(f"FAILED: {item.name}")
            _take_screenshot(item)


def _take_screenshot(item):
    driver = item.funcargs.get("driver")
    if driver is None:
        return

    filename = f"{item.name}_{time.strftime('%H%M%S')}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)

    try:
        driver.save_screenshot(filepath)
        logger.error(f"失敗截圖：{filepath}")
        print(f"\n📸 失敗截圖：{filepath}")

        try:
            import allure
            with open(filepath, "rb") as f:
                allure.attach(
                    f.read(),
                    name=f"失敗截圖_{item.name}",
                    attachment_type=allure.attachment_type.PNG
                )
        except ImportError:
            pass

    except Exception as e:
        logger.warning(f"截圖失敗：{e}")


# ── Appium Capabilities ───────────────────────────────────────────────────────

def get_options(app_path: str) -> UiAutomator2Options:
    options = UiAutomator2Options()
    options.platform_name          = "Android"
    options.platform_version       = "13"
    options.device_name            = "emulator-5554"
    options.app                    = app_path
    options.app_package            = APP_PACKAGE
    options.app_activity           = APP_ACTIVITY
    options.automation_name        = "UiAutomator2"
    options.no_reset               = True
    options.full_reset             = False
    options.new_command_timeout    = 60
    options.auto_grant_permissions = True
    return options


# ── 導航到登入頁 ──────────────────────────────────────────────────────────────

def navigate_to_login(driver):
    logger.info("重置 App，導航到登入頁")
    print("\n🔄 重置 App，導航到登入頁...")

    subprocess.run(["adb", "shell", "am", "force-stop", APP_PACKAGE],
                   capture_output=True)
    time.sleep(0.5)

    subprocess.run(["adb", "shell", "pm", "clear", APP_PACKAGE],
                   capture_output=True)
    time.sleep(1)

    subprocess.run(
        ["adb", "shell", "am", "start", "-n", f"{APP_PACKAGE}/{APP_ACTIVITY}"],
        capture_output=True
    )
    time.sleep(3)

    subprocess.run(["adb", "shell", "input", "tap", "105", "193"],
                   capture_output=True)
    time.sleep(1.5)

    subprocess.run(["adb", "shell", "input", "tap", "378", "1499"],
                   capture_output=True)
    time.sleep(1.5)

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (AppiumBy.ACCESSIBILITY_ID, "Login button")
        )
    )
    time.sleep(0.5)

    logger.info("登入頁就緒")
    print("✅ 登入頁已就緒")


# ── Fixtures ──────────────────────────────────────────────────────────────────

def pytest_addoption(parser):
    parser.addoption("--app-path", action="store", default=APP_PATH,
                     help="APK 檔案的完整路徑")


@pytest.fixture(scope="session")
def app_path(request):
    return request.config.getoption("--app-path")


@pytest.fixture(scope="function")
def driver(app_path):
    logger.info(f"啟動 Driver - {APPIUM_URL}")
    options = get_options(app_path)

    driver = webdriver.Remote(
        command_executor=APPIUM_URL,
        options=options
    )
    driver.implicitly_wait(10)
    navigate_to_login(driver)

    yield driver

    logger.info("關閉 Driver")
    driver.quit()
