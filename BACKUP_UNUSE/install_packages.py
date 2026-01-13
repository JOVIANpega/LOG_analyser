#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安裝必要的Python套件
"""

import subprocess
import sys

def install_package(package_name):
    """安裝Python套件"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ {package_name} 安裝成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package_name} 安裝失敗: {e}")
        return False

def main():
    """主函數"""
    print("=== PEGA Log Analyzer 套件安裝工具 ===\n")
    
    packages = [
        "py7zr",      # 7Z檔案支援
        "rarfile",    # RAR檔案支援
        "openpyxl",   # Excel檔案支援
        "pandas"      # CSV檔案支援
    ]
    
    print("將安裝以下套件:")
    for pkg in packages:
        print(f"  - {pkg}")
    
    print("\n開始安裝...")
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n安裝完成！成功安裝 {success_count}/{len(packages)} 個套件")
    
    if success_count == len(packages):
        print("🎉 所有套件安裝成功！現在可以完整使用所有功能。")
    else:
        print("⚠️  部分套件安裝失敗，某些功能可能無法使用。")

if __name__ == "__main__":
    main()
