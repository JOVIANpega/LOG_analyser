@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

REM 1. 從 app/version.py 提取版本號 (例如 VERSION = "1.9.1")
set "APP_VERSION=1.0.0"
for /f "tokens=2 delims==" %%a in ('findstr /C:"VERSION =" "app\version.py"') do (
    set "val=%%a"
    set "val=!val:"=!"
    set "val=!val: =!"
    set "APP_VERSION=!val!"
)
set "APP_VERSION=%APP_VERSION: =%"

echo ========================================
echo PEGA Log Analyzer V%APP_VERSION% 打包工具
echo ========================================
echo [偵測版本] %APP_VERSION%
echo.

REM 檢查 PyInstaller 是否安裝
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 goto INSTALL_PYI
goto CHOOSE_MODE

:INSTALL_PYI
echo [資訊] 正在安裝 PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo [錯誤] 安裝 PyInstaller 失敗。
    pause
    exit /b 1
)

:CHOOSE_MODE
echo 請選擇打包模式：
echo [1] 單一檔案模式 (OneFile) - 啟動較慢
echo [2] 資料夾模式 (OneDir)     - 啟動最快 (建議)
set "PACK_MODE=2"
set /p "PACK_MODE=請輸入 1 或 2 (預設為 2): "

set "EXE_NAME=PEGA_Log_Analyzer_V%APP_VERSION%"
set "OPTS=--noconsole --name=%EXE_NAME%"

REM 2. 更新 assets/version_info.txt 中版本 (使用 Python 腳本確保編碼為 UTF-8)
echo [更新] 正在產出 assets\version_info.txt...
python tools\gen_version.py "%APP_VERSION%"
if errorlevel 1 (
    echo [警告] 版本資訊產生失敗，將使用舊有的。
)

REM 處理圖示
if not exist "assets\icon.ico" goto SKIP_ICON
set "OPTS=%OPTS% --icon=assets/icon.ico"
:SKIP_ICON

REM 處理模式
if "%PACK_MODE%"=="1" goto ONEFILE_SETTING
goto ONEDIR_SETTING

:ONEFILE_SETTING
echo [狀態] 模式：單一檔案 (OneFile)
set "OPTS=%OPTS% --onefile"
if not exist "owl.png" goto ADD_DATA
echo [狀態] 加入啟動畫面 (Splash Screen)...
set "OPTS=%OPTS% --splash owl.png"
goto ADD_DATA

:ONEDIR_SETTING
echo [狀態] 模式：資料夾 (OneDir)
set "OPTS=%OPTS% --onedir"
goto ADD_DATA

:ADD_DATA
REM 封裝資源與库
set "OPTS=%OPTS% --version-file=assets/version_info.txt"
set "OPTS=%OPTS% --add-data=assets;assets"
set "OPTS=%OPTS% --add-data=docs;docs"
set "OPTS=%OPTS% --add-data=IMAGES;IMAGES"
set "OPTS=%OPTS% --add-data=app;app"
set "OPTS=%OPTS% --add-data=owl.png;."
set "OPTS=%OPTS% --add-data=scare.png;."
set "OPTS=%OPTS% --add-data=settings.json;."
set "OPTS=%OPTS% --collect-all=ttkbootstrap"
set "OPTS=%OPTS% --collect-all=pandas"
set "OPTS=%OPTS% --collect-all=openpyxl"
set "OPTS=%OPTS% --collect-all=py7zr"
set "OPTS=%OPTS% --collect-all=rarfile"

REM 排除不必要的模組
set "OPTS=%OPTS% --exclude-module=matplotlib --exclude-module=scipy --exclude-module=notebook --exclude-module=sqlite3"

echo.
echo [執行] 開始打包 (pyinstaller %OPTS% main.py)...
echo.

python -m PyInstaller %OPTS% main.py

if errorlevel 1 goto ERROR_EXIT

REM --- 額外複製文件到輸出目錄的根目錄 ---
if "%PACK_MODE%"=="2" (
    echo [整理] 正在複製 HTML、IMAGES、INI 與其他文件至根目錄...
    if exist "docs" xcopy /E /I /Y "docs" "dist\%EXE_NAME%\docs" >nul
    if exist "IMAGES" xcopy /E /I /Y "IMAGES" "dist\%EXE_NAME%\IMAGES" >nul
    if exist "*.ini" copy /Y "*.ini" "dist\%EXE_NAME%\" >nul
    if exist "settings.json" copy /Y "settings.json" "dist\%EXE_NAME%\" >nul
    if exist "docs\*.html" copy /Y "docs\*.html" "dist\%EXE_NAME%\" >nul
)

goto SUCCESS_EXIT

:ERROR_EXIT
echo.
echo [失敗] 打包過程出錯。
pause
exit /b 1

:SUCCESS_EXIT
echo.
echo ========================================
echo [成功] 打包完成！版本：%APP_VERSION%
echo ========================================
echo.
if "%PACK_MODE%"=="2" echo 執行檔路徑：dist\%EXE_NAME%\%EXE_NAME%.exe
if "%PACK_MODE%"=="1" echo 執行檔路徑：dist\%EXE_NAME%.exe
echo.
pause
