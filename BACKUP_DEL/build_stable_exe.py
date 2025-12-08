#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
穩定版 EXE 打包腳本 - 解決跨平台相容性問題
"""

import os
import subprocess
import sys

def build_stable_exe():
    """使用穩定配置打包 EXE"""
    print("🔨 開始打包穩定版 EXE...")
    
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
        '--distpath', 'dist',           # 輸出目錄
        '--workpath', 'build',          # 工作目錄
        '--name', 'PEGA_Log_Analyzer_V1.6.6_Stable',  # 執行檔名稱
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
        '--exclude-module', 'matplotlib',
        '--exclude-module', 'numpy',
        '--exclude-module', 'scipy',
        '--exclude-module', 'PIL',
        '--exclude-module', 'cv2',
        'main.py'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ 穩定版 EXE 打包完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失敗: {e}")
        return False

def create_compatibility_guide():
    """創建相容性指南"""
    guide = '''PEGA Log Analyzer V1.6.6 相容性指南
==========================================

🎯 目標系統：
- Windows 7 SP1 或更新版本
- 64位元作業系統
- 至少 2GB RAM
- 100MB 可用磁碟空間

📋 必要元件：
1. Microsoft Visual C++ 2015-2022 Redistributable
2. .NET Framework 4.7.2 或更新版本

🔧 安裝步驟：
1. 下載並安裝 Visual C++ 2015-2022 Redistributable
2. 下載並安裝 .NET Framework 4.7.2+
3. 將 EXE 檔案複製到目標電腦
4. 雙擊執行

❌ 常見問題：
Q: 程式閃退或無法啟動
A: 安裝 Visual C++ 運行時庫

Q: 缺少 DLL 檔案
A: 安裝 .NET Framework

Q: 權限錯誤
A: 以系統管理員身份執行

📞 技術支援：
檢查 Windows 事件檢視器 > Windows 記錄 > 應用程式
'''
    
    with open('dist/相容性指南.txt', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("✅ 已創建相容性指南")

def main():
    """主函數"""
    print("🚀 PEGA Log Analyzer V1.6.6 穩定版打包工具")
    print("=" * 50)
    
    if build_stable_exe():
        create_compatibility_guide()
        print("\n🎉 打包完成！")
        print("📁 輸出: dist/PEGA_Log_Analyzer_V1.6.6_Stable.exe")
        print("📋 相容性指南: dist/相容性指南.txt")
    else:
        print("❌ 打包失敗")

if __name__ == '__main__':
    main() 