@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo ========================================
echo PEGA Log Analyzer V1.9.0 打包工具
echo ========================================
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

set "EXE_NAME=PEGA_Log_Analyzer_V1.9.0"
set "OPTS=--noconsole --name=%EXE_NAME%"

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
set "OPTS=%OPTS% --add-data=app;app"
set "OPTS=%OPTS% --add-data=owl.png;."
set "OPTS=%OPTS% --add-data=scare.png;."
set "OPTS=%OPTS% --add-data=settings.json;."
set "OPTS=%OPTS% --collect-all=ttkbootstrap"
set "OPTS=%OPTS% --collect-all=pandas"
set "OPTS=%OPTS% --collect-all=openpyxl"
set "OPTS=%OPTS% --collect-all=py7zr"
set "OPTS=%OPTS% --collect-all=rarfile"

REM 排除不必要的模組以加速啟動並縮小體積
set "OPTS=%OPTS% --exclude-module=matplotlib --exclude-module=scipy --exclude-module=notebook --exclude-module=sqlite3"

echo.
echo [執行] 開始啟動打包程式 (pyinstaller %OPTS% main.py)...
echo.

REM 嘗試使用 python -m PyInstaller 確保環境一致
python -m PyInstaller %OPTS% main.py

if errorlevel 1 goto ERROR_EXIT
goto SUCCESS_EXIT

:ERROR_EXIT
echo.
echo [失敗] 打包過程出錯，請檢查上方輸出。
pause
exit /b 1

:SUCCESS_EXIT
echo.
echo ========================================
echo [成功] 打包完成！
echo ========================================
echo.
if "%PACK_MODE%"=="2" echo 執行檔路徑：dist\%EXE_NAME%\%EXE_NAME%.exe
if "%PACK_MODE%"=="1" echo 執行檔路徑：dist\%EXE_NAME%.exe
echo.
pause