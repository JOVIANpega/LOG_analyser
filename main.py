#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試Log分析器GUI應用程式
提供現代化的圖形使用者介面來分析測試log檔案
僅啟動增強版模式
"""

import tkinter as tk
import sys
import os

def main():
    """主程式入口點（僅增強版）"""
    from app.main_app import EnhancedLogAnalyzerApp
    root = tk.Tk()
    app = EnhancedLogAnalyzerApp(root)
    root.mainloop()

if __name__ == '__main__':
    main() 