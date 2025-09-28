#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完全自包含 EXE 打包腳本
創建不需要安裝任何額外元件的獨立執行檔
"""

import os
import sys
import subprocess

def build_standalone_exe():
    """打包完全自包含的 EXE"""
    print("🔨 開始打包完全自包含 EXE...")
    
    # 清理舊檔案
    if os.path.exists('dist'):
        import shutil
        shutil.rmtree('dist')
    
    # 使用 PyInstaller 打包，包含所有依賴項
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',                    # 單一檔案
        '--noconsole',                  # 無控制台視窗
        '--clean',                      # 清理舊檔案
        '--name', 'PEGA_Log_Analyzer_V1.6.6_Standalone',  # 執行檔名稱
        '--add-data', 'settings.json;.',  # 包含設定檔
        '--hidden-import', 'tkinter',
        '--hidden-import', 'tkinter.ttk',
        '--hidden-import', 'tkinter.filedialog',
        '--hidden-import', 'tkinter.messagebox',
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
        '--collect-all', 'pandas',      # 收集所有 pandas 依賴
        '--collect-all', 'openpyxl',    # 收集所有 openpyxl 依賴
        '--collect-all', 'xlrd',        # 收集所有 xlrd 依賴
        '--collect-all', 'numpy',       # 收集所有 numpy 依賴
        '--collect-submodules', 'tkinter',  # 收集所有 tkinter 子模組
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
        print("✅ 完全自包含 EXE 打包完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失敗: {e}")
        return False

def create_standalone_guide():
    """創建自包含版本說明"""
    guide = '''PEGA Log Analyzer V1.6.6 完全自包含版本
==========================================

🎯 特點：
✅ 完全自包含，不需要安裝任何額外元件
✅ 不需要 Visual C++ 運行時庫
✅ 不需要 .NET Framework
✅ 不需要 Python 環境
✅ 可在任何 Windows 7+ 電腦上直接執行

📋 系統需求：
- Windows 7 SP1 或更新版本
- 64位元作業系統
- 至少 2GB RAM
- 100MB 可用磁碟空間

🔧 使用方法：
1. 將 PEGA_Log_Analyzer_V1.6.6_Standalone.exe 複製到目標電腦
2. 雙擊執行即可，無需安裝任何元件
3. 首次執行可能需要較長時間載入

❌ 注意事項：
- 檔案大小會比標準版本大一些
- 首次啟動時間較長
- 如果仍有問題，請檢查防毒軟體設定

📞 技術支援：
如果程式無法啟動，請檢查：
1. Windows 事件檢視器 > 應用程式記錄
2. 防毒軟體是否阻擋
3. 系統權限設定

版本: V1.6.6 完全自包含版
打包日期: {date}
'''
    
    from datetime import datetime
    guide = guide.format(date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    with open('dist/自包含版本說明.txt', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("✅ 已創建自包含版本說明")

def main():
    """主函數"""
    print("🚀 PEGA Log Analyzer V1.6.6 完全自包含版本打包工具")
    print("=" * 60)
    print("💡 這個版本不需要在其他電腦安裝任何額外元件！")
    print("=" * 60)
    
    if build_standalone_exe():
        create_standalone_guide()
        print("\n🎉 完全自包含版本打包完成！")
        print("📁 輸出目錄: dist/")
        print("📄 執行檔: PEGA_Log_Analyzer_V1.6.6_Standalone.exe")
        print("📋 說明文件: dist/自包含版本說明.txt")
        
        # 檢查檔案大小
        exe_path = 'dist/PEGA_Log_Analyzer_V1.6.6_Standalone.exe'
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📊 檔案大小: {size_mb:.1f} MB")
            
        print("\n💡 優點：")
        print("✅ 不需要安裝 Visual C++ 運行時庫")
        print("✅ 不需要安裝 .NET Framework")
        print("✅ 不需要 Python 環境")
        print("✅ 可在任何 Windows 7+ 電腦上直接執行")
        
        print("\n📤 部署方式：")
        print("1. 將 EXE 檔案複製到目標電腦")
        print("2. 雙擊執行即可，無需安裝任何元件")
        
    else:
        print("❌ 打包失敗，請檢查錯誤訊息")

if __name__ == '__main__':
    main() 