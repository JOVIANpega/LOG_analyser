#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全打包腳本 - 不會刪除現有的 EXE 檔案
創建新的 EXE 而不影響現有檔案
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime

def create_backup():
    """備份現有的 dist 資料夾"""
    if os.path.exists('dist'):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"dist_backup_{timestamp}"
        
        print(f"📦 備份現有的 dist 資料夾到 {backup_name}...")
        try:
            shutil.copytree('dist', backup_name)
            print(f"✅ 備份完成: {backup_name}")
            return backup_name
        except Exception as e:
            print(f"❌ 備份失敗: {e}")
            return None
    return None

def build_safe_exe():
    """安全打包 EXE，不刪除現有檔案"""
    print("🔨 開始安全打包 EXE...")
    
    # 創建新的輸出目錄
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_output_dir = f"dist_new_{timestamp}"
    
    print(f"📁 使用新的輸出目錄: {new_output_dir}")
    
    # 使用 --onedir 模式，包含所有 DLL 和依賴項
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onedir',                     # 目錄模式，包含所有依賴
        '--noconsole',                  # 無控制台視窗
        '--distpath', new_output_dir,   # 指定新的輸出目錄
        '--workpath', f"build_{timestamp}",  # 指定新的工作目錄
        '--name', 'PEGA_Log_Analyzer_V1.6.6_Safe',  # 執行檔名稱
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
        print("✅ 安全打包完成")
        return new_output_dir
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失敗: {e}")
        return None

def create_safe_guide(output_dir):
    """創建安全版本說明"""
    guide = f'''PEGA Log Analyzer V1.6.6 安全版本
==========================================

🎯 特點：
✅ 完全自包含，包含所有必要的 DLL 和依賴項
✅ 不需要安裝任何額外元件
✅ 不需要 Visual C++ 運行時庫
✅ 不需要 .NET Framework
✅ 不需要 Python 環境
✅ 可在任何 Windows 7+ 電腦上直接執行
✅ 最大相容性，支援各種 Windows 版本
✅ 已修復 numpy 依賴問題
✅ 安全打包，不會刪除現有檔案

📋 系統需求：
- Windows 7 SP1 或更新版本
- 64位元作業系統
- 至少 2GB RAM
- 100MB 可用磁碟空間

🔧 使用方法：
1. 將整個 {os.path.basename(output_dir)} 資料夾複製到目標電腦
2. 雙擊 PEGA_Log_Analyzer_V1.6.6_Safe.exe 執行
3. 無需安裝任何元件，無需管理員權限

📁 檔案結構：
{os.path.basename(output_dir)}/
├── PEGA_Log_Analyzer_V1.6.6_Safe.exe  (主程式)
├── _internal/                             (內建依賴項)
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

版本: V1.6.6 安全版本 (已修復 numpy 依賴)
打包日期: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
安全打包: 不會刪除現有檔案
'''
    
    with open(f'{output_dir}/安全版本說明.txt', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("✅ 已創建安全版本說明")

def cleanup_build_files():
    """清理構建檔案，保留 dist 資料夾"""
    print("\n🧹 清理構建檔案...")
    
    # 只清理 build 資料夾，不清理 dist
    build_dirs = [d for d in os.listdir('.') if d.startswith('build_')]
    for build_dir in build_dirs:
        try:
            shutil.rmtree(build_dir)
            print(f"✅ 已清理: {build_dir}")
        except Exception as e:
            print(f"❌ 清理失敗 {build_dir}: {e}")

def main():
    """主函數"""
    print("🚀 PEGA Log Analyzer V1.6.6 安全打包工具")
    print("=" * 60)
    print("💡 這個版本完全自包含，不需要安裝任何額外元件！")
    print("🛡️ 安全打包：不會刪除您現有的 EXE 檔案！")
    print("=" * 60)
    
    # 備份現有檔案
    backup_dir = create_backup()
    
    # 安全打包
    output_dir = build_safe_exe()
    
    if output_dir:
        # 創建說明文件
        create_safe_guide(output_dir)
        
        # 清理構建檔案
        cleanup_build_files()
        
        print("\n🎉 安全打包完成！")
        print(f"📁 新輸出目錄: {output_dir}")
        print("📄 執行檔: PEGA_Log_Analyzer_V1.6.6_Safe.exe")
        print("📋 說明文件: 安全版本說明.txt")
        
        if backup_dir:
            print(f"📦 備份目錄: {backup_dir}")
        
        # 檢查檔案大小
        exe_path = f'{output_dir}/PEGA_Log_Analyzer_V1.6.6_Safe.exe'
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📊 主程式大小: {size_mb:.1f} MB")
            
        # 檢查整個資料夾大小
        if os.path.exists(output_dir):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(output_dir):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
            total_size_mb = total_size / (1024 * 1024)
            print(f"📊 整個套件大小: {total_size_mb:.1f} MB")
            
        print("\n💡 安全打包特點：")
        print("✅ 完全自包含，包含所有 DLL 檔案")
        print("✅ 不需要安裝 Visual C++ 運行時庫")
        print("✅ 不需要安裝 .NET Framework")
        print("✅ 不需要 Python 環境")
        print("✅ 可在任何 Windows 7+ 電腦上直接執行")
        print("✅ 已修復 numpy 依賴問題")
        print("🛡️ 安全打包，不會刪除現有檔案")
        
        print("\n📤 部署方式：")
        print(f"1. 將整個 {os.path.basename(output_dir)} 資料夾複製到目標電腦")
        print("2. 雙擊 PEGA_Log_Analyzer_V1.6.6_Safe.exe 執行")
        print("3. 無需安裝任何元件，無需管理員權限")
        
        print(f"\n📁 您的現有檔案仍然在: dist/")
        if backup_dir:
            print(f"📦 備份檔案在: {backup_dir}/")
        
    else:
        print("❌ 打包失敗，請檢查錯誤訊息")

if __name__ == '__main__':
    main() 