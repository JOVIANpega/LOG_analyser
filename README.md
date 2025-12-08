# PEGA Log Analyzer - 測試LOG分析工具

## 📋 專案概述

<<<<<<< HEAD
PEGA Log Analyzer 是一個專門用於分析測試LOG檔案的圖形化工具，支援多種LOG格式和壓縮檔案，提供直觀的分析結果和Excel報告生成功能。
=======
## 功能特色
- 單檔/整批資料夾 Log 解析（自動分辨 PASS/FAIL 並提取細節）
- **壓縮檔 LOG 讀取**：支援 ZIP/7Z/RAR 格式，自動解壓縮並分析
- **多選壓縮檔**：選擇包含多個壓縮檔的資料夾，可勾選要處理的檔案
- **搜尋功能**：支援跨標籤頁搜尋，內建 Ctrl+F 功能
- **Tooltip 提示**：所有按鈕和輸入欄位都有詳細說明
- **加密驗證**：啟動時檢查 SIGN.txt 檔案進行授權驗證
- PASS/FAIL 分頁檢視與雙擊展開完整內容
- Excel 匯出報告
- 介面/內容字體大小調整（含 +/− 控制）
- 左右視窗分隔寬度記憶（關閉儲存、開啟套用）
- Markdown 說明檔（docs/README.md）內嵌檢視
- UI 細節優化：左側主要按鈕粗體、滑鼠靠近變色（hover）
>>>>>>> 3f570f8bd7b4d8fef1b1355ebaa580a957dfc5cd

## ✨ 主要功能

### 🔍 LOG檔案分析
- **單一檔案分析** - 支援單個LOG檔案分析
- **批量檔案分析** - 支援資料夾內多個LOG檔案批量分析
- **壓縮檔案支援** - 支援ZIP、7Z、RAR格式的壓縮檔案
- **多層壓縮** - 支援壓縮檔案內嵌壓縮檔案的遞迴解壓

### 📊 分析結果顯示
- **PASS測項** - 顯示所有通過的測試項目
- **FAIL測項** - 顯示失敗的測試項目，包含錯誤原因
- **原始LOG** - 顯示原始LOG內容，錯誤行高亮顯示
- **動態標籤頁** - 根據分析結果自動顯示/隱藏相關標籤頁

### 📈 報告生成
- **Excel報告** - 自動生成PASS/FAIL匯總Excel檔案
- **CSV處理** - 支援CSV檔案整理和格式轉換
- **格式化輸出** - 自動調整欄寬、顏色標記、字體設定

### 🎨 使用者介面
- **現代化GUI** - 基於Tkinter的現代化介面
- **字體控制** - 支援介面和內容字體大小調整
- **視窗記憶** - 自動記憶視窗大小和分割比例
- **進度顯示** - 處理過程中的進度條和時間估算

## 🚀 快速開始

### 環境需求
- Python 3.8+
- Windows 10/11 (主要測試平台)

### 安裝依賴
```bash
pip install -r requirements.txt
```

### 執行應用程式
```bash
python main.py
```

## 📁 專案結構

```
PEGA_Log_Analyzer/
├── main.py                    # 主程式入口
├── main_enhanced.py           # 增強版GUI應用程式
├── log_parser.py              # LOG檔案解析引擎
├── excel_writer.py            # Excel報告生成器
├── csv_processor.py           # CSV檔案處理器
├── ui_enhanced_fixed.py       # 增強UI元件
├── enhanced_left_panel.py     # 左側面板
├── enhanced_settings.py       # 設定頁面
├── settings_loader.py         # 設定載入器
├── requirements.txt           # 依賴套件清單
├── settings.json             # 應用程式設定
├── docs/                      # 文件資料夾
├── assets/                    # 資源檔案
└── Analysis_CSV_FILE/        # CSV分析結果輸出
```

## 🔧 功能詳解

<<<<<<< HEAD
### LOG檔案分析流程
1. **檔案選擇** - 選擇單一LOG檔案或包含LOG檔案的資料夾
2. **格式識別** - 自動識別LOG檔案格式（PEGA、IQGPRF、通用格式）
3. **內容解析** - 提取測試步驟、指令、回應、結果
4. **結果分類** - 將測試項目分為PASS和FAIL兩類
5. **錯誤分析** - 分析FAIL項目的錯誤原因和RETRY次數

### 壓縮檔案處理
- **支援格式** - ZIP、7Z、RAR
- **多選支援** - 可同時選擇多個壓縮檔案
- **資料夾掃描** - 自動掃描資料夾內所有壓縮檔案
- **遞迴解壓** - 支援壓縮檔案內嵌壓縮檔案的遞迴解壓
- **暫存管理** - 自動清理解壓縮後的暫存檔案

### Excel報告功能
- **PASS匯總** - 生成PASS測試項目的Excel報告
- **FAIL匯總** - 生成FAIL測試項目的Excel報告，包含詳細錯誤信息
- **格式優化** - 自動調整欄寬、添加顏色標記、設定字體
- **安全保存** - 避免Excel開啟時的警告訊息

## ⚙️ 設定選項

### 字體設定
- **介面字體大小** - 控制按鈕、標籤等UI元件字體大小
- **內容字體大小** - 控制LOG內容、表格等內容字體大小
- **字體聯動** - 介面字體與設定頁面字體同步

### 視窗設定
- **視窗大小記憶** - 自動記憶視窗大小
- **分割比例記憶** - 記憶左右面板分割比例
- **標籤頁記憶** - 記憶最後使用的標籤頁

### 檔案設定
- **預設路徑** - 設定檔案選擇的預設路徑
- **輸出目錄** - 設定分析結果的輸出目錄

## 🐛 已知問題與解決方案

### 壓縮檔案問題
- **7Z解壓縮失敗** - 需要安裝py7zr套件：`pip install py7zr`
- **RAR解壓縮失敗** - 需要安裝rarfile套件：`pip install rarfile`
- **取消操作無響應** - 已修復，現在會正確清理暫存檔案

### Excel檔案問題
- **開啟時出現警告** - 已修復，現在會自動設定安全屬性
- **格式問題** - 已修復，會自動清理問題字符

### 字體問題
- **字體不顯示** - 確保系統已安裝Microsoft JhengHei字體
- **字體大小不生效** - 重新啟動應用程式

## 🔄 版本歷史

### V1.9.0 (最新)
- ✅ 新增搜尋功能
- ✅ 新增Tooltip提示功能
- ✅ 新增加密驗證功能
- ✅ 新增多選壓縮檔功能
- ✅ 修復壓縮檔取消問題
- ✅ 修復Excel開啟警告
- ✅ 修復7zip解壓縮問題
- ✅ 整合壓縮檔選擇功能

### V1.7.2
- ✅ 修復原始LOG標籤頁錯誤
- ✅ 還原滑鼠懸停預覽
- ✅ 確保原始LOG正常顯示

### V1.7.1
- ✅ 修復原始LOG顯示問題

## 🚀 GitHub 本地端設置指南

### 1. 初始化Git倉庫
```bash
# 在專案目錄中初始化Git
git init

# 添加所有檔案到暫存區
git add .

# 提交初始版本
git commit -m "Initial commit: PEGA Log Analyzer V1.9.0"
```

### 2. 創建GitHub倉庫
1. 登入GitHub網站
2. 點擊右上角的"+"按鈕，選擇"New repository"
3. 填寫倉庫名稱：`PEGA-Log-Analyzer`
4. 選擇"Public"或"Private"
5. 不要勾選"Initialize this repository with a README"
6. 點擊"Create repository"

### 3. 連接本地倉庫與GitHub
```bash
# 添加遠端倉庫
git remote add origin https://github.com/YOUR_USERNAME/PEGA-Log-Analyzer.git

# 推送到GitHub
git push -u origin main
```

### 4. 日常Git操作
```bash
# 查看檔案狀態
git status
=======
### 圖示資源
- `assets/icon.png` - PNG 格式圖示（256x256 像素）
- `assets/icon.ico` - ICO 格式圖示（Windows 應用程式專用）
- 圖示規格：綠色背景，白色 "LOG" 文字

### 快速打包
使用提供的BAT檔案：
```bash
build_exe.bat          # 標準版（已包含圖示設定）
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
- **資源檔案**：`assets/`（包含圖示）、`docs/`、`settings.json`
- **圖示檔案**：`assets/icon.ico`（256x256 綠色背景 LOG 圖示）
- **依賴套件**：`tkinter`、`pandas`、`openpyxl`、`xlrd` 等

### 打包指令說明
`build_exe.bat` 已包含以下設定：
- `--icon=assets/icon.ico` - 設定應用程式圖示
- `--version-file=assets/version_info.txt` - 設定版本資訊
- `--add-data="assets;assets"` - 包含資源檔案
- 完整的隱藏匯入設定

詳細說明請參考 `EXE_打包說明.md`。

## 設定檔
- `settings.json`：記錄字體大小、視窗大小、左側面板寬度 `pane_width` 等。
- `settings_loader.py`：讀寫設定。
>>>>>>> 3f570f8bd7b4d8fef1b1355ebaa580a957dfc5cd

# 添加修改的檔案
git add .

<<<<<<< HEAD
# 提交修改
git commit -m "描述修改內容"

# 推送到GitHub
git push

# 拉取最新版本
git pull
```

### 5. 忽略檔案設定
創建`.gitignore`檔案：
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# 暫存檔案
*.tmp
*.temp
temp/
tmp/

# 分析結果
Analysis_CSV_FILE/
*.xlsx
*.csv

# 設定檔案（可選）
settings.json

# IDE
.vscode/
.idea/
*.swp
*.swo

# 系統檔案
.DS_Store
Thumbs.db
```

### 6. 分支管理
```bash
# 創建新分支
git checkout -b feature/new-feature

# 切換分支
git checkout main

# 合併分支
git merge feature/new-feature

# 刪除分支
git branch -d feature/new-feature
```

### 7. 標籤管理
```bash
# 創建標籤
git tag -a v1.8.5 -m "Version 1.8.5"

# 推送標籤
git push origin v1.8.5

# 推送所有標籤
git push origin --tags
```

## 📞 技術支援

### 常見問題
1. **程式無法啟動** - 檢查Python版本和依賴套件
2. **LOG檔案無法解析** - 檢查LOG檔案格式是否支援
3. **Excel檔案無法生成** - 檢查輸出目錄權限
4. **壓縮檔案無法解壓** - 安裝相應的解壓縮套件

### 聯絡方式
- 專案維護者：[您的姓名]
- 電子郵件：[您的郵箱]
- GitHub Issues：[倉庫Issues頁面]

## 📄 授權條款

本專案採用MIT授權條款，詳見LICENSE檔案。

## 🤝 貢獻指南

歡迎提交Issue和Pull Request來改進這個專案！

### 提交Issue
1. 檢查是否已有相同問題
2. 提供詳細的問題描述
3. 附上相關的LOG檔案或截圖

### 提交Pull Request
1. Fork專案
2. 創建功能分支
3. 提交修改
4. 創建Pull Request

---

**PEGA Log Analyzer** - 讓LOG分析變得簡單高效！ 🚀
=======
## 版本資訊
- V1.8.5
  - 新增搜尋功能：
    - **跨標籤頁搜尋**：支援在 PASS、FAIL、原始LOG 標籤頁中搜尋
    - **內建 Ctrl+F**：使用 Tkinter 內建搜尋功能，支援上下搜尋
    - **搜尋高亮**：找到的匹配文字以黃底黑字高亮顯示
    - **循環搜尋**：搜尋到末尾時自動從頭開始
  - 新增 Tooltip 提示功能：
    - **全面覆蓋**：所有按鈕和輸入欄位都有詳細說明
    - **智能顯示**：滑鼠懸停時顯示，離開時隱藏
    - **多行支援**：支援多行文字和自動換行
    - **位置追蹤**：滑鼠移動時 Tooltip 跟隨顯示
  - 新增加密驗證功能：
    - **檔案驗證**：啟動時檢查 SIGN.txt 加密檔案
    - **內容驗證**：驗證檔案內容是否包含授權字串
    - **安全啟動**：只有通過驗證才能正常使用程式
    - **錯誤提示**：驗證失敗時顯示明確的錯誤訊息
  - 新增多選壓縮檔功能：
    - **批次處理**：選擇包含多個壓縮檔的資料夾
    - **選擇性解壓**：顯示所有壓縮檔清單，可勾選要處理的檔案
    - **多層嵌套**：支援壓縮檔內還有壓縮檔的複雜結構
    - **進度顯示**：顯示解壓縮和分析進度百分比
    - **可取消操作**：處理過程中可隨時取消
- V1.7.8
  - 新增壓縮檔 LOG 讀取功能：
    - **支援格式**：ZIP、7Z、RAR 壓縮檔案
    - **自動解壓縮**：無需手動解壓縮，直接選擇壓縮檔即可
    - **智能模式**：單一 LOG 檔案自動使用單檔模式，多個 LOG 檔案使用資料夾模式
    - **多層搜尋**：支援壓縮包內多層目錄結構的 LOG 檔案搜尋
    - **自動清理**：分析完成後自動清理暫存檔案
    - **依賴套件**：新增 py7zr 和 rarfile 支援
- V1.7.7
  - 新增圖示支援：
    - **自訂圖示**：建立 256x256 像素的綠色背景 LOG 圖示
    - **打包整合**：更新 `build_exe.bat` 包含圖示設定
    - **圖示格式**：提供 PNG 和 ICO 兩種格式
    - **文件更新**：README.md 新增圖示相關說明
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

## 專案結構

### 核心檔案
- `main.py` - 主程式入口
- `main_enhanced.py` - 增強版 GUI
- `log_parser.py` - LOG 解析器
- `excel_writer.py` - Excel 匯出
- `ui_components.py` - UI 元件
- `ui_enhanced_fixed.py` - 增強版 UI 元件
- `enhanced_left_panel.py` - 左側面板
- `enhanced_settings.py` - 設定頁面
- `settings_loader.py` - 設定載入器

### 配置檔案
- `build_exe.bat` - 打包腳本
- `requirements.txt` - 依賴套件
- `settings.json` - 設定檔
- `SIGN.txt` - 加密驗證檔案

### 資源檔案
- `assets/` - 圖示與版本資訊
- `docs/` - 使用者文件
- `dist/` - 打包輸出目錄

### 備份目錄
- `BACKUP_DEL/` - 所有用不到的檔案（開發測試檔案、舊版文件、建置目錄等）

## 檔案清理記錄

### V1.7.9 檔案整理
- 將用不到的檔案集中移到 `BACKUP_DEL/` 資料夾
- 清理專案結構，保留核心檔案
- 移除開發測試檔案和快取目錄
- 統一備份檔案管理

### 已移動到 BACKUP_DEL 的檔案
- `main_enhanced_fixed.py` - 測試版本
- `generate_documentation.py` - 文件生成工具
- `PEGA_Log_Analyzer_V1.7.9.spec` - PyInstaller 規格檔
- `build/` - PyInstaller 建置目錄
- `MINE/` - 測試檔案與資料
- `dioc/` - 舊版文件目錄
- `__pycache__/` - Python 快取目錄（已刪除）

## 授權
此專案授權方式若未特別標註，預設為公司/個人內部使用。若需對外開放，請補充授權條款（LICENSE）。
>>>>>>> 3f570f8bd7b4d8fef1b1355ebaa580a957dfc5cd
