#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI測試腳本
"""

import tkinter as tk
from tkinter import messagebox
import threading
import time

def test_gui_components():
    """測試GUI元件"""
    print("=== GUI元件測試 ===")
    
    # 建立測試視窗
    root = tk.Tk()
    root.title("GUI測試")
    root.geometry("400x300")
    
    # 測試標籤
    label = tk.Label(root, text="測試標籤", font=("Arial", 12))
    label.pack(pady=20)
    
    # 測試按鈕
    def test_button():
        messagebox.showinfo("測試", "按鈕功能正常!")
    
    button = tk.Button(root, text="測試按鈕", command=test_button)
    button.pack(pady=10)
    
    # 測試進度條
    progress = tk.ttk.Progressbar(root, mode='indeterminate')
    progress.pack(pady=10)
    progress.start()
    
    # 測試文字區域
    text_area = tk.Text(root, height=5, width=40)
    text_area.pack(pady=10)
    text_area.insert(tk.END, "這是測試文字區域\nGUI元件測試正常!")
    
    # 自動關閉
    def close_window():
        root.destroy()
    
    root.after(3000, close_window)  # 3秒後自動關閉
    
    print("✅ GUI元件測試完成")
    root.mainloop()

if __name__ == "__main__":
    test_gui_components() 