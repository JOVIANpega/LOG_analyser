#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PEGA Log Analyzer V1.6.6 打包腳本
解決跨平台相容性問題，確保 EXE 檔案可在其他 PC 正常執行
"""

import os
import sys
import subprocess
import shutil

def create_spec_file():
    """創建優化的 PyInstaller spec 檔案"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('settings.json', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'pandas',
        'openpyxl',
        'xlrd',
        'json',
        'os',
        'sys',
        'threading',
        'datetime',
        're',
        'logging',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'PIL',
        'cv2',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PEGA_Log_Analyzer_V1.6.6',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
    version_file=None,
    uac_admin=False,
    uac_uiaccess=False,
)
'''
    
    with open('PEGA_Log_Analyzer_V1.6.6.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 已創建優化的 spec 檔案")

def install_dependencies():
    """安裝必要的依賴項"""
    print("📦 安裝依賴項...")
    
    dependencies = [
        'pyinstaller>=5.0.0',
        'pandas>=1.5.0',
        'openpyxl>=3.0.0',
        'xlrd>=2.0.0',
    ]
    
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], check=True)
            print(f"✅ 已安裝 {dep}")
        except subprocess.CalledProcessError:
            print(f"❌ 安裝 {dep} 失敗")

def build_exe():
    """使用 PyInstaller 打包 EXE"""
    print("🔨 開始打包 EXE...")
    
    # 清理舊的構建檔案
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # 使用 spec 檔案打包
    try:
        subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            'PEGA_Log_Analyzer_V1.6.6.spec'
        ], check=True)
        print("✅ EXE 打包完成")
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失敗: {e}")
        return False
    
    return True

def create_installer_info():
    """創建安裝說明檔案"""
    installer_info = '''PEGA Log Analyzer V1.6.6 安裝說明
==========================================

系統需求：
- Windows 7/8/10/11 (64位元)
- 至少 100MB 可用磁碟空間
- 建議 4GB 以上記憶體

安裝步驟：
1. 將 PEGA_Log_Analyzer_V1.6.6.exe 複製到目標電腦
2. 雙擊執行，首次執行可能需要較長時間
3. 如果出現錯誤，請安裝 Visual C++ 2015-2022 運行時庫

常見問題解決：
Q: 程式無法啟動？
A: 請安裝 Microsoft Visual C++ 2015-2022 Redistributable

Q: 缺少 DLL 檔案？
A: 請安裝 .NET Framework 4.7.2 或更新版本

Q: 權限不足？
A: 請以系統管理員身份執行

技術支援：
如有問題，請檢查 Windows 事件檢視器中的錯誤訊息
'''
    
    with open('dist/安裝說明.txt', 'w', encoding='utf-8') as f:
        f.write(installer_info)
    
    print("✅ 已創建安裝說明檔案")

def main():
    """主函數"""
    print("🚀 PEGA Log Analyzer V1.6.6 打包工具")
    print("=" * 50)
    
    # 檢查 Python 版本
    if sys.version_info < (3, 7):
        print("❌ 需要 Python 3.7 或更新版本")
        return
    
    # 安裝依賴項
    install_dependencies()
    
    # 創建 spec 檔案
    create_spec_file()
    
    # 打包 EXE
    if build_exe():
        # 創建安裝說明
        create_installer_info()
        
        print("\n🎉 打包完成！")
        print("📁 輸出目錄: dist/")
        print("📄 執行檔: PEGA_Log_Analyzer_V1.6.6.exe")
        print("📋 安裝說明: dist/安裝說明.txt")
        
        # 檢查檔案大小
        exe_path = 'dist/PEGA_Log_Analyzer_V1.6.6.exe'
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📊 檔案大小: {size_mb:.1f} MB")
    else:
        print("❌ 打包失敗，請檢查錯誤訊息")

if __name__ == '__main__':
    main() 