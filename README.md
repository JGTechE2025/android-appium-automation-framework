# Android 自動化測試作品集

> 作者：Joe｜從手動到自動化：Android 測試框架學習與技術沉澱
> 技術棧：Python · Appium · pytest · Allure · UiAutomator2 · Android Studio

---

## 專案簡介

本專案以 **Page Object Model（POM）** 設計模式，針對 Sauce Labs My Demo App RN 實作完整的 Android 登入功能自動化測試，涵蓋 8 個測試案例，整合 Allure 產出視覺化測試報告，並於每次執行結束後自動寄送報告至 Gmail。

---

## 專案結構

```
android_appium_tests/
├── apps/                         # [手動建立] 放置測試用 .apk 檔案
├── pages/
│   ├── base_page.py              # 所有 Page 的父類別（共用操作）
│   ├── login_page.py             # 登入頁面物件
│   └── home_page.py              # 首頁物件
├── tests/
│   └── test_login.py             # 登入測試案例 TC001~TC008
├── utils/
│   └── check_connection.py       # Appium 連線檢查工具（非測試用）
├── screenshots/
│   └── 20260413_172345/          # 每次執行獨立資料夾（自動生成）
├── allure-results/
│   └── 20260413_172345/          # 每次執行獨立資料夾（自動生成）
├── logs/
│   └── 20260413_172345.log       # 每次執行獨立 log 檔（自動生成）
├── conftest.py                   # Driver、Fixture、Hook、Gmail 通知
├── requirements.txt              # 套件清單
├── pytest.ini                    # pytest 執行配置
├── .env                          # [個人本地] 儲存 Gmail App Password (已忽略)
├── .env.example                  # 環境變數設定範本 (供使用者參考)
└── README.md
```

> 所有帶時間戳的目錄與檔案均在執行時自動生成，無需手動建立。

---

## 環境需求

| 工具 | 版本 |
|---|---|
| Python | 3.11.9 |
| Appium | 2.x |
| appium-uiautomator2-driver | 最新版 |
| Node.js | 18+ |
| Android Studio | Panda 3（模擬器 API 33 / Android 13）|

---

## Appium Capabilities 設定

```python
options.platform_name          = "Android"
options.platform_version       = "13"
options.device_name            = "emulator-5554"
options.app_package            = "com.saucelabs.mydemoapp.rn"
options.app_activity           = ".MainActivity"
options.automation_name        = "UiAutomator2"
options.no_reset               = True
options.auto_grant_permissions = True
```

---

## 安裝步驟

### 1. 安裝 Python 套件

```bash
pip install -r requirements.txt
```

### 2. 安裝 Appium 與 Driver

```powershell
npm install -g appium
appium driver install uiautomator2
```

### 3. 安裝 Allure

```powershell
scoop install allure
allure --version  # 確認安裝成功
```

### 4. 設定環境變數 (資安防護)
本專案使用 python-dotenv 管理敏感資訊，嚴禁將密碼硬編碼於程式碼中。

**步驟一：開啟兩步驟驗證**
1. 前往 https://myaccount.google.com/security
2. 開啟「兩步驟驗證」

**步驟二：產生 App Password**
1. 前往 https://myaccount.google.com/apppasswords
2. 選擇「其他（自訂名稱）」，輸入 `appium-tests`
3. 點擊「產生」，複製 16 位數的密碼

**步驟三：複製 .env.example 並更名為 .env**

依照 Google App Password 指南 產生 16 位數密碼。

在 .env 中填入帳號資訊：
```python
GMAIL_SENDER=你的Email
GMAIL_APP_PASSWORD=你的16位密碼
GMAIL_RECEIVER=接收報告的Email
```
> ⚠️ **安全提醒**：`.env` 已加入 `.gitignore`。若在 CI/CD 或本地環境執行，亦可透過 PowerShell 設定暫時性的環境變數：
> ```powershell
> $env:GMAIL_APP_PASSWORD = "你的16位密碼"
> ```

### 5. 安裝 APK 到模擬器

下載：https://github.com/saucelabs/my-demo-app-rn/releases

框架已實作動態路徑自動化，無論專案放在哪個資料夾都能運作：
1. 手動建立 apps/ 資料夾
2. 將載好的 sauce_labs.apk 放入該資料夾
3. 執行安裝（可選）:

```powershell
adb install apps/sauce_labs.apk
```

### 6. 路徑自動化與環境適配
最初在 conftest.py 中使用絕對路徑來指定 APK 位置：

**初始錯誤寫法**
```python
"app": "C:\\Users\\Joe\\PycharmProjects\\android-appium-automation-framework\\apps\\demo.apk"
```
**🔧解決方案**

利用 Python 的 os 模組實作動態路徑獲取。無論專案被克隆到哪個資料夾，框架都能自動定位到專案根目錄下的 APK 檔案。

修正後的程式碼片段：
```python
import os

# 自動獲取當前檔案 (conftest.py) 的絕對路徑，並回溯到專案根目錄
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
APK_PATH = os.path.join(PROJECT_ROOT, "apps", "sauce_labs.apk")

# 在 Desired Capabilities 中使用動態路徑
options.app = APK_PATH
```
**帶來的效益**

環境零配置: 重新 Clone 專案後即可執行，不需手動修改路徑。

架構健壯性: 專案目錄改名或搬移位置，測試腳本依然能穩定運行。

---

## 執行測試

### 每次執行前

```powershell
# 確認模擬器已開機
adb devices
# 應看到：emulator-5554   device

# 啟動 Appium Server（獨立視窗，保持開著）
appium

# 可選：確認連線正常
python utils/check_connection.py
```

### 執行指令

```powershell
# 執行全部測試（自動產生 Allure 報告 + 開啟瀏覽器 + 寄信）
pytest --alluredir=allure-results/$(Get-Date -Format "yyyyMMdd_HHmmss")

# 更簡單的方式（時間戳由 conftest.py 自動處理）
pytest

# 執行指定測試案例
pytest -k TC001

# 執行指定測試檔案
pytest tests/test_login.py

# 手動開啟歷史報告
allure serve allure-results/20260413_172345
```

> **每次執行後會自動：**
> 1. 在 `allure-results/時間戳/` 產生獨立報告資料
> 2. 在 `logs/時間戳.log` 產生獨立 log 檔
> 3. 在 `screenshots/時間戳/` 儲存失敗截圖
> 4. 自動開啟瀏覽器顯示 Allure 報告
> 5. 寄送測試結果摘要 + log 附件至 Gmail

---

### Log 說明

每次執行產生獨立 log 檔，例如 `logs/20260413_172345.log`：

| 層級 | 記錄內容 |
|---|---|
| INFO | 關鍵操作步驟（Driver 啟動、導航、登入、登出）|
| WARNING | 非預期但可接受的狀況（截圖失敗、寄信失敗）|
| ERROR | 測試失敗、連線失敗 |

---

## 測試案例

| 編號 | 測試案例 | 嚴重程度 | 預期結果 |
|---|---|---|---|
| TC001 | 正確帳號密碼登入 | BLOCKER | 進入首頁，購物車出現 |
| TC002 | 密碼錯誤 | CRITICAL | 顯示錯誤訊息 |
| TC003 | 帳號密碼皆空白 | NORMAL | 顯示帳號必填錯誤 |
| TC004 | 只填帳號，密碼空白 | NORMAL | 顯示密碼必填錯誤 |
| TC005 | 只填密碼，帳號空白 | NORMAL | 顯示帳號必填錯誤 |
| TC006 | 鎖定帳號登入 | CRITICAL | 顯示鎖定錯誤訊息 |
| TC007 | 不存在的帳號 | NORMAL | 顯示登入失敗訊息 |
| TC008 | 登入成功後登出 | CRITICAL | 回到登入頁 |

### 登出流程（TC008）

```
漢堡選單 → Log Out → 彈窗①確認(LOG OUT) → 彈窗②成功(OK) → 登入頁
```

### 測試帳號

| 帳號 | 密碼 | 說明 |
|---|---|---|
| bob@example.com | 10203040 | 正常帳號 |
| alice@example.com | 10203040 | 被鎖定帳號 |

---

## 踩坑與優化紀錄

### 1. 為何選擇 Accessibility ID 優於 XPath

| 定位方式 | 穩定性 | 可讀性 | 維護成本 |
|---|---|---|---|
| Accessibility ID | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 低 |
| XPath | ⭐⭐ | ⭐⭐⭐ | 高 |
| Resource ID | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 低 |

XPath 依賴 UI 階層結構，App 改版調整佈局就會大量失效。Accessibility ID 對應元素語意名稱，更貼近使用者行為。

### 2. 解決 Android Studio 模擬器連線問題

Appium 2.x 連線路徑已從 `/wd/hub` 改為 `/`，Appium Inspector 的 Remote Path 需設定為 `/`。

### 3. 解決 App 啟動後停在商品頁的問題

**`no_reset=True` 搭配 `pm clear` 的設計邏輯：**
- `no_reset=True`：不重裝 APK，節省時間
- `pm clear`：精準清除登入 session，比 `full_reset` 快約 20%

### 4. 解決 StaleElementReferenceException

React Native 頁面重繪後 Appium 元素參考失效，改用 `adb tap` 繞過：

```python
# React Native 頁面：adb tap（繞過 StaleElement）
subprocess.run(["adb", "shell", "input", "tap", "105", "193"])

# 原生 Android Dialog：Element Click（DOM 穩定）
self.click((AppiumBy.ID, "android:id/button1"))
```

> **未來優化計畫**：改用 `WebDriverWait` 等待頁面穩定後重新定位，支援不同解析度裝置。

### 5. 憑證外洩處理與資安防護
> 曾不慎將 App 密碼上傳至 Git。隨即執行憑證輪替 (Credential Rotation)，撤銷舊密碼並導入 python-dotenv 實現資安左移 (Security Left)，確保代碼庫不含任何敏感資訊。

### 6. 解決 APK 遺失問題 (Clone 後缺少載體導致 Session 啟動失敗)
在 conftest.py 啟動前加入 os.path.exists() 判斷，若 APK 遺失則拋出友善的預檢錯誤 (Pre-check Error)，而非崩潰。

### 7. 為何在轉職之際選擇自建自動化框架

**① 實踐測試左移**：作為 QA，深知手動測試在高頻迭代中的痛點，透過自建框架能將核心邏輯封裝，實現高效的回歸測試。

**② 掌握底層邏輯**：從 WebDriver 通訊、Capabilities 配置到 POM 模式設計，全面掌握自動化開發技術，而非依賴錄製工具產出的脆弱代碼。

**③ 提升測試價值**：自動化釋放了重複勞動，使我能投入更多精力在探索性測試與複雜業務邏輯的驗證。

---

## 常見問題

| 錯誤訊息 | 原因                  | 解法 |
|---|---------------------|--|
| `MaxRetryError` | Appium Server 未啟動   | 執行 `appium` 並保持視窗開啟 |
| `TimeoutException` | 元素定位失敗              | 用 Appium Inspector 重新確認元素 ID |
| `StaleElementReferenceException` | 頁面重繪後元素失效           | 改用 adb tap 或加入重試機制 |
| `socket hang up` | UiAutomator2 server 斷線 | 增加等待時間，亦可檢查前一案案例是否正常登出，避免模擬器資源長時間占用導致通訊中斷 |
| App 停在商品頁 | 登入 session 未清除      | conftest 的 `pm clear` 自動處理 |
| `allure: command not found` | Allure 未安裝          | `scoop install allure` 後重開 PowerShell |
| 寄信失敗：SMTPAuthenticationError | `GMAIL_APP_PASSWORD` 錯誤                 | 重新產生 App Password 並更新 .env 檔案 |
| 寄信功能未啟用 | `GMAIL_APP_PASSWORD` 未填 | 確保已執行 load_dotenv() 且 .env 內容正確 |
