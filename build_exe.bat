@echo off
echo ========================================
echo PEGA Log Analyzer V1.9.0 打包工具
echo ========================================
echo.

REM 檢查Python是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo 錯誤：未找到Python，請先安裝Python 3.9+
    pause
    exit /b 1
)

REM 檢查PyInstaller是否安裝
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo 正在安裝PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo 錯誤：PyInstaller安裝失敗
        pause
        exit /b 1
    )
)

echo 開始打包EXE檔案...
echo.

REM 清理舊的build和dist目錄
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

REM 使用PyInstaller打包（包含圖示）
echo 正在執行PyInstaller...
pyinstaller --onefile ^
    --noconsole ^
    --name="PEGA_Log_Analyzer_V1.9.0" ^
    --icon=assets/icon.ico ^
    --version-file=assets/version_info.txt ^
    --add-data="assets;assets" ^
    --add-data="docs;docs" ^
    --add-data="settings.json;." ^
    --add-data="app;app" ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.ttk ^
    --hidden-import=tkinter.messagebox ^
    --hidden-import=tkinter.filedialog ^
    --hidden-import=tkinter.scrolledtext ^
    --hidden-import=openpyxl ^
    --hidden-import=pandas ^
    --hidden-import=xlrd ^
    --hidden-import=re ^
    --hidden-import=json ^
    --hidden-import=os ^
    --hidden-import=sys ^
    --hidden-import=datetime ^
    --hidden-import=threading ^
    --hidden-import=webbrowser ^
    --hidden-import=app.settings_loader ^
    --hidden-import=app.log_parser ^
    --hidden-import=app.ui_components ^
    --hidden-import=app.ui_enhanced_fixed ^
    --hidden-import=app.enhanced_settings ^
    --hidden-import=app.enhanced_left_panel ^
    --hidden-import=app.excel_writer ^
    --hidden-import=app.csv_processor ^
    --hidden-import=app.main_app ^
    --hidden-import=app.main_app_full ^
    --hidden-import=app.file_handlers ^
    --hidden-import=app.config_manager ^
    --hidden-import=app.progress_manager ^
    --hidden-import=app.search_handler ^
    --hidden-import=app.result_display ^
    --hidden-import=app.analysis_engine ^
    --hidden-import=app.ui_builder ^
    --hidden-import=py7zr ^
    --hidden-import=rarfile ^
    --collect-all=pandas ^
    --collect-all=openpyxl ^
    --collect-all=xlrd ^
    --collect-all=py7zr ^
    --collect-all=rarfile ^
    main_enhanced.py

if errorlevel 1 (
    echo.
    echo 錯誤：打包失敗！
    pause
    exit /b 1
)

echo.
echo ========================================
echo 打包完成！
echo ========================================
echo.
echo EXE檔案位置：dist\PEGA_Log_Analyzer_V1.9.0.exe
echo.

REM 複製設定檔和HTML文件到dist目錄
echo 正在複製設定檔和文件...
if exist "settings.json" copy "settings.json" "dist\"
if exist "docs\USER_GUIDE.html" copy "docs\USER_GUIDE.html" "dist\"
if exist "SIGN.txt" copy "SIGN.txt" "dist\"
echo 設定檔、HTML文件和加密檔案已複製到dist目錄

REM 檢查檔案是否存在
if exist "dist\PEGA_Log_Analyzer_V1.9.0.exe" (
    echo 檔案大小：
    dir "dist\PEGA_Log_Analyzer_V1.9.0.exe" | findstr "PEGA_Log_Analyzer_V1.9.0.exe"
    echo.
    echo 是否要開啟dist目錄？
    set /p choice="請輸入 y 或 n: "
    if /i "%choice%"=="y" (
        explorer dist
    )
) else (
    echo 錯誤：EXE檔案未生成！
)

echo.
echo dist目錄內容：
dir dist

echo.
echo 按任意鍵結束...
pause >nul