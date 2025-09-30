#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enhanced_left_panel.py
用途：提供增強版左側面板建構，從 main_enhanced.py 抽離。
"""
import tkinter as tk

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
    # 標題 - 使用綠色背景
    title_frame = tk.Frame(parent, bg='#4CAF50', relief=tk.RAISED, bd=2)
    title_frame.pack(fill=tk.X, padx=10, pady=(10, 20))
    
    title_label = tk.Label(title_frame, text=app.settings.get('gui_header', 'PEGA LOG ANALYZER'), 
                          font=('Arial', 24, 'bold'), fg='white', bg='#4CAF50')
    title_label.pack(pady=10)
    app.font_scaler.register(title_label)
    # 讓設定頁面可即時更新此標題
    app.left_title_label = title_label
    
    # 檔案選擇區域
    file_frame = tk.LabelFrame(parent, text="檔案選擇", padx=10, pady=10)
    file_frame.pack(fill=tk.X, padx=10, pady=5)
    
    # 單一檔案選擇
    btn_single = tk.Button(file_frame, text="📁 選擇單一檔案", 
                          command=app._select_file, bg='#4CAF50', fg='white')
    btn_single.pack(fill=tk.X, pady=2)
    app.font_scaler.register(btn_single)
    # 添加 tooltip
    _create_tooltip(btn_single, "選擇單一 LOG 檔案進行分析\n支援 .log 格式")
    
    # 資料夾選擇
    btn_folder = tk.Button(file_frame, text="📂 選擇資料夾", 
                          command=app._select_folder, bg='#2196F3', fg='white')
    btn_folder.pack(fill=tk.X, pady=2)
    app.font_scaler.register(btn_folder)
    # 添加 tooltip
    _create_tooltip(btn_folder, "選擇包含多個 LOG 檔案的資料夾\n自動分析所有 .log 檔案")
    
    # 壓縮檔選擇
    btn_compressed = tk.Button(file_frame, text="📦 讀取壓縮檔LOG", 
                              command=app._select_compressed_file, bg='#FF9800', fg='white')
    btn_compressed.pack(fill=tk.X, pady=2)
    app.font_scaler.register(btn_compressed)
    # 添加 tooltip
    _create_tooltip(btn_compressed, "讀取壓縮檔中的 LOG 檔案\n支援 .zip, .7z, .rar 格式")

    # 壓縮資料夾選擇（批次遞迴展開）
    btn_compressed_folder = tk.Button(file_frame, text="🗃️ 讀取多個壓縮檔", 
                                     command=app._select_compressed_folder, bg='#FB8C00', fg='white')
    btn_compressed_folder.pack(fill=tk.X, pady=2)
    app.font_scaler.register(btn_compressed_folder)
    _create_tooltip(btn_compressed_folder, "選擇含多個壓縮檔的資料夾\n可勾選要處理的壓縮檔，支援多層嵌套")
    
    # 清除結果按鈕
    btn_clear = tk.Button(file_frame, text="🗑️ 清除結果", 
                         command=app._clear_enhanced_results, bg='#F44336', fg='white')
    btn_clear.pack(fill=tk.X, pady=2)
    app.font_scaler.register(btn_clear)
    # 添加 tooltip
    _create_tooltip(btn_clear, "清除所有分析結果\n重置介面到初始狀態")
    
    # 左四個按鈕：加粗與hover
    try:
        from ui_components import make_bold, apply_button_hover
        make_bold(btn_single)
        make_bold(btn_folder)
        make_bold(btn_compressed)
        make_bold(btn_clear)
        apply_button_hover(btn_single, hover_bg="#66BB6A", hover_fg='white', normal_bg='#4CAF50', normal_fg='white')
        apply_button_hover(btn_folder, hover_bg="#64B5F6", hover_fg='white', normal_bg='#2196F3', normal_fg='white')
        apply_button_hover(btn_compressed, hover_bg="#FFB74D", hover_fg='white', normal_bg='#FF9800', normal_fg='white')
        apply_button_hover(btn_compressed_folder, hover_bg="#FFB74D", hover_fg='white', normal_bg='#FB8C00', normal_fg='white')
        apply_button_hover(btn_clear,  hover_bg="#EF5350", hover_fg='white', normal_bg='#F44336', normal_fg='white')
        
        # 重新添加 tooltip（因為 hover 效果可能覆蓋了事件綁定）
        _create_tooltip(btn_single, "選擇單一 LOG 檔案進行分析\n支援 .log 格式")
        _create_tooltip(btn_folder, "選擇包含多個 LOG 檔案的資料夾\n自動分析所有 .log 檔案")
        _create_tooltip(btn_compressed, "讀取壓縮檔中的 LOG 檔案\n支援 .zip, .7z, .rar 格式")
        _create_tooltip(btn_compressed_folder, "選擇含多個壓縮檔的資料夾\n自動遞迴展開內嵌壓縮並分析 .log")
        _create_tooltip(btn_clear, "清除所有分析結果\n重置介面到初始狀態")
    except Exception:
        pass
    
    # 搜尋功能區域
    search_frame = tk.LabelFrame(parent, text="🔍 搜尋功能", padx=10, pady=10)
    search_frame.pack(fill=tk.X, padx=10, pady=5)
    
    search_label = tk.Label(search_frame, text="搜尋關鍵字:", font=('Arial', 10))
    search_label.pack(anchor='w')
    app.font_scaler.register(search_label)
    
    app.search_var = tk.StringVar()
    app.search_entry = tk.Entry(search_frame, textvariable=app.search_var, width=25, font=('Arial', 10))
    app.search_entry.pack(fill=tk.X, pady=2)
    app.search_entry.bind('<KeyRelease>', app._on_search_change)
    app.search_entry.bind('<Return>', app._on_search_enter)
    app.font_scaler.register(app.search_entry)
    # 添加 tooltip
    _create_tooltip(app.search_entry, "輸入要搜尋的關鍵字\n按 Enter 開始搜尋")
    
    search_btn_frame = tk.Frame(search_frame)
    search_btn_frame.pack(fill=tk.X, pady=2)
    
    search_btn = tk.Button(search_btn_frame, text="下一個", command=app._search_next, 
                          bg='#2196F3', fg='white', font=('Arial', 9))
    search_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,2))
    app.font_scaler.register(search_btn)
    # 添加 tooltip
    _create_tooltip(search_btn, "搜尋下一個匹配項目\n在當前標籤頁中向下搜尋")
    
    prev_btn = tk.Button(search_btn_frame, text="上一個", command=app._search_prev, 
                        bg='#4CAF50', fg='white', font=('Arial', 9))
    prev_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2,2))
    app.font_scaler.register(prev_btn)
    # 添加 tooltip
    _create_tooltip(prev_btn, "搜尋上一個匹配項目\n在當前標籤頁中向上搜尋")
    
    clear_search_btn = tk.Button(search_btn_frame, text="清除", command=app._clear_search, 
                                bg='#FF9800', fg='white', font=('Arial', 9))
    clear_search_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2,0))
    app.font_scaler.register(clear_search_btn)
    # 添加 tooltip
    _create_tooltip(clear_search_btn, "清除搜尋結果\n移除所有高亮標記")
    
    # 搜尋結果計數標籤
    app.search_count_label = tk.Label(search_frame, text="", font=('Arial', 9), fg='#666')
    app.search_count_label.pack(pady=(5, 0))
    app.font_scaler.register(app.search_count_label)
    
    # 說明文件按鈕（HTML操作說明）
    help_btn = tk.Button(parent, text="📖 查看操作說明(HTML)", command=app._open_html_help, bg="#607D8B", fg="white")
    help_btn.pack(fill=tk.X, padx=10, pady=(8, 8))
    app.font_scaler.register(help_btn)
    # 添加 tooltip
    _create_tooltip(help_btn, "開啟操作說明文件\n查看詳細使用指南")
    try:
        make_bold(help_btn)
        apply_button_hover(help_btn, hover_bg="#78909C", hover_fg='white', normal_bg='#607D8B', normal_fg='white')
        # 重新添加 tooltip
        _create_tooltip(help_btn, "開啟操作說明文件\n查看詳細使用指南")
    except Exception:
        pass
    
    # 顯示選擇的檔案
    app.file_info_label = tk.Label(file_frame, text="未選擇檔案", 
                                   fg='#666', wraplength=200)
    app.file_info_label.pack(pady=(5, 0))
    app.font_scaler.register(app.file_info_label)
    