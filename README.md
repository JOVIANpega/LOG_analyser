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

### 快速打包
使用提供的BAT檔案：
```bash
build_exe_fixed.bat    # 修復版（推薦）
build_exe.bat          # 標準版
build_exe_advanced.bat # 進階版
```

### 手動打包
```bash
pyinstaller --onefile --noconsole --icon=assets/icon.ico --name="PEGA_Log_Analyzer_V1.7.1" main_enhanced.py
```

### 完整打包指令
```bash
pyinstaller --onefile --noconsole --icon=assets/icon.ico --name="PEGA_Log_Analyzer_V1.7.1" --version-file=assets/version_info.txt --add-data="assets;assets" --add-data="docs;docs" --add-data="settings.json;." --hidden-import=tkinter --hidden-import=tkinter.ttk --hidden-import=tkinter.messagebox --hidden-import=tkinter.filedialog --hidden-import=tkinter.scrolledtext --hidden-import=openpyxl --hidden-import=pandas --hidden-import=xlrd --hidden-import=re --hidden-import=json --hidden-import=os --hidden-import=sys --hidden-import=datetime --hidden-import=threading --hidden-import=webbrowser --hidden-import=settings_loader --hidden-import=log_parser --hidden-import=ui_components --hidden-import=ui_enhanced_fixed --hidden-import=enhanced_settings --hidden-import=enhanced_left_panel --hidden-import=excel_writer --hidden-import=generate_documentation --collect-all=pandas --collect-all=openpyxl --collect-all=xlrd main_enhanced.py
```

程式內已提供 `get_resource_path()` 以支援打包後資源路徑（`sys._MEIPASS`）。

### 打包檔案清單
- **核心檔案**：`main_enhanced.py` 及所有自定義模組
- **資源檔案**：`assets/`、`docs/`、`settings.json`
- **依賴套件**：`tkinter`、`pandas`、`openpyxl`、`xlrd` 等

詳細說明請參考 `EXE_打包說明.md`。

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
- V1.7.1
  - 優化Excel顯示效果：
    - **調整行高**：增加Excel行高以顯示更多文字內容
    - **統一字體大小**：所有Excel內容字體統一設為11號
    - **改善文字顯示**：Summary頁面和LOG工作表的文字內容更清晰易讀
- V1.7.6
  - 修復資料夾分析功能：
    - **原始LOG標籤頁顯示**：資料夾分析時自動合併所有FAIL LOG內容到原始LOG標籤頁，並套用顏色突出顯示
    - **Excel Summary詳細化**：FAIL匯總.xlsx的Summary頁面現在顯示詳細錯誤原因，包含主要錯誤、錯誤詳情和執行指令
    - **錯誤資訊完整性**：Excel中每個LOG的錯誤摘要包含多層次資訊，便於快速了解失敗原因
- V1.7.5
  - 增強資料夾分析和Excel匯出功能：
    - **統一錯誤提取邏輯**：左視窗選擇資料夾時使用與單檔案相同的錯誤提取邏輯
    - **Excel Summary頁面優化**：FAIL匯總.xlsx第一頁標題改為"Summary of Sheet Page"
    - **主要錯誤原因顯示**：在Excel中顯示每個LOG的主要錯誤原因，使用統一的錯誤識別邏輯
    - **錯誤原因分組**：Excel中按錯誤原因分組顯示，便於快速識別相同類型的錯誤
    - **資料夾分析預覽**：左側視窗顯示分析預覽，包含PASS/FAIL檔案分類和主要錯誤原因
    - **"doesn't match"錯誤突出顯示**：在Excel和GUI中特別標記 "doesn't match" 相關錯誤
- V1.7.4
  - 全面增強LOG顯示功能：
    - **添加行數顯示**：所有LOG內容現在都顯示行數（1, 2, 3, 4...）
    - **修復搜尋功能**：解決搜尋時的遞歸錯誤問題
    - **突出顯示 "doesn't match"**：特別標記並優先顯示 "doesn't match" 錯誤
    - **錯誤原因區塊置頂**：將錯誤原因區塊移到最上面顯示，標題為"===============錯誤原因===================="
    - **多層次錯誤分類**：保持原有的錯誤類型顏色標註系統
- V1.7.3
  - 增強FAIL測項標籤頁：
    - **顯示所有錯誤**：FAIL測項標籤頁現在顯示所有錯誤，不再只顯示部分內容
    - **標題優化**：標題改為"🔴 所有錯誤"，並添加分隔線
    - **錯誤分類顯示**：所有突顯的錯誤文字都會被收集並分類顯示
    - **多層次顏色標註**：保持原有的錯誤類型顏色標註系統
- V1.7.2
  - 修復並還原功能：
    - **修復原始LOG標籤頁錯誤**：解決 `'EnhancedText' object has no attribute '_is_error_line'` 錯誤
    - **還原滑鼠懸停預覽**：恢復到上一個顯示方式，只顯示第一個錯誤原因
    - **確保原始LOG正常顯示**：移除有問題的方法調用，使用內聯錯誤檢查
- V1.7.1
  - 修復並增強錯誤顯示功能：
    - **修復原始LOG顯示問題**：確保原始LOG內容能正確顯示
    - **滑鼠懸停預覽全面優化**：
      - 顯示所有錯誤原因列表，不再只顯示第一個
      - 錯誤原因和完整內容以紅色粗體+淡黃色背景整行突出顯示
      - 自動為錯誤行添加🔴標記
      - 標題改為"🔴 所有錯誤原因"
- V1.7.0
  - 全面優化錯誤顯示和用戶體驗：
    - **滑鼠懸停預覽增強**：
      - 錯誤原因和完整內容以紅色粗體+淡黃色背景整行突出顯示
      - 自動為錯誤行添加🔴標記
    - **原始LOG標籤頁智能聚焦**：
      - 分析完成後自動切換到原始LOG標籤頁
      - 自動聚焦到第一個錯誤位置，無需手動搜尋
    - **統一錯誤識別邏輯**：
      - FAIL標籤頁和原始LOG標籤頁使用相同的錯誤關鍵字識別
      - 確保所有錯誤類型都能被正確識別和突出顯示
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