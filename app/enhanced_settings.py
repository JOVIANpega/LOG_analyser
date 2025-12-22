#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enhanced_settings.py
用途：提供增強版設定頁面內容建構函式，從 main_enhanced.py 抽離以降低主檔案行數。
"""
import tkinter as tk
from tkinter import ttk

def build_settings_content(app, parent):
    """建立設定內容（從 app._build_settings_content 抽出）"""
    # 將 parent 設定為 app.settings_frame，以便字體更新函式能找到它
    app.settings_frame = parent
    
    # 標題
    title_label = tk.Label(parent, text="應用程式設定", 
                          font=('Arial', 16, 'bold'), fg='#2E86AB')
    title_label._is_settings_title = True  # 標識為設定頁面標題
    title_label.pack(pady=(0, 20))
    
    # 建立左右兩欄佈局
    columns_frame = tk.Frame(parent)
    columns_frame.pack(fill=tk.BOTH, expand=True, padx=15)
    
    # 左欄
    left_column = tk.Frame(columns_frame)
    left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
    
    # 右欄
    right_column = tk.Frame(columns_frame)
    right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
    
    # ===== 左欄內容 =====
    
    # 字體設定區域
    font_frame = tk.LabelFrame(left_column, text="字體設定", padx=15, pady=15)
    font_frame.pack(fill=tk.X, pady=5)
    
    # 介面字體大小設定
    ui_font_frame = tk.Frame(font_frame)
    ui_font_frame.pack(fill=tk.X, pady=8)
    
    ui_font_label = tk.Label(ui_font_frame, text="介面文字大小：", font=('Arial', 11))
    ui_font_label._is_settings_label = True  # 標識為設定標籤
    ui_font_label.pack(side=tk.LEFT)
    app.font_scaler.register(ui_font_label)  # 註冊字體縮放
    
    btn_ui_minus = tk.Button(ui_font_frame, text="－", width=3, 
                            command=app._decrease_ui_font)
    btn_ui_minus._is_settings_button = True  # 標識為設定按鈕
    btn_ui_minus.pack(side=tk.LEFT, padx=3)
    app.font_scaler.register(btn_ui_minus)  # 註冊字體縮放
    
    app.settings_ui_font_size_label = tk.Label(ui_font_frame, text=str(app.ui_font_size), 
                                     width=3, relief=tk.SUNKEN, font=('Arial', 11))
    app.settings_ui_font_size_label._is_settings_label = True  # 標識為設定標籤
    app.settings_ui_font_size_label.pack(side=tk.LEFT, padx=3)
    app.font_scaler.register(app.settings_ui_font_size_label)  # 註冊字體縮放
    
    btn_ui_plus = tk.Button(ui_font_frame, text="＋", width=3, 
                           command=app._increase_ui_font)
    btn_ui_plus._is_settings_button = True  # 標識為設定按鈕
    btn_ui_plus.pack(side=tk.LEFT, padx=3)
    app.font_scaler.register(btn_ui_plus)  # 註冊字體縮放
    
    # 內容字體大小設定
    content_font_frame = tk.Frame(font_frame)
    content_font_frame.pack(fill=tk.X, pady=8)
    
    content_font_label = tk.Label(content_font_frame, text="內容字體大小：", font=('Arial', 11))
    content_font_label._is_settings_label = True  # 標識為設定標籤
    content_font_label.pack(side=tk.LEFT)
    app.font_scaler.register(content_font_label)  # 註冊字體縮放
    
    btn_content_minus = tk.Button(content_font_frame, text="－", width=3, 
                                command=app._decrease_content_font)
    btn_content_minus._is_settings_button = True  # 標識為設定按鈕
    btn_content_minus.pack(side=tk.LEFT, padx=3)
    app.font_scaler.register(btn_content_minus)  # 註冊字體縮放
    
    app.settings_content_font_size_label = tk.Label(content_font_frame, text=str(app.content_font_size), 
                                          width=3, relief=tk.SUNKEN, font=('Arial', 11))
    app.settings_content_font_size_label._is_settings_label = True  # 標識為設定標籤
    app.settings_content_font_size_label.pack(side=tk.LEFT, padx=3)
    app.font_scaler.register(app.settings_content_font_size_label)  # 註冊字體縮放
    
    btn_content_plus = tk.Button(content_font_frame, text="＋", width=3, 
                                 command=app._increase_content_font)
    btn_content_plus._is_settings_button = True  # 標識為設定按鈕
    btn_content_plus.pack(side=tk.LEFT, padx=3)
    app.font_scaler.register(btn_content_plus)  # 註冊字體縮放
    
    # ===== 右欄內容 =====
    
    # 其他設定區域
    other_frame = tk.LabelFrame(right_column, text="其他設定", padx=15, pady=15)
    other_frame.pack(fill=tk.X, pady=5)
    app.font_scaler.register(other_frame)
    
    # 自動分析設定
    app.auto_analyze_var = tk.BooleanVar(value=app.settings.get('auto_analyze', True))
    auto_analyze_check = tk.Checkbutton(other_frame, text="選擇檔案後自動開始分析", 
                                       variable=app.auto_analyze_var, 
                                       font=('Arial', 11))
    auto_analyze_check._is_settings_checkbutton = True  # 標識為設定核取方塊
    auto_analyze_check.pack(anchor=tk.W, pady=3)
    app.font_scaler.register(auto_analyze_check)
    
    # 路徑記憶設定
    app.remember_path_var = tk.BooleanVar(value=app.settings.get('remember_path', True))
    remember_path_check = tk.Checkbutton(other_frame, text="記住上次選擇的路徑", 
                                        variable=app.remember_path_var, 
                                        font=('Arial', 11))
    remember_path_check._is_settings_checkbutton = True  # 標識為設定核取方塊
    remember_path_check.pack(anchor=tk.W, pady=3)
    app.font_scaler.register(remember_path_check)
    
    # 忽略無測試時間的LOG
    app.skip_no_test_time_var = tk.BooleanVar(value=app.settings.get('skip_no_test_time', True))
    skip_no_test_time_check = tk.Checkbutton(other_frame, text="忽略未找到測試總時間的LOG", 
                                            variable=app.skip_no_test_time_var, 
                                            font=('Arial', 11))
    skip_no_test_time_check._is_settings_checkbutton = True  # 標識為設定核取方塊
    skip_no_test_time_check.pack(anchor=tk.W, pady=3)
    app.font_scaler.register(skip_no_test_time_check)
    
    # 主題設定區域
    theme_frame = tk.LabelFrame(right_column, text="介面主題", padx=15, pady=15)
    theme_frame.pack(fill=tk.X, pady=5)
    app.font_scaler.register(theme_frame)
    
    theme_edit_frame = tk.Frame(theme_frame)
    theme_edit_frame.pack(fill=tk.X, pady=8)
    
    theme_label = tk.Label(theme_edit_frame, text="主題名稱：", font=('Arial', 11))
    theme_label._is_settings_label = True
    theme_label.pack(side=tk.LEFT)
    app.font_scaler.register(theme_label)
    
    # 支援的主題清單
    themes = ['superhero', 'darkly', 'cosmo', 'flatly', 'journal', 'litera', 'lumen', 'minty', 'pulse', 'sandstone', 'united', 'yeti', 'morph', 'simplex', 'cerculean']
    app.theme_var = tk.StringVar(value=app.settings.get('theme', 'superhero'))
    
    # 使用 ttk.Combobox
    theme_combo = ttk.Combobox(theme_edit_frame, textvariable=app.theme_var, values=themes, state='readonly', width=15)
    theme_combo.pack(side=tk.LEFT, padx=8)
    # 綁定即時切換事件
    theme_combo.bind('<<ComboboxSelected>>', app._on_theme_change)
    
    # 版本設定區域
    version_frame = tk.LabelFrame(right_column, text="版本設定", padx=15, pady=15)
    version_frame.pack(fill=tk.X, pady=5)
    app.font_scaler.register(version_frame)
    
    # 版本號碼設定
    version_edit_frame = tk.Frame(version_frame)
    version_edit_frame.pack(fill=tk.X, pady=8)
    
    version_label = tk.Label(version_edit_frame, text="版本號碼：", font=('Arial', 11))
    version_label._is_settings_label = True  # 標識為設定標籤
    version_label.pack(side=tk.LEFT)
    app.font_scaler.register(version_label)
    
    app.version_var = tk.StringVar(value=app.settings.get('version', 'V1.5.6'))
    version_entry = tk.Entry(version_edit_frame, textvariable=app.version_var, width=20)
    version_entry._is_settings_entry = True  # 標識為設定輸入框
    version_entry.pack(side=tk.LEFT, padx=8)
    app.font_scaler.register(version_entry)
    
    # 版本說明
    version_info_label = tk.Label(version_frame, text="版本號碼會顯示在應用程式標題和設定頁面中", 
                                 fg='#666', font=('Arial', 9))
    version_info_label._is_info_label = True  # 標識為說明文字
    version_info_label.pack(pady=(8, 0))
    app.font_scaler.register(version_info_label)
    
    # ===== 底部按鈕區域 =====
    
    # 分隔線
    separator = ttk.Separator(parent, orient='horizontal')
    separator.pack(fill=tk.X, padx=15, pady=15)
    
    # 按鈕區域
    button_frame = tk.Frame(parent)
    button_frame.pack(fill=tk.X, padx=15, pady=15)
    
    # 統一的儲存設定按鈕
    save_btn = tk.Button(button_frame, text="儲存所有設定", 
                        command=app._save_settings,
                        bg='#4CAF50', fg='white', font=('Arial', 12, 'bold'),
                        width=15, height=2)
    save_btn._is_settings_button = True  # 標識為設定按鈕
    save_btn.pack(side=tk.RIGHT, padx=5)
    
    # 說明文字
    save_info_label = tk.Label(button_frame, text="點擊儲存按鈕後，所有設定將立即生效", 
                              fg='#666', font=('Arial', 9))
    save_info_label._is_info_label = True  # 標識為說明文字
    save_info_label.pack(side=tk.LEFT, pady=10) 