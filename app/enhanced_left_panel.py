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

def _create_tooltip(widget, text, app=None):
    """創建 tooltip 功能"""
    def on_enter(event):
        # 確保沒有重複的 tooltip
        if hasattr(widget, 'tooltip'):
            widget.tooltip.destroy()
        
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        
        # 根據設定調整字體大小
        font_size = 9
        if app and app.settings:
            font_size = app.settings.get('ui_font_size', 10) - 1 # 稍微比主 UI 小一點點
            if font_size < 9: font_size = 9
            
        label = tk.Label(tooltip, text=text, background="lightyellow", 
                        relief="solid", borderwidth=1, font=("Microsoft JhengHei", font_size),
                        justify="left", wraplength=300)
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
    file_frame = tk.LabelFrame(parent, text=" 📁 檔案來源 ", padx=10, pady=10)
    file_frame.pack(fill=tk.X, padx=10, pady=5)
    
    # 智能選擇按鈕 (整合單檔/多檔/資料夾)
    btn_smart = tk.Button(file_frame, text=" 📂 選擇 LOG 來源 (檔案/資料夾) ▼", 
                          bg='#673AB7', fg='white', font=('Arial', 10, 'bold'),
                          anchor='w', padx=15)
    btn_smart.pack(fill=tk.X, pady=5, ipady=5)
    app.font_scaler.register(btn_smart)
    _create_tooltip(btn_smart, "點擊選擇 LOG 來源\n支援單個/多個檔案、壓縮檔或整個資料夾", app=app)
    
    # 創建下拉選單 (設定字體以連動 UI 大小)
    ui_font_size = app.settings.get('ui_font_size', 10)
    selection_menu = tk.Menu(btn_smart, tearoff=0, font=('Arial', ui_font_size))
    selection_menu.add_command(label="📄 選擇檔案 (Log/壓縮檔)...", command=app._select_files_unified)
    selection_menu.add_command(label="📁 選擇資料夾 (批次處理)...", command=app._select_folder_unified)
    app.selection_menu = selection_menu
    
    # 綁定點擊事件顯示選單
    def show_smart_menu(event):
        selection_menu.post(event.x_root, event.y_root)
        
    btn_smart.bind("<Button-1>", show_smart_menu)
    
    # CSV檔案整理按鈕
    btn_csv = tk.Button(file_frame, text=" 📊 CSV 檔案整理", 
                       command=app.start_csv_processing, bg='#FF9800', fg='white',
                       font=('Arial', 10, 'bold'), anchor='w', padx=15)
    btn_csv.pack(fill=tk.X, pady=2, ipady=3)
    app.font_scaler.register(btn_csv)
    _create_tooltip(btn_csv, "選擇目錄自動搜尋 CSV 檔案並整理\n自動調整欄寬，PASS/FAIL 顏色標記", app=app)
    
    # 清除結果按鈕
    btn_clear = tk.Button(file_frame, text=" 🗑️ 清除結果", 
                         command=app._clear_enhanced_results, bg='#F44336', fg='white',
                         font=('Arial', 10, 'bold'), anchor='w', padx=15)
    btn_clear.pack(fill=tk.X, pady=2, ipady=3)
    app.font_scaler.register(btn_clear)
    _create_tooltip(btn_clear, "清除所有分析結果\n重置介面到初始狀態", app=app)
    
    # 搜尋功能區域
    search_frame = ttk.LabelFrame(parent, text=" 🔍 搜尋功能 ", padding=(10, 10))
    search_frame.pack(fill=tk.X, padx=10, pady=5)
    
    # 搜尋結果計數標籤 (提前到輸入框上方，增加醒目度)
    app.search_count_label = ttk.Label(search_frame, text="準備搜尋...", font=('Arial', 10, 'bold'))
    app.search_count_label.pack(anchor='w', pady=(0, 5))
    app.font_scaler.register(app.search_count_label)
    
    search_label = ttk.Label(search_frame, text="搜尋關鍵字:", font=('Arial', 10))
    search_label.pack(anchor='w')
    app.font_scaler.register(search_label)
    
    app.search_var = tk.StringVar(value="doesn't")
    app.search_entry = ttk.Entry(search_frame, textvariable=app.search_var, font=('Arial', 10))
    app.search_entry.pack(fill=tk.X, pady=5)
    app.search_entry.bind('<KeyRelease>', app._on_search_change)
    app.search_entry.bind('<Return>', app._on_search_enter)
    app.font_scaler.register(app.search_entry)
    _create_tooltip(app.search_entry, "輸入要搜尋的關鍵字\n按 Enter 開始搜尋", app=app)
    
    search_btn_frame = ttk.Frame(search_frame)
    search_btn_frame.pack(fill=tk.X, pady=2)
    
    search_btn = ttk.Button(search_btn_frame, text="下一個", command=app._search_next, 
                           style='info.Outline.TButton')
    search_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,2))
    app.font_scaler.register(search_btn)
    # 添加 tooltip
    _create_tooltip(search_btn, "搜尋下一個匹配項目\n在當前標籤頁中向下搜尋", app=app)
    
    prev_btn = ttk.Button(search_btn_frame, text="上一個", command=app._search_prev, 
                         style='success.Outline.TButton')
    prev_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
    app.font_scaler.register(prev_btn)
    _create_tooltip(prev_btn, "搜尋上一個匹配項目\n在當前標籤頁中向上搜尋", app=app)
    
    clear_search_btn = ttk.Button(search_btn_frame, text="清除", command=app._clear_search, 
                                 style='warning.Outline.TButton')
    clear_search_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2,0))
    app.font_scaler.register(clear_search_btn)
    _create_tooltip(clear_search_btn, "清除搜尋結果\n移除所有高亮標記", app=app)
    
    # 不需要額外的 bold 和 hover 處理
    pass
    
    # 說明文件按鈕 (改用 tk.Button 以確保左對齊)
    help_btn = tk.Button(parent, text=" 📖 查看操作說明 (HTML)", 
                        command=app._open_html_help, bg='#607D8B', fg='white',
                        font=('Arial', 10, 'bold'), anchor='w', padx=15)
    help_btn.pack(fill=tk.X, padx=10, pady=(8, 8), ipady=5)
    app.font_scaler.register(help_btn)
    _create_tooltip(help_btn, "開啟操作說明文件\n查看詳細使用指南", app=app)
    
    # 🚀 跨分頁快捷導覽按鈕區 (User Requested: 放在 HTML 按鈕下方)
    nav_labelframe = ttk.LabelFrame(parent, text=" ⚡ 快捷導覽 (隨當前標籤切換) ", padding=(10, 10))
    nav_labelframe.pack(fill=tk.X, padx=10, pady=5)
    
    nav_btn_frame = ttk.Frame(nav_labelframe)
    nav_btn_frame.pack(fill=tk.X)
    
    # 使用網格佈局 2x2
    # TOP
    btn_top = ttk.Button(nav_btn_frame, text="🔝 TOP (置頂)", 
                        command=app._global_scroll_top, style='info.TButton')
    btn_top.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)
    app.font_scaler.register(btn_top)
    
    # PAGE UP
    btn_pgup = ttk.Button(nav_btn_frame, text="▲ 上一頁", 
                         command=app._global_scroll_pgup, style='secondary.TButton')
    btn_pgup.grid(row=0, column=1, sticky='nsew', padx=2, pady=2)
    app.font_scaler.register(btn_pgup)
    
    # PAGE DOWN
    btn_pgdn = ttk.Button(nav_btn_frame, text="▼ 下一頁", 
                         command=app._global_scroll_pgdn, style='secondary.TButton')
    btn_pgdn.grid(row=1, column=1, sticky='nsew', padx=2, pady=2)
    app.font_scaler.register(btn_pgdn)
    
    # END
    btn_end = ttk.Button(nav_btn_frame, text="🔚 END (最後)", 
                        command=app._global_scroll_bottom, style='info.TButton')
    btn_end.grid(row=1, column=0, sticky='nsew', padx=2, pady=2)
    app.font_scaler.register(btn_end)
    
    nav_btn_frame.columnconfigure(0, weight=1)
    nav_btn_frame.columnconfigure(1, weight=1)
    _create_tooltip(nav_labelframe, "快速捲動目前的內容\n💡 鍵盤快捷鍵：\n• 方向鍵 [↑/↓]：直接翻頁 (Page Up/Down)\n• [Alt + PageUp/Dn]：切換測項章節 (@STEP)", app=app)

    # 顯示選擇的檔案
    app.file_info_label_left = ttk.Label(file_frame, text="未選擇檔案", 
                                        wraplength=200, style='secondary.TLabel')
    app.file_info_label_left.pack(pady=(5, 0))
    app.font_scaler.register(app.file_info_label_left)
    