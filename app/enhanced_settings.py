#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enhanced_settings.py
用途：提供增強版設定頁面內容建構函式，從 main_enhanced.py 抽離以降低主檔案行數。
"""
import tkinter as tk
import ttkbootstrap as ttk

def build_settings_content(app, parent):
    """建立設定內容（從 app._build_settings_content 抽出）"""
    # 將 parent 設定為 app.settings_frame，以便字體更新函式能找到它
    app.settings_frame = parent
    
    # 標題
    title_label = ttk.Label(parent, text="應用程式設定", 
                           font=('Arial', 16, 'bold'), bootstyle="primary")
    title_label._is_settings_title = True  # 標識為設定頁面標題
    title_label.pack(pady=(0, 20))
    
    # 建立左右兩欄佈局
    columns_frame = ttk.Frame(parent)
    columns_frame.pack(fill=tk.BOTH, expand=True, padx=15)
    
    # 左欄
    left_column = ttk.Frame(columns_frame)
    left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
    
    # 右欄
    right_column = ttk.Frame(columns_frame)
    right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
    
    # ===== 左欄內容 =====
    
    # 字體設定區域
    font_frame = ttk.LabelFrame(left_column, text="字體設定", padding=(15, 15))
    font_frame.pack(fill=tk.X, pady=5)
    
    # 介面字體大小設定
    ui_font_frame = ttk.Frame(font_frame)
    ui_font_frame.pack(fill=tk.X, pady=8)
    
    ui_font_label = ttk.Label(ui_font_frame, text="介面文字大小：", font=('Arial', 11))
    ui_font_label._is_settings_label = True  # 標識為設定標籤
    ui_font_label.pack(side=tk.LEFT)
    app.font_scaler.register(ui_font_label)  # 註冊字體縮放
    
    btn_ui_minus = ttk.Button(ui_font_frame, text="－", width=3, 
                             command=app._decrease_ui_font, bootstyle="secondary-outline")
    btn_ui_minus._is_settings_button = True  # 標識為設定按鈕
    btn_ui_minus.pack(side=tk.LEFT, padx=3)
    app.font_scaler.register(btn_ui_minus)  # 註冊字體縮放
    
    app.settings_ui_font_size_label = ttk.Label(ui_font_frame, text=str(app.ui_font_size), 
                                     width=3, relief=tk.SUNKEN, font=('Arial', 11), anchor="center")
    app.settings_ui_font_size_label._is_settings_label = True  # 標識為設定標籤
    app.settings_ui_font_size_label.pack(side=tk.LEFT, padx=3)
    app.font_scaler.register(app.settings_ui_font_size_label)  # 註冊字體縮放
    
    btn_ui_plus = ttk.Button(ui_font_frame, text="＋", width=3, 
                            command=app._increase_ui_font, bootstyle="secondary-outline")
    btn_ui_plus._is_settings_button = True  # 標識為設定按鈕
    btn_ui_plus.pack(side=tk.LEFT, padx=3)
    app.font_scaler.register(btn_ui_plus)  # 註冊字體縮放
    
    # 內容字體大小設定
    content_font_frame = ttk.Frame(font_frame)
    content_font_frame.pack(fill=tk.X, pady=8)
    
    content_font_label = ttk.Label(content_font_frame, text="內容字體大小：", font=('Arial', 11))
    content_font_label._is_settings_label = True  # 標識為設定標籤
    content_font_label.pack(side=tk.LEFT)
    app.font_scaler.register(content_font_label)  # 註冊字體縮放
    
    btn_content_minus = ttk.Button(content_font_frame, text="－", width=3, 
                                 command=app._decrease_content_font, bootstyle="secondary-outline")
    btn_content_minus._is_settings_button = True  # 標識為設定按鈕
    btn_content_minus.pack(side=tk.LEFT, padx=3)
    app.font_scaler.register(btn_content_minus)  # 註冊字體縮放
    
    app.settings_content_font_size_label = ttk.Label(content_font_frame, text=str(app.content_font_size), 
                                           width=3, relief=tk.SUNKEN, font=('Arial', 11), anchor="center")
    app.settings_content_font_size_label._is_settings_label = True  # 標識為設定標籤
    app.settings_content_font_size_label.pack(side=tk.LEFT, padx=3)
    app.font_scaler.register(app.settings_content_font_size_label)  # 註冊字體縮放
    
    btn_content_plus = ttk.Button(content_font_frame, text="＋", width=3, 
                                  command=app._increase_content_font, bootstyle="secondary-outline")
    btn_content_plus._is_settings_button = True  # 標識為設定按鈕
    btn_content_plus.pack(side=tk.LEFT, padx=3)
    app.font_scaler.register(btn_content_plus)  # 註冊字體縮放
    
    # ===== 右欄內容 =====
    
    # 其他設定區域
    other_frame = ttk.LabelFrame(right_column, text="其他設定", padding=(15, 15))
    other_frame.pack(fill=tk.X, pady=5)
    app.font_scaler.register(other_frame)
    
    # 自動分析設定
    app.auto_analyze_var = tk.BooleanVar(value=app.settings.get('auto_analyze', True))
    auto_analyze_check = ttk.Checkbutton(other_frame, text="選擇檔案後自動開始分析", 
                                       variable=app.auto_analyze_var, 
                                       bootstyle="round-toggle")
    auto_analyze_check._is_settings_checkbutton = True  # 標識為設定核取方塊
    auto_analyze_check.pack(anchor=tk.W, pady=3)
    app.font_scaler.register(auto_analyze_check)
    
    # 路徑記憶設定
    app.remember_path_var = tk.BooleanVar(value=app.settings.get('remember_path', True))
    remember_path_check = ttk.Checkbutton(other_frame, text="記住上次選擇的路徑", 
                                         variable=app.remember_path_var, 
                                         bootstyle="round-toggle")
    remember_path_check._is_settings_checkbutton = True  # 標識為設定核取方塊
    remember_path_check.pack(anchor=tk.W, pady=3)
    app.font_scaler.register(remember_path_check)
    
    # 忽略無測試時間的LOG
    app.skip_no_test_time_var = tk.BooleanVar(value=app.settings.get('skip_no_test_time', True))
    skip_no_test_time_check = ttk.Checkbutton(other_frame, text="忽略未找到測試總時間的LOG", 
                                             variable=app.skip_no_test_time_var, 
                                             bootstyle="round-toggle")
    skip_no_test_time_check._is_settings_checkbutton = True  # 標識為設定核取方塊
    skip_no_test_time_check.pack(anchor=tk.W, pady=3)
    app.font_scaler.register(skip_no_test_time_check)

    # 顯示懸停預覽彈窗
    app.show_hover_preview_var = tk.BooleanVar(value=app.settings.get('show_hover_preview', False))
    hover_preview_check = ttk.Checkbutton(other_frame, text="顯示懸停預覽彈窗 (預設關閉)", 
                                        variable=app.show_hover_preview_var, 
                                        bootstyle="round-toggle")
    hover_preview_check._is_settings_checkbutton = True
    hover_preview_check.pack(anchor=tk.W, pady=3)
    app.font_scaler.register(hover_preview_check)
    
    # ISN 識別前綴設定
    isn_prefix_frame = ttk.Frame(other_frame)
    isn_prefix_frame.pack(fill=tk.X, pady=8)
    
    isn_prefix_label = ttk.Label(isn_prefix_frame, text="ISN 識別前綴：", font=('Arial', 10))
    isn_prefix_label._is_settings_label = True
    isn_prefix_label.pack(side=tk.LEFT)
    app.font_scaler.register(isn_prefix_label)
    
    app.isn_prefix_var = tk.StringVar(value=app.settings.get('image_search_isn_prefix', 'WE'))
    isn_prefix_entry = ttk.Entry(isn_prefix_frame, textvariable=app.isn_prefix_var, width=10)
    isn_prefix_entry.pack(side=tk.LEFT, padx=5)
    
    def on_isn_prefix_change(*args):
        app.settings['image_search_isn_prefix'] = app.isn_prefix_var.get()
        app.config_manager.set('image_search_isn_prefix', app.isn_prefix_var.get())
        
    app.isn_prefix_var.trace_add("write", on_isn_prefix_change)
    
    # 原始 LOG 懸停顏色設定
    hover_color_frame = ttk.Frame(other_frame)
    hover_color_frame.pack(fill=tk.X, pady=8)
    
    hover_color_label = ttk.Label(hover_color_frame, text="LOG 懸停顏色：", font=('Arial', 10))
    hover_color_label._is_settings_label = True
    hover_color_label.pack(side=tk.LEFT)
    app.font_scaler.register(hover_color_label)
    
    # 顏色映射
    app.color_map = {
        "黃色 (預設)": "#FFF9C4",
        "藍色": "#E3F2FD",
        "綠色": "#E8F5E9",
        "紫色": "#F3E5F5",
        "橘色": "#FFF3E0",
        "灰色": "#F5F5F5"
    }
    app.reverse_color_map = {v: k for k, v in app.color_map.items()}
    
    current_color_hex = app.settings.get('log_hover_color', '#FFF9C4')
    current_color_name = app.reverse_color_map.get(current_color_hex, "黃色 (預設)")
    
    app.hover_color_var = tk.StringVar(value=current_color_name)
    hover_color_combo = ttk.Combobox(hover_color_frame, textvariable=app.hover_color_var, 
                                    values=list(app.color_map.keys()), state='readonly', width=12)
    hover_color_combo.pack(side=tk.LEFT, padx=5)
    
    # 🟢 FAIL 判定關鍵字設定
    fail_kw_frame = ttk.LabelFrame(right_column, text="FAIL 判定設定", padding=(15, 15))
    fail_kw_frame.pack(fill=tk.X, pady=5)
    app.font_scaler.register(fail_kw_frame)
    
    fail_kw_info = ttk.Label(fail_kw_frame, text="自定義 FAIL 關鍵字 (逗號分隔)：", font=('Arial', 10))
    fail_kw_info.pack(anchor=tk.W)
    app.font_scaler.register(fail_kw_info)
    
    app.fail_keywords_var = tk.StringVar(value=app.settings.get('user_fail_keywords', 'FAIL, FAILED, ERROR, NACK, timeout, Status:False, doesn\'t match'))
    fail_kw_entry = ttk.Entry(fail_kw_frame, textvariable=app.fail_keywords_var)
    fail_kw_entry.pack(fill=tk.X, pady=(5, 0))
    app.font_scaler.register(fail_kw_entry)
    
    fail_kw_hint = ttk.Label(fail_kw_frame, text="LOG 中若包含以上任一字串，該章節將判定為 FAIL", 
                            bootstyle="secondary", font=('Arial', 9))
    fail_kw_hint.pack(anchor=tk.W, pady=(5, 0))
    app.font_scaler.register(fail_kw_hint)
    
    # 主題設定區域
    theme_frame = ttk.LabelFrame(right_column, text="介面主題", padding=(15, 15))
    theme_frame.pack(fill=tk.X, pady=5)
    app.font_scaler.register(theme_frame)
    
    theme_edit_frame = ttk.Frame(theme_frame)
    theme_edit_frame.pack(fill=tk.X, pady=8)
    
    theme_label = ttk.Label(theme_edit_frame, text="主題名稱：", font=('Arial', 11))
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
    version_frame = ttk.LabelFrame(right_column, text="版本設定", padding=(15, 15))
    version_frame.pack(fill=tk.X, pady=5)
    app.font_scaler.register(version_frame)
    
    # 版本號碼設定
    version_edit_frame = ttk.Frame(version_frame)
    version_edit_frame.pack(fill=tk.X, pady=8)
    
    version_label = ttk.Label(version_edit_frame, text="版本號碼：", font=('Arial', 11))
    version_label._is_settings_label = True  # 標識為設定標籤
    version_label.pack(side=tk.LEFT)
    app.font_scaler.register(version_label)
    
    app.version_var = tk.StringVar(value=app.settings.get('version', 'V1.5.6'))
    version_entry = ttk.Entry(version_edit_frame, textvariable=app.version_var, width=20)
    version_entry._is_settings_entry = True  # 標識為設定輸入框
    version_entry.pack(side=tk.LEFT, padx=8)
    app.font_scaler.register(version_entry)
    
    # 版本說明
    version_info_label = ttk.Label(version_frame, text="版本號碼會顯示在應用程式標題和設定頁面中", 
                                 bootstyle="secondary", font=('Arial', 9))
    version_info_label._is_info_label = True  # 標識為說明文字
    version_info_label.pack(pady=(8, 0))
    app.font_scaler.register(version_info_label)
    
    # 圖片檢索設定區域
    image_search_frame = ttk.LabelFrame(left_column, text="圖片檢索設定", padding=(15, 15))
    image_search_frame.pack(fill=tk.X, pady=5)
    app.font_scaler.register(image_search_frame)
    
    # 啟用開關
    app.enable_image_search_var = tk.BooleanVar(value=app.settings.get('enable_image_search', True))
    enable_check = ttk.Checkbutton(image_search_frame, text="啟用圖片檢索功能", 
                                 variable=app.enable_image_search_var, 
                                 bootstyle="success-round-toggle")
    enable_check.pack(anchor=tk.W, pady=(0, 10))
    app.font_scaler.register(enable_check)
    
    # 搜尋根目錄
    root_frame = ttk.Frame(image_search_frame)
    root_frame.pack(fill=tk.X, pady=5)
    
    lbl_frame = ttk.Frame(root_frame)
    lbl_frame.pack(fill=tk.X)
    ttk.Label(lbl_frame, text="搜尋根路徑 (如 D:\\):", font=('Arial', 10)).pack(side=tk.LEFT)
    
    # 📁 新增選擇資料夾按鈕
    def on_browse_root():
        from tkinter import filedialog
        path = filedialog.askdirectory(initialdir=app.image_root_var.get())
        if path:
            # 轉換為 Windows 風格路徑並補上反斜線
            path = path.replace('/', '\\')
            if not path.endswith('\\'): path += '\\'
            app.image_root_var.set(path)

    browse_btn = ttk.Button(lbl_frame, text=" 📂 瀏覽... ", 
                          command=on_browse_root, bootstyle="secondary-outline")
    browse_btn.pack(side=tk.RIGHT)

    app.image_root_var = tk.StringVar(value=app.settings.get('image_search_root', 'D:\\'))
    root_entry = ttk.Entry(root_frame, textvariable=app.image_root_var)
    root_entry.pack(fill=tk.X, pady=(2, 0))
    
    # 目標資料夾名稱
    dir_name_frame = ttk.Frame(image_search_frame)
    dir_name_frame.pack(fill=tk.X, pady=5)
    ttk.Label(dir_name_frame, text="目標資料夾關鍵字 (如 STATION_RECORD):", font=('Arial', 10)).pack(anchor='w')
    app.image_dir_name_var = tk.StringVar(value=app.settings.get('image_search_dir_name', 'STATION_RECORD'))
    dir_entry = ttk.Entry(dir_name_frame, textvariable=app.image_dir_name_var)
    dir_entry.pack(fill=tk.X)
    
    # 原本的次級子目錄欄位已移除 (User Requested)
    
    # ===== 底部按鈕區域 =====
    
    # 分隔線
    separator = ttk.Separator(parent, orient='horizontal')
    separator.pack(fill=tk.X, padx=15, pady=15)
    
    # 按鈕區域
    button_frame = ttk.Frame(parent)
    button_frame.pack(fill=tk.X, padx=15, pady=15)
    
    # 統一的儲存設定按鈕
    save_btn = ttk.Button(button_frame, text="儲存所有設定", 
                        command=app._save_settings,
                        bootstyle="success",
                        width=15)
    save_btn._is_settings_button = True  # 標識為設定按鈕
    save_btn.pack(side=tk.RIGHT, padx=5)
    
    # 說明文字
    save_info_label = ttk.Label(button_frame, text="點擊儲存按鈕後，所有設定將立即生效", 
                              bootstyle="secondary", font=('Arial', 9))
    save_info_label._is_info_label = True  # 標識為說明文字
    save_info_label.pack(side=tk.LEFT, pady=10) 
