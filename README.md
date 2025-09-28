# 測試 Log 分析器 (LOG_analyser)

本工具提供圖形化介面（Tkinter）解析測試 Log，支援單檔/資料夾、多頁分頁檢視、Excel 匯出、字體大小調整、左右視窗寬度記憶、Markdown 說明檢視等功能。可於本機直接執行，亦可使用 PyInstaller 打包為單一 EXE。

## 功能特色
- 單檔/整批資料夾 Log 解析（自動分辨 PASS/FAIL 並提取細節）
- PASS/FAIL 分頁檢視與雙擊展開完整內容
- Excel 匯出報告
- 介面/內容字體大小調整（含 +/− 控制）
- 左右視窗分隔寬度記憶（關閉儲存、開啟套用）
- Markdown 說明檔（docs/README.md）內嵌檢視
- UI 細節優化：左側主要按鈕粗體、滑鼠靠近變色（hover）

## 安裝需求
- Python 3.9+（建議）
- 依需求安裝套件：
  - 參考 `requirements.txt`

安裝範例：
```
pip install -r requirements.txt
```

## 快速開始
- 增強版 GUI（預設）：
```
python main.py
```
- 標準版 GUI：
```
python main.py --classic
```

## 打包為 EXE（單一檔）
建議將圖示等資源置於 `assets/`。

範例指令（請依照實際需求調整）：
```
pyinstaller --onefile --noconsole --icon=assets/icon.ico main.py
```
程式內已提供 `get_resource_path()` 以支援打包後資源路徑（`sys._MEIPASS`）。

## 設定檔
- `settings.json`：記錄字體大小、視窗大小、左側面板寬度 `pane_width` 等。
- `settings_loader.py`：讀寫設定。

## 主要模組
- `main.py`：入口（預設啟動增強版 GUI）
- `main_enhanced.py`：增強版 GUI
- `main_standard.py`：標準版 GUI
- `log_parser.py`：Log 解析邏輯
- `excel_writer.py`：Excel 匯出
- `ui_components.py`：共用 UI 工具（字體縮放、hover、資源路徑）
- `ui_enhanced_fixed.py`：增強版 TreeView/文字檢視元件
- `docs/`：完整文件（操作指引、專案說明等）

## 版本資訊
- V1.6.9
  - 修復並增強錯誤顯示功能：
    - **修復滑鼠懸停預覽**：確保FAIL項目懸停時直接顯示錯誤原因
    - **增強原始LOG標籤頁**：
      - 新增嚴重錯誤關鍵字識別：`Segmentation fault`, `core dumped`, `executes fail`, `doesn't match`, `timeout`, `exception`, `wrong`
      - 嚴重錯誤以深紅色粗體和淺紅色背景突出顯示
      - 與FAIL標籤頁保持一致的錯誤識別邏輯
- V1.6.8
  - 全面增強GUI視覺化錯誤顯示：
    - **滑鼠懸停預覽優化**：
      - 自動識別FAIL項目並優先顯示錯誤原因
      - 錯誤原因以紅色粗體突出顯示
      - 完整內容以藍色標題分隔顯示
      - 支援多種錯誤關鍵字識別和提取
    - **修復標籤頁樣式兼容性問題**：移除不支援的樣式設定，確保程式正常運行
- V1.6.7
  - 增強錯誤顯示功能：
    - 擴展錯誤關鍵字識別：新增 `fail`, `error`, `Wrong`, `Segmentation fault`, `core dumped`, `executes fail`, `doesn't match`, `timeout`, `exception` 等
    - 多層次顏色標註系統：
      - 🔴 **紅色粗體**：主要錯誤 ("is Fail")
      - 🔴 **深紅色粗體**：嚴重錯誤 (Segmentation fault, executes fail, doesn't match 等)
      - 🟠 **橙紅色粗體**：一般錯誤關鍵字 (ERROR, error, fail, FAIL, Wrong)
      - 🟠 **橙色粗體**：錯誤代碼 (ErrorCode, Test Aborted)
      - 🔵 **藍色**：執行的指令 ((LAN) >, Run 等)
    - 改善錯誤上下文提取，讓用戶能一眼看到完整的錯誤原因和相關指令
- V1.5.6
  - FAIL測試標籤優化：
    - 錯誤原因自動顯示，切換到FAIL標籤即可看到內容，無需點擊
    - 修正錯誤原因擷取邏輯，只顯示測試項目名稱，不顯示時間戳記和錯誤代碼
    - 大字體顯示格式：例如 "Chec Frimware version is Fail"
  - 優化按鍵與視窗互動體驗：
    - 左側前三個主要按鈕（選檔/選夾/清除或選擇腳本）字體改為粗體
    - 按鈕新增滑鼠懸停變色（hover）
  - 左右視窗分隔寬度記憶：拖動後即時寫入設定、關閉時保存、開啟時套用
  - 新增「查看說明 (README)」按鈕，內嵌顯示 `docs/README.md`
  - 改良字體縮放保留粗體樣式

## 授權
此專案授權方式若未特別標註，預設為公司/個人內部使用。若需對外開放，請補充授權條款（LICENSE）。 