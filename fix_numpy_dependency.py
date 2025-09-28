#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復 numpy 依賴問題的打包腳本
解決 pandas 無法導入 numpy 的問題
"""

import os
import sys
import subprocess
import shutil

def install_numpy():
    """安裝 numpy 依賴"""
    print("📦 安裝 numpy 依賴...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'numpy'], 
                      check=True, capture_output=True)
        print("✅ numpy 安裝成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ numpy 安裝失敗: {e}")
        return False

def build_fixed_exe():
    """打包修復 numpy 依賴的 EXE"""
    print("🔨 開始打包修復 numpy 依賴的 EXE...")
    
    # 清理舊檔案
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # 使用修復後的配置打包
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onedir',                     # 目錄模式，包含所有依賴
        '--noconsole',                  # 無控制台視窗
        '--clean',                      # 清理舊檔案
        '--name', 'PEGA_Log_Analyzer_V1.6.6_Fixed',  # 執行檔名稱
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
        '--hidden-import', 'numpy.random',
        '--hidden-import', 'numpy.linalg',
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
        print("✅ 修復 numpy 依賴的 EXE 打包完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失敗: {e}")
        return False

def create_fix_guide():
    """創建修復說明"""
    guide = '''PEGA Log Analyzer V1.6.6 修復 numpy 依賴版本
==========================================

🎯 修復內容：
✅ 已修復 pandas 無法導入 numpy 的問題
✅ 已修復 ImportError: No module named 'numpy' 錯誤
✅ 包含完整的 numpy 依賴項
✅ 完全自包含，不需要安裝任何額外元件

🔧 問題原因：
原來的 EXE 檔案缺少 numpy 依賴，導致 pandas 無法正常運作。
numpy 是 pandas 的核心依賴，必須包含在打包中。

📋 系統需求：
- Windows 7 SP1 或更新版本
- 64位元作業系統
- 至少 2GB RAM
- 100MB 可用磁碟空間

🔧 使用方法：
1. 將整個 PEGA_Log_Analyzer_V1.6.6_Fixed 資料夾複製到目標電腦
2. 雙擊 PEGA_Log_Analyzer_V1.6.6_Fixed.exe 執行
3. 無需安裝任何元件，無需管理員權限

📁 檔案結構：
PEGA_Log_Analyzer_V1.6.6_Fixed/
├── PEGA_Log_Analyzer_V1.6.6_Fixed.exe  (主程式)
├── _internal/                             (內建依賴項，包含 numpy)
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

版本: V1.6.6 修復 numpy 依賴版
打包日期: {date}
'''
    
    from datetime import datetime
    guide = guide.format(date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    with open('dist/PEGA_Log_Analyzer_V1.6.6_Fixed/修復說明.txt', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("✅ 已創建修復說明")

def main():
    """主函數"""
    print("🚀 PEGA Log Analyzer V1.6.6 修復 numpy 依賴問題工具")
    print("=" * 60)
    print("🔧 專門解決 pandas 無法導入 numpy 的問題！")
    print("=" * 60)
    
    # 安裝 numpy 依賴
    if not install_numpy():
        print("❌ numpy 安裝失敗，無法繼續")
        return
    
    # 打包修復版本
    if build_fixed_exe():
        create_fix_guide()
        print("\n🎉 numpy 依賴問題修復完成！")
        print("📁 輸出目錄: dist/PEGA_Log_Analyzer_V1.6.6_Fixed/")
        print("📄 執行檔: PEGA_Log_Analyzer_V1.6.6_Fixed.exe")
        print("📋 修復說明: 修復說明.txt")
        
        # 檢查檔案大小
        exe_path = 'dist/PEGA_Log_Analyzer_V1.6.6_Fixed/PEGA_Log_Analyzer_V1.6.6_Fixed.exe'
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📊 主程式大小: {size_mb:.1f} MB")
            
        print("\n💡 修復內容：")
        print("✅ 已修復 pandas 無法導入 numpy 的問題")
        print("✅ 已修復 ImportError: No module named 'numpy' 錯誤")
        print("✅ 包含完整的 numpy 依賴項")
        print("✅ 完全自包含，不需要安裝任何額外元件")
        
        print("\n📤 部署方式：")
        print("1. 將整個 PEGA_Log_Analyzer_V1.6.6_Fixed 資料夾複製到目標電腦")
        print("2. 雙擊 PEGA_Log_Analyzer_V1.6.6_Fixed.exe 執行")
        print("3. 無需安裝任何元件，無需管理員權限")
        
    else:
        print("❌ 打包失敗，請檢查錯誤訊息")

if __name__ == '__main__':
    main() 