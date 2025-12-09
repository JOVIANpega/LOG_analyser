#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試Log分析器GUI應用程式 - 增強版
向後相容入口點
"""

import tkinter as tk

def main_enhanced():
    """主程式入口點（增強版）"""
    from app.main_app import EnhancedLogAnalyzerApp
    root = tk.Tk()
    app = EnhancedLogAnalyzerApp(root)
    root.mainloop()

if __name__ == '__main__':
    main_enhanced()