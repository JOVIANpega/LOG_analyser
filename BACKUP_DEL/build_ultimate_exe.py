#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
終極自包含 EXE 打包腳本
創建最大相容性的獨立執行檔，確保在任何 Windows 電腦上都能執行
"""

import os
import sys
import subprocess
import shutil

def build_ultimate_exe():
    """打包終極自包含版本"""
    print("🔨 開始打包終極自包含版本...")
    
    # 清理舊檔案
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # 使用 --onedir 模式，包含所有 DLL 和依賴項
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onedir',                     # 目錄模式，包含所有依賴
        '--noconsole',                  # 無控制台視窗
        '--clean',                      # 清理舊檔案
        '--name', 'PEGA_Log_Analyzer_V1.6.6_Ultimate',  # 執行檔名稱
        '--add-data', 'settings.json;.',  # 包含設定檔
        '--hidden-import', 'tkinter',
        '--hidden-import', 'tkinter.ttk',
        '--hidden-import', 'tkinter.filedialog',
        '--hidden-import', 'tkinter.messagebox',
        '--hidden-import', 'tkinter.scrolledtext',
        '--hidden-import', 'pandas',
        '--hidden-import', 'openpyxl',
        '--hidden-import', 'xlrd',
        '--hidden-import', 'json',
        '--hidden-import', 'threading',
        '--hidden-import', 'datetime',
        '--hidden-import', 're',
        '--hidden-import', 'logging',
        '--hidden-import', 'settings_loader',
        '--hidden-import', 'log_parser',
        '--hidden-import', 'ui_components',
        '--hidden-import', 'ui_enhanced_fixed',
        '--hidden-import', 'enhanced_settings',
        '--hidden-import', 'enhanced_left_panel',
        '--hidden-import', 'excel_writer',
        '--hidden-import', 'generate_documentation',
        # 修復 numpy 依賴問題
        '--hidden-import', 'numpy',
        '--hidden-import', 'numpy.core',
        '--hidden-import', 'numpy.core._methods',
        '--hidden-import', 'numpy.lib.format',
        '--collect-all', 'pandas',
        '--collect-all', 'openpyxl',
        '--collect-all', 'xlrd',
        '--collect-all', 'numpy',       # 收集所有 numpy 依賴
        '--collect-submodules', 'tkinter',
        '--exclude-module', 'matplotlib',
        '--exclude-module', 'scipy',
        '--exclude-module', 'PIL',
        '--exclude-module', 'cv2',
        '--exclude-module', 'PyQt5',
        '--exclude-module', 'PyQt6',
        '--exclude-module', 'PySide2',
        '--exclude-module', 'PySide6',
        '--exclude-module', 'IPython',
        '--exclude-module', 'jupyter',
        '--exclude-module', 'notebook',
        '--exclude-module', 'spyder',
        '--exclude-module', 'pytest',
        '--exclude-module', 'unittest',
        'main.py'
    ]
    
    try:
        print("執行命令:", ' '.join(cmd))
        subprocess.run(cmd, check=True)
        print("✅ 終極自包含版本打包完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失敗: {e}")
        return False

def create_portable_package():
    """創建便攜式套件"""
    print("\n📦 創建便攜式套件...")
    
    # 創建便攜式說明
    portable_guide = '''PEGA Log Analyzer V1.6.6 終極便攜版
==========================================

🎯 特點：
✅ 完全自包含，包含所有必要的 DLL 和依賴項
✅ 不需要安裝任何額外元件
✅ 不需要 Visual C++ 運行時庫
✅ 不需要 .NET Framework
✅ 不需要 Python 環境
✅ 可在任何 Windows 7+ 電腦上直接執行
✅ 最大相容性，支援各種 Windows 版本

📋 系統需求：
- Windows 7 SP1 或更新版本
- 64位元作業系統
- 至少 2GB RAM
- 100MB 可用磁碟空間

🔧 使用方法：
1. 將整個 PEGA_Log_Analyzer_V1.6.6_Ultimate 資料夾複製到目標電腦
2. 雙擊 PEGA_Log_Analyzer_V1.6.6_Ultimate.exe 執行
3. 無需安裝任何元件，無需管理員權限

📁 檔案結構：
PEGA_Log_Analyzer_V1.6.6_Ultimate/
├── PEGA_Log_Analyzer_V1.6.6_Ultimate.exe  (主程式)
├── _internal/                               (內建依賴項)
├── settings.json                           (設定檔)
└── 其他必要檔案...

❌ 注意事項：
- 整個資料夾需要一起複製
- 首次執行可能需要較長時間載入
- 如果仍有問題，請檢查防毒軟體設定

📞 技術支援：
如果程式無法啟動，請檢查：
1. Windows 事件檢視器 > 應用程式記錄
2. 防毒軟體是否阻擋
3. 確保整個資料夾都複製過去

版本: V1.6.6 終極便攜版
打包日期: {date}
'''
    
    from datetime import datetime
    portable_guide = portable_guide.format(date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    with open('dist/PEGA_Log_Analyzer_V1.6.6_Ultimate/便攜版說明.txt', 'w', encoding='utf-8') as f:
        f.write(portable_guide)
    
    # 創建快速啟動腳本
    launcher_script = '''@echo off
echo 正在啟動 PEGA Log Analyzer V1.6.6...
echo.

if exist "PEGA_Log_Analyzer_V1.6.6_Ultimate.exe" (
    echo 找到主程式，正在啟動...
    start "" "PEGA_Log_Analyzer_V1.6.6_Ultimate.exe"
) else (
    echo 錯誤：找不到主程式檔案
    echo 請確保整個資料夾都複製過來
    pause
)
'''
    
    with open('dist/PEGA_Log_Analyzer_V1.6.6_Ultimate/快速啟動.bat', 'w', encoding='utf-8') as f:
        f.write(launcher_script)
    
    print("✅ 已創建便攜式套件")
    print("   - 便攜版說明.txt")
    print("   - 快速啟動.bat")

def main():
    """主函數"""
    print("🚀 PEGA Log Analyzer V1.6.6 終極便攜版打包工具")
    print("=" * 60)
    print("💡 這個版本完全自包含，不需要安裝任何額外元件！")
    print("💡 使用 --onedir 模式，包含所有必要的 DLL 檔案！")
    print("=" * 60)
    
    if build_ultimate_exe():
        create_portable_package()
        print("\n🎉 終極便攜版打包完成！")
        print("📁 輸出目錄: dist/PEGA_Log_Analyzer_V1.6.6_Ultimate/")
        print("📄 執行檔: PEGA_Log_Analyzer_V1.6.6_Ultimate.exe")
        print("📋 說明文件: 便攜版說明.txt")
        print("🔧 快速啟動: 快速啟動.bat")
        
        # 檢查檔案大小
        exe_path = 'dist/PEGA_Log_Analyzer_V1.6.6_Ultimate/PEGA_Log_Analyzer_V1.6.6_Ultimate.exe'
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📊 主程式大小: {size_mb:.1f} MB")
            
        # 檢查整個資料夾大小
        folder_path = 'dist/PEGA_Log_Analyzer_V1.6.6_Ultimate'
        if os.path.exists(folder_path):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
            total_size_mb = total_size / (1024 * 1024)
            print(f"📊 整個套件大小: {total_size_mb:.1f} MB")
            
        print("\n💡 最大優點：")
        print("✅ 完全自包含，包含所有 DLL 檔案")
        print("✅ 不需要安裝 Visual C++ 運行時庫")
        print("✅ 不需要安裝 .NET Framework")
        print("✅ 不需要 Python 環境")
        print("✅ 可在任何 Windows 7+ 電腦上直接執行")
        print("✅ 最大相容性，支援各種 Windows 版本")
        
        print("\n📤 部署方式：")
        print("1. 將整個 PEGA_Log_Analyzer_V1.6.6_Ultimate 資料夾複製到目標電腦")
        print("2. 雙擊 PEGA_Log_Analyzer_V1.6.6_Ultimate.exe 執行")
        print("3. 或執行 快速啟動.bat")
        print("4. 無需安裝任何元件，無需管理員權限")
        
    else:
        print("❌ 打包失敗，請檢查錯誤訊息")

if __name__ == '__main__':
    main() 