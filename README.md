# PEGA Log Analyzer - 測試LOG分析工具

## 📋 專案概述

PEGA Log Analyzer 是一個專門用於分析測試LOG檔案的圖形化工具，支援多種LOG格式和壓縮檔案，提供直觀的分析結果和Excel報告生成功能。

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

### V1.8.5 (最新)
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
git commit -m "Initial commit: PEGA Log Analyzer V1.8.5"
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

# 添加修改的檔案
git add .

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