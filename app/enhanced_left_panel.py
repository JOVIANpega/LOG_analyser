#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enhanced_left_panel.py
用途：提供增強版左側面板建構，從 main_enhanced.py 抽離。
"""
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *

def _create_tooltip(widget, text):
    """創建 tooltip 功能"""
    def on_enter(event):
        # 確保沒有重複的 tooltip
        if hasattr(widget, 'tooltip'):
            widget.tooltip.destroy()
        
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        
        label = tk.Label(tooltip, text=text, background="lightyellow", 
                        relief="solid", borderwidth=1, font=("Arial", 9),
                        justify="left", wraplength=200)
        label.pack()
        
        widget.tooltip = tooltip
    
    def on_leave(event):
        if hasattr(widget, 'tooltip'):
            widget.tooltip.destroy()
            del widget.tooltip
    
    def on_motion(event):
        # 滑鼠移動時更新位置
        if hasattr(widget, 'tooltip'):
            widget.tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
    
    # 綁定多個事件以確保 tooltip 正常工作
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)
    widget.bind("<Motion>", on_motion)
    
    # 對於按鈕，也綁定 Button-1 事件
    if isinstance(widget, tk.Button):
        widget.bind("<Button-1>", lambda e: on_leave(e))

def build_left_panel(parent, app):
    # 標題 - 使用傳統 tk 視窗以便分析時能正常閃爍
    from ttkbootstrap import Style
    try:
        colors = Style().colors
        header_bg = colors.primary
        header_fg = colors.inversefg if hasattr(colors, 'inversefg') else 'white'
    except:
        header_bg = '#4CAF50'
        header_fg = 'white'

    title_frame = tk.Frame(parent, bg=header_bg, relief=tk.RAISED, bd=2)
    title_frame.pack(fill=tk.X, padx=10, pady=(10, 20))
    
    title_label = tk.Label(title_frame, text=app.settings.get('gui_header', 'PEGA LOG ANALYZER'), 
                          font=('Arial', 24, 'bold'), fg=header_fg, bg=header_bg)
    title_label.pack(pady=15)
    app.font_scaler.register(title_label)
    
    # 讓設定頁面可即時更新此標題
    app.left_title_label = title_label
    app.left_title_frame = title_frame
    
    # 檔案選擇區域
    file_frame = ttk.LabelFrame(parent, text=" 📁 檔案選擇 ", padding=(10, 10))
    file_frame.pack(fill=tk.X, padx=10, pady=5)
    
    # 檔案選擇區域
    file_frame = tk.LabelFrame(parent, text="檔案選擇", padx=10, pady=10)
    file_frame.pack(fill=tk.X, padx=10, pady=5)
    
    # 統一檔案選擇 (多選, 支援 Log/壓縮檔)
    btn_files = tk.Button(file_frame, text="📄 選擇檔案 (Log/壓縮檔)", 
                          command=app._select_files_unified, bg='#4CAF50', fg='white')
    btn_files.pack(fill=tk.X, pady=2)
    app.font_scaler.register(btn_files)
    _create_tooltip(btn_files, "選擇一個或多個檔案\n支援 .log 以及 .zip/.7z/.rar 壓縮檔")
    
    # 統一資料夾選擇 (自動識別)
    btn_folder = tk.Button(file_frame, text="📂 選擇資料夾 (自動識別)", 
                          command=app._select_folder_unified, bg='#2196F3', fg='white')
    btn_folder.pack(fill=tk.X, pady=2)
    app.font_scaler.register(btn_folder)
    _create_tooltip(btn_folder, "選擇資料夾\n自動識別內容為 Log 檔案或壓縮檔\n若混合存在將詢問處理方式")
    
    # 壓縮檔處理按鈕 - 已移除，功能整合至上述按鈕

    
    # CSV檔案整理按鈕
    btn_csv = tk.Button(file_frame, text="📊 CSV檔案整理", 
                       command=app.start_csv_processing, bg='#FF9800', fg='white')
    btn_csv.pack(fill=tk.X, pady=2)
    app.font_scaler.register(btn_csv)
    _create_tooltip(btn_csv, "選擇目錄自動搜尋CSV檔案並整理\n自動調整欄寬，PASS/FAIL顏色標記")
    
    # 清除結果按鈕
    btn_clear = tk.Button(file_frame, text="🗑️ 清除結果", 
                         command=app._clear_enhanced_results, bg='#F44336', fg='white')
    btn_clear.pack(fill=tk.X, pady=2)
    app.font_scaler.register(btn_clear)
    # 添加 tooltip
    _create_tooltip(btn_clear, "清除所有分析結果\n重置介面到初始狀態")
    
    # 不需要額外的 bold 和 hover 處理，因為 ttkbootstrap 已經處理好了
    pass
    
    # 搜尋功能區域
    search_frame = ttk.LabelFrame(parent, text=" 🔍 搜尋功能 ", padding=(10, 10))
    search_frame.pack(fill=tk.X, padx=10, pady=5)
    
    search_label = ttk.Label(search_frame, text="搜尋關鍵字:", font=('Arial', 10))
    search_label.pack(anchor='w')
    app.font_scaler.register(search_label)
    
    app.search_var = tk.StringVar()
    app.search_entry = ttk.Entry(search_frame, textvariable=app.search_var, font=('Arial', 10))
    app.search_entry.pack(fill=tk.X, pady=5)
    app.search_entry.bind('<KeyRelease>', app._on_search_change)
    app.search_entry.bind('<Return>', app._on_search_enter)
    app.font_scaler.register(app.search_entry)
    _create_tooltip(app.search_entry, "輸入要搜尋的關鍵字\n按 Enter 開始搜尋")
    
    search_btn_frame = ttk.Frame(search_frame)
    search_btn_frame.pack(fill=tk.X, pady=2)
    
    search_btn = ttk.Button(search_btn_frame, text="下一個", command=app._search_next, 
                           style='info.Outline.TButton')
    search_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,2))
    app.font_scaler.register(search_btn)
    # 添加 tooltip
    _create_tooltip(search_btn, "搜尋下一個匹配項目\n在當前標籤頁中向下搜尋")
    
    prev_btn = ttk.Button(search_btn_frame, text="上一個", command=app._search_prev, 
                         style='success.Outline.TButton')
    prev_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
    app.font_scaler.register(prev_btn)
    _create_tooltip(prev_btn, "搜尋上一個匹配項目\n在當前標籤頁中向上搜尋")
    
    clear_search_btn = ttk.Button(search_btn_frame, text="清除", command=app._clear_search, 
                                 style='warning.Outline.TButton')
    clear_search_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2,0))
    app.font_scaler.register(clear_search_btn)
    _create_tooltip(clear_search_btn, "清除搜尋結果\n移除所有高亮標記")
    
    # 搜尋結果計數標籤
    app.search_count_label = ttk.Label(search_frame, text="", font=('Arial', 9))
    app.search_count_label.pack(pady=(5, 0))
    app.font_scaler.register(app.search_count_label)
    
    # 說明文件按鈕（HTML操作說明）
    help_btn = ttk.Button(parent, text="📖 查看操作說明(HTML)", command=app._open_html_help, style='secondary.TButton')
    help_btn.pack(fill=tk.X, padx=10, pady=(8, 8))
    app.font_scaler.register(help_btn)
    _create_tooltip(help_btn, "開啟操作說明文件\n查看詳細使用指南")
    
    # 不需要額外的 bold 和 hover 處理
    pass
    
    # 顯示選擇的檔案
    app.file_info_label = ttk.Label(file_frame, text="未選擇檔案", 
                                    wraplength=200, style='secondary.TLabel')
    app.file_info_label.pack(pady=(5, 0))
    app.font_scaler.register(app.file_info_label)
    