#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LOG 錯誤分析工具 - 主程式入口
用於分析4cam測試LOG，快速定位錯誤並提供維修建議

Author: PEGA
Date: 2025-11-25
"""

import tkinter as tk
from log_analyzer_gui import LogAnalyzerGUI

def main():
    """主程式入口"""
    # 創建主視窗
    root = tk.Tk()
    
    # 設定視窗圖示（如果有的話）
    # root.iconbitmap('icon.ico')
    
    # 創建應用程式
    app = LogAnalyzerGUI(root)
    
    # 啟動主循環
    root.mainloop()

if __name__ == "__main__":
    main()
