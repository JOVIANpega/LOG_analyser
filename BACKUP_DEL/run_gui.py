#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試Log分析器 - 啟動腳本
簡單的GUI啟動器，用於測試和演示
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

def check_dependencies():
    """檢查必要的依賴套件"""
    try:
        import pandas
        import openpyxl
        return True
    except ImportError as e:
        messagebox.showerror("缺少依賴套件", 
                           f"請先安裝必要套件：\npip install pandas openpyxl\n\n錯誤：{e}")
        return False

def main():
    """主啟動函數"""
    print("=== 測試Log分析器 ===")
    print("正在檢查依賴套件...")
    
    if not check_dependencies():
        return
    
    print("依賴套件檢查完成")
    print("正在啟動GUI...")
    
    try:
        # 導入主程式
        from main import LogAnalyzerApp
        
        # 創建主視窗
        root = tk.Tk()
        root.geometry("1200x800")
        
        # 創建應用程式
        app = LogAnalyzerApp(root)
        
        print("GUI已啟動，請在視窗中操作")
        print("使用說明：")
        print("1. 點擊左側「選擇檔案」或「選擇資料夾」")
        print("2. 點擊「開始分析」按鈕")
        print("3. 在右側Tab中查看結果")
        print("4. 使用+/-按鈕調整字體大小")
        print("5. 多檔模式可匯出Excel報告")
        
        # 啟動GUI主迴圈
        root.mainloop()
        
    except Exception as e:
        print(f"啟動失敗：{e}")
        import traceback
        traceback.print_exc()
        messagebox.showerror("啟動錯誤", f"GUI啟動失敗：\n{str(e)}")

if __name__ == "__main__":
    main()