#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXE 相容性問題解決腳本
解決 PEGA_Log_Analyzer_V1.6.6.exe 在其他 PC 無法開啟的問題
"""

import os
import sys
import subprocess
import platform

def check_system_compatibility():
    """檢查系統相容性"""
    print("🔍 檢查系統相容性...")
    
    # 檢查 Python 版本
    python_version = sys.version_info
    print(f"🐍 Python 版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 檢查作業系統
    os_name = platform.system()
    os_version = platform.version()
    print(f"💻 作業系統: {os_name} {os_version}")
    
    # 檢查架構
    arch = platform.architecture()[0]
    print(f"🏗️ 系統架構: {arch}")
    
    # 檢查是否為 Windows
    if os_name != 'Windows':
        print("❌ 此腳本僅支援 Windows 系統")
        return False
    
    print("✅ 系統相容性檢查通過")
    return True

def install_required_packages():
    """安裝必要的套件"""
    print("\n📦 安裝必要套件...")
    
    packages = [
        'pyinstaller>=5.0.0',
        'pandas>=1.5.0',
        'openpyxl>=3.0.0',
        'xlrd>=2.0.0',
    ]
    
    for package in packages:
        try:
            print(f"正在安裝 {package}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                         check=True, capture_output=True)
            print(f"✅ {package} 安裝成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ {package} 安裝失敗: {e}")
            return False
    
    return True

def create_optimized_spec():
    """創建優化的 PyInstaller spec 檔案"""
    print("\n📝 創建優化的 spec 檔案...")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
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
        'settings_loader',
        'log_parser',
        'ui_components',
        'ui_enhanced_fixed',
        'enhanced_settings',
        'enhanced_left_panel',
        'excel_writer',
        'generate_documentation',
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
        'IPython',
        'jupyter',
        'notebook',
        'spyder',
        'pytest',
        'unittest',
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
    name='PEGA_Log_Analyzer_V1.6.6_Compatible',
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
    icon=None,
    version_file=None,
    uac_admin=False,
    uac_uiaccess=False,
)
'''
    
    with open('PEGA_Log_Analyzer_V1.6.6_Compatible.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 已創建優化的 spec 檔案")

def build_compatible_exe():
    """打包相容性 EXE"""
    print("\n🔨 開始打包相容性 EXE...")
    
    # 清理舊檔案
    if os.path.exists('dist'):
        import shutil
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # 使用 spec 檔案打包
    try:
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            'PEGA_Log_Analyzer_V1.6.6_Compatible.spec'
        ]
        
        print("執行命令:", ' '.join(cmd))
        subprocess.run(cmd, check=True)
        
        print("✅ 相容性 EXE 打包完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失敗: {e}")
        return False

def create_deployment_package():
    """創建部署套件"""
    print("\n📦 創建部署套件...")
    
    # 創建部署說明
    deployment_guide = '''PEGA Log Analyzer V1.6.6 部署套件
==========================================

🎯 系統需求：
- Windows 7 SP1 或更新版本
- 64位元作業系統
- 至少 2GB RAM
- 100MB 可用磁碟空間

📋 必要元件（目標電腦需要安裝）：
1. Microsoft Visual C++ 2015-2022 Redistributable
   下載連結: https://aka.ms/vs/17/release/vc_redist.x64.exe

2. .NET Framework 4.7.2 或更新版本
   下載連結: https://dotnet.microsoft.com/download/dotnet-framework

🔧 部署步驟：
1. 在目標電腦安裝必要元件
2. 將 PEGA_Log_Analyzer_V1.6.6_Compatible.exe 複製到目標電腦
3. 雙擊執行，首次執行可能需要較長時間
4. 如果出現錯誤，檢查 Windows 事件檢視器

❌ 常見問題解決：
Q: 程式無法啟動或閃退
A: 安裝 Visual C++ 2015-2022 Redistributable

Q: 缺少 DLL 檔案錯誤
A: 安裝 .NET Framework 4.7.2+

Q: 權限不足錯誤
A: 以系統管理員身份執行

Q: 防毒軟體阻擋
A: 將程式加入防毒軟體白名單

📞 技術支援：
1. 檢查 Windows 事件檢視器 > Windows 記錄 > 應用程式
2. 查看錯誤訊息和事件 ID
3. 確認系統已安裝所有必要元件

版本: V1.6.6
打包日期: {date}
'''
    
    from datetime import datetime
    deployment_guide = deployment_guide.format(date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    with open('dist/部署說明.txt', 'w', encoding='utf-8') as f:
        f.write(deployment_guide)
    
    # 創建快速安裝腳本
    install_script = '''@echo off
echo 正在安裝 PEGA Log Analyzer V1.6.6 必要元件...
echo.

echo 1. 檢查系統相容性...
systeminfo | findstr /i "OS Name"
systeminfo | findstr /i "OS Version"
systeminfo | findstr /i "System Type"
echo.

echo 2. 建議安裝以下元件：
echo    - Microsoft Visual C++ 2015-2022 Redistributable
echo    - .NET Framework 4.7.2 或更新版本
echo.

echo 3. 下載連結：
echo    Visual C++: https://aka.ms/vs/17/release/vc_redist.x64.exe
echo    .NET Framework: https://dotnet.microsoft.com/download/dotnet-framework
echo.

echo 4. 安裝完成後，雙擊 PEGA_Log_Analyzer_V1.6.6_Compatible.exe 執行
echo.

pause
'''
    
    with open('dist/快速安裝.bat', 'w', encoding='utf-8') as f:
        f.write(install_script)
    
    print("✅ 已創建部署套件")
    print("   - 部署說明.txt")
    print("   - 快速安裝.bat")

def main():
    """主函數"""
    print("🚀 PEGA Log Analyzer V1.6.6 相容性問題解決工具")
    print("=" * 60)
    
    # 檢查系統相容性
    if not check_system_compatibility():
        return
    
    # 安裝必要套件
    if not install_required_packages():
        print("❌ 套件安裝失敗，無法繼續")
        return
    
    # 創建優化 spec 檔案
    create_optimized_spec()
    
    # 打包相容性 EXE
    if build_compatible_exe():
        # 創建部署套件
        create_deployment_package()
        
        print("\n🎉 相容性問題解決完成！")
        print("📁 輸出目錄: dist/")
        print("📄 執行檔: PEGA_Log_Analyzer_V1.6.6_Compatible.exe")
        print("📋 部署說明: dist/部署說明.txt")
        print("🔧 快速安裝: dist/快速安裝.bat")
        
        # 檢查檔案大小
        exe_path = 'dist/PEGA_Log_Analyzer_V1.6.6_Compatible.exe'
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📊 檔案大小: {size_mb:.1f} MB")
            
        print("\n💡 建議：")
        print("1. 將整個 dist 資料夾複製到目標電腦")
        print("2. 在目標電腦執行 快速安裝.bat")
        print("3. 安裝必要元件後再執行主程式")
        
    else:
        print("❌ 打包失敗，請檢查錯誤訊息")

if __name__ == '__main__':
    main() 