#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試Log分析器GUI應用程式 - 增強版
提供現代化的圖形使用者介面來分析測試log檔案
支援雙字體控制、視窗大小記憶、預覽視窗等功能
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import json
import time
from settings_loader import load_settings, save_settings
import webbrowser
from log_parser import LogParser
from ui_components import FontScaler, build_output_dir, get_resource_path
from ui_enhanced_fixed import EnhancedTreeview, EnhancedText, FailDetailsPanel
from enhanced_settings import build_settings_content
from enhanced_left_panel import build_left_panel
from excel_writer import ExcelWriter

class EnhancedLogAnalyzerApp:
    """增強版LOG分析器應用程式"""
    
    def __init__(self, root):
        """初始化增強版應用程式"""
        self.root = root
        
        # 檢查加密檔案
        if not self._check_encryption():
            return
        
        # 先載入設定再設定標題
        self.settings = load_settings()
        app_title = self.settings.get('app_title', 'PEGA test log Aanlyser')
        version = self.settings.get('version', 'V1.5.6')
        self.root.title(f"{app_title} {version}")
        
        # 載入設定（其餘）
        self.ui_font_size = self.settings.get('ui_font_size', 11)
        self.content_font_size = self.settings.get('content_font_size', 11)
        
        # 設定視窗大小 - 預設最大化
        window_width = self.settings.get('window_width', 1400)
        window_height = self.settings.get('window_height', 900)
        self.root.geometry(f"{window_width}x{window_height}")
        
        # 設定視窗最大化
        self.root.state('zoomed')  # Windows 最大化
        
        # 初始化模組
        self.font_scaler = FontScaler(root, default_size=self.ui_font_size)
        self.log_parser = LogParser()
        self.excel_writer = ExcelWriter()
        
        # 狀態變數
        self.current_mode = 'single'
        self.current_log_path = ''
        self.temp_cleanup_path = None  # 壓縮檔解壓縮的暫存路徑
        self._progress_win = None      # 背景處理進度窗
        self._cancel_flag = False      # 取消旗標
        self._search_cache = {'text': '', 'count': 0}
        
        # 建立UI
        self._build_enhanced_ui()
        self._apply_font_size()
        
        # 綁定視窗關閉事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _check_encryption(self):
        """檢查加密檔案"""
        try:
            # 獲取EXE所在目錄
            if getattr(sys, 'frozen', False):
                # 如果是打包的EXE
                exe_dir = os.path.dirname(sys.executable)
            else:
                # 如果是Python腳本
                exe_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 檢查SIGN.txt檔案
            sign_file = os.path.join(exe_dir, "SIGN.txt")
            
            if not os.path.exists(sign_file):
                self._show_encryption_error()
                return False
            
            # 讀取檔案內容
            with open(sign_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # 檢查是否包含jovian字串
            if 'jovian' not in content.lower():
                self._show_encryption_error()
                return False
            
            print("加密檔案驗證成功")
            return True
            
        except Exception as e:
            print(f"檢查加密檔案時發生錯誤: {e}")
            self._show_encryption_error()
            return False
    
    def _show_encryption_error(self):
        """顯示加密錯誤訊息"""
        messagebox.showerror("加密驗證失敗", "請提供運作工具的加密檔案")
        self.root.destroy()
    
    def _on_closing(self):
        """處理視窗關閉事件"""
        try:
            # 保存視窗大小
            self.settings['window_width'] = self.root.winfo_width()
            self.settings['window_height'] = self.root.winfo_height()
            
            # 保存左側面板寬度
            if hasattr(self, 'left_frame'):
                left_width = self.left_frame.winfo_width()
                if left_width > 0:  # 確保寬度有效
                    self.settings['pane_width'] = left_width
            
            # 保存字體設定
            self.settings['ui_font_size'] = self.ui_font_size
            self.settings['content_font_size'] = self.content_font_size
            
            # 保存其他設定
            if hasattr(self, 'auto_analyze_var'):
                self.settings['auto_analyze'] = self.auto_analyze_var.get()
            if hasattr(self, 'remember_path_var'):
                self.settings['remember_path'] = self.remember_path_var.get()
            
            save_settings(self.settings)
            print("設定已保存")
        except Exception as e:
            print(f"保存設定失敗: {e}")
        
        # 設定取消旗標並背景清理暫存檔案，避免關閉卡頓
        self._cancel_flag = True
        self._cleanup_temp_files_async()
        
        self.root.destroy()
    
    def _build_enhanced_ui(self):
        """建立增強版UI"""
        # 主要分割視窗
        self.paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        self.paned.pack(fill=tk.BOTH, expand=1)
        
        # 左側控制面板
        pane_width = self.settings.get('pane_width', 250)
        self.left_frame = tk.Frame(self.paned, width=pane_width)
        self._build_enhanced_left_panel(self.left_frame)
        self.paned.add(self.left_frame, minsize=200)
        
        # 右側結果顯示區域
        self.right_frame = tk.Frame(self.paned)
        self._build_enhanced_right_panel(self.right_frame)
        self.paned.add(self.right_frame, minsize=800)
        
        # 綁定分割視窗調整事件
        self.paned.bind('<ButtonRelease-1>', self._on_pane_adjust)
        self.paned.bind('<B1-Motion>', self._on_pane_adjust)  # 拖動時也保存
        
        # 設定初始面板寬度（使用after確保UI已建立）
        self.root.after(100, lambda: self._set_initial_pane_width(pane_width))
    
    def _set_initial_pane_width(self, width):
        """設定初始面板寬度"""
        try:
            if hasattr(self, 'paned') and hasattr(self, 'left_frame'):
                # 使用configure方法設定寬度
                self.left_frame.configure(width=width)
                # 強制更新
                self.paned.update_idletasks()
        except Exception as e:
            print(f"設定初始面板寬度失敗: {e}")
    
    def _on_pane_adjust(self, event):
        """處理分割視窗調整事件"""
        try:
            # 獲取左側面板的當前寬度
            if hasattr(self, 'left_frame'):
                left_width = self.left_frame.winfo_width()
                if left_width > 0:  # 確保寬度有效
                    self.settings['pane_width'] = left_width
                    # 更新設定標籤頁中的顯示
                    if hasattr(self, 'pane_width_label'):
                        self.pane_width_label.config(text=f"{left_width}px")
                    # 立即保存設定
                    save_settings(self.settings)
        except Exception as e:
            print(f"保存面板寬度失敗: {e}")
    
    def _build_enhanced_left_panel(self, parent):
        """建立增強版左側面板（抽離至模組）"""
        build_left_panel(parent, self)
    
    def _build_enhanced_right_panel(self, parent):
        """建立增強版右側面板"""
        # 建立頂部檔案資訊框架
        top_frame = tk.Frame(parent)
        top_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # 檔案資訊標籤
        self.file_info_label = tk.Label(top_frame, text="尚未選擇檔案", fg='gray', anchor='w')
        self.file_info_label.pack(fill=tk.X)
        self.font_scaler.register(self.file_info_label)
        
        # 建立標籤頁
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=1)
        
        # 設定標籤頁樣式
        self._setup_tab_styles()
        
        # 建立各標籤頁
        self._build_enhanced_pass_tab()
        self._build_enhanced_fail_tab()
        self._build_enhanced_log_tab()
        self._build_enhanced_settings_tab()
    
    def _setup_tab_styles(self):
        """設定標籤頁樣式"""
        style = ttk.Style()
        
        # 設定主題
        style.theme_use('clam')  # 使用clam主題，支援更多自訂樣式
        
        # 設定標籤頁基本樣式
        style.configure('TNotebook.Tab', 
                       font=('Arial', self.ui_font_size),
                       padding=[10, 5])
        
        # 設定標籤頁顏色映射
        style.map('TNotebook.Tab',
                 background=[('selected', '#2E7D32'),    # 選中：深綠底
                            ('active', '#2E7D32'),       # hover：深綠底
                            ('!selected', '#1565C0')],   # 未選中：深藍底
                 foreground=[('selected', 'white'),      # 選中：白字
                            ('active', 'white'),         # hover：白字
                            ('!selected', 'white')])     # 未選中：白字
    
    def _build_enhanced_pass_tab(self):
        """建立PASS標籤頁"""
        self.tab_pass = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_pass, text="✅ PASS測項")
        
        # 使用增強型TreeView
        pass_columns = ("測項名稱", "指令", "收到指令", "PASS/FAIL")
        self.pass_tree_enhanced = EnhancedTreeview(self.tab_pass, pass_columns)
        self.pass_tree_enhanced.pack_with_scrollbars(fill=tk.BOTH, expand=1)
    
    def _build_enhanced_fail_tab(self):
        """建立FAIL標籤頁 - 分割成上下兩個視窗"""
        self.tab_fail = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_fail, text="❌ FAIL測項")
        
        # 創建上下分割視窗
        self.fail_paned = tk.PanedWindow(self.tab_fail, orient=tk.VERTICAL, sashrelief=tk.RAISED)
        self.fail_paned.pack(fill=tk.BOTH, expand=1)
        
        # 上半部 - FAIL測項列表
        self.fail_upper_frame = tk.Frame(self.fail_paned)
        fail_columns = ("測項名稱", "指令", "錯誤回應", "Retry次數", "FAIL原因")
        self.fail_tree_enhanced = EnhancedTreeview(self.fail_upper_frame, fail_columns)
        self.fail_tree_enhanced.pack_with_scrollbars(fill=tk.BOTH, expand=1)
        self.fail_paned.add(self.fail_upper_frame, minsize=200)
        
        # 下半部 - FAIL錯誤詳細資訊
        self.fail_lower_frame = tk.Frame(self.fail_paned, bg='white')
        
        # 錯誤標題
        self.fail_error_title = tk.Label(self.fail_lower_frame, text="選擇FAIL項目查看詳細錯誤", 
                                        font=('Arial', 16, 'bold'), fg='red', bg='white')
        self.fail_error_title.pack(pady=10)
        
        # 錯誤內容文字框
        error_text_frame = tk.Frame(self.fail_lower_frame)
        error_text_frame.pack(fill=tk.BOTH, expand=1, padx=10, pady=5)
        
        self.fail_error_text = tk.Text(error_text_frame, wrap=tk.WORD, 
                                      bg='white', fg='black', font=('Consolas', 12))
        self.fail_error_text.grid(row=0, column=0, sticky='nsew')
        
        # 滾動條
        error_scrollbar = tk.Scrollbar(error_text_frame, command=self.fail_error_text.yview)
        error_scrollbar.grid(row=0, column=1, sticky='ns')
        self.fail_error_text.config(yscrollcommand=error_scrollbar.set)
        
        error_text_frame.grid_rowconfigure(0, weight=1)
        error_text_frame.grid_columnconfigure(0, weight=1)
        
        self.fail_paned.add(self.fail_lower_frame, minsize=150)
        
        # 載入FAIL分割視窗設定
        fail_pane_position = self.settings.get('fail_pane_position', 300)
        self.root.after(100, lambda: self._set_fail_pane_position(fail_pane_position))
        
        # 綁定分割視窗調整事件
        self.fail_paned.bind('<ButtonRelease-1>', self._on_fail_pane_adjust)
        
        # 綁定選擇事件
        self.fail_tree_enhanced.tree.bind('<<TreeviewSelect>>', self._on_fail_item_select)
        
        # 自動顯示第一個FAIL項目（如果有的話）
        self.root.after(500, self._auto_select_first_fail)
        
        # 自動顯示FAIL錯誤原因（不需要點擊）
        self.root.after(1000, self._auto_display_fail_reason)
    
    def _build_enhanced_log_tab(self):
        """建立原始LOG標籤頁"""
        self.tab_log = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_log, text="📄 原始LOG")
        
        # 使用增強型文字元件
        self.log_text_enhanced = EnhancedText(self.tab_log)
        self.log_text_enhanced.pack(fill=tk.BOTH, expand=1)

    def _build_enhanced_settings_tab(self):
        """建立設定標籤頁"""
        self.tab_settings = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_settings, text="⚙️ 設定")
        
        # 建立滾動框架
        canvas = tk.Canvas(self.tab_settings)
        scrollbar = ttk.Scrollbar(self.tab_settings, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 設定區域
        self._build_settings_content(scrollable_frame)
        
        # 打包滾動元件
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 綁定滾動事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def _build_settings_content(self, parent):
        """建立設定內容（抽離至模組）"""
        build_settings_content(self, parent)
    
    def _get_default_directory(self):
        """獲取預設目錄 - EXE或PY檔案所在目錄"""
        try:
            # 如果是EXE檔案，使用sys.executable
            if getattr(sys, 'frozen', False):
                # 打包成EXE的情況
                default_dir = os.path.dirname(sys.executable)
            else:
                # 直接執行PY檔案的情況
                default_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 如果目錄不存在，使用當前工作目錄
            if not os.path.exists(default_dir):
                default_dir = os.getcwd()
            
            return default_dir
        except Exception:
            # 如果出現任何錯誤，使用當前工作目錄
            return os.getcwd()
    
    def _select_file(self):
        """選擇單一檔案"""
        # 優先使用上次選擇的路徑，如果沒有則使用預設路徑
        if self.settings.get('last_log_path') and os.path.exists(self.settings.get('last_log_path')):
            default_dir = os.path.dirname(self.settings.get('last_log_path'))
        else:
            default_dir = self._get_default_directory()
        
        file_path = filedialog.askopenfilename(
            title="選擇Log檔案", 
            filetypes=[("Log檔案", "*.log"), ("所有檔案", "*.*")],
            initialdir=default_dir
        )
        if file_path:
            # 先清除現有結果，避免誤導
            self._clear_enhanced_results()
            
            # 顯示檔案預覽
            self._show_file_preview(file_path, 'log')
            
            self.current_mode = 'single'
            self.current_log_path = file_path
            filename = os.path.basename(file_path)
            self.file_info_label.config(text=f"已選擇：{filename}", fg='green')
            
            # 儲存選擇的路徑到設定
            self.settings['last_log_path'] = file_path
            self._save_settings_silent()
            
            # 自動開始分析（enhanced）
            self._analyze_enhanced_log()
    
    def _select_folder(self):
        """選擇資料夾"""
        # 優先使用上次選擇的路徑，如果沒有則使用預設路徑
        if self.settings.get('last_folder_path') and os.path.exists(self.settings.get('last_folder_path')):
            default_dir = self.settings.get('last_folder_path')
        else:
            default_dir = self._get_default_directory()
        
        # 先讓使用者看到所有內容物（僅視覺，實際只處理 .log）
        folder_path = filedialog.askdirectory(
            title="選擇Log資料夾",
            initialdir=default_dir
        )
        if folder_path:
            # 先清除現有結果，避免誤導
            self._clear_enhanced_results()
            
            self.current_mode = 'multi'
            self.current_log_path = folder_path
            
            foldername = os.path.basename(folder_path)
            self.file_info_label.config(text=f"已選擇資料夾：{foldername}", fg='blue')
            
            # 儲存選擇的路徑到設定
            self.settings['last_folder_path'] = folder_path
            self._save_settings_silent()
            
            # 自動開始分析（enhanced）
            self._analyze_enhanced_log()
    
    def _select_compressed_file(self):
        """選擇並處理壓縮檔案（支援多選）"""
        import tempfile
        import shutil
        
        # 獲取預設目錄
        if self.settings.get('last_compressed_path') and os.path.exists(self.settings.get('last_compressed_path')):
            default_dir = os.path.dirname(self.settings.get('last_compressed_path'))
        else:
            default_dir = self._get_default_directory()
        
        file_paths = filedialog.askopenfilenames(
            title="選擇壓縮檔案（可多選）", 
            filetypes=[
                ("壓縮檔案", "*.zip;*.7z;*.rar"),
                ("ZIP檔案", "*.zip"),
                ("7Z檔案", "*.7z"), 
                ("RAR檔案", "*.rar"),
                ("所有檔案", "*.*")
            ],
            initialdir=default_dir
        )
        
        if file_paths:
            # 先清除現有結果
            self._clear_enhanced_results()
            
            if len(file_paths) == 1:
                # 單一檔案：顯示預覽後直接處理
                self._show_file_preview(file_paths[0], 'compressed')
                self._process_single_compressed_file(file_paths[0])
            else:
                # 多個檔案：顯示選擇視窗
                self._show_compressed_selection_window(file_paths)
    
    def _process_single_compressed_file(self, file_path):
        """處理單一壓縮檔案"""
        # 背景處理壓縮檔案
        self._show_progress("正在處理壓縮檔", os.path.basename(file_path))
        def _bg():
            try:
                if self._cancel_flag:
                    return
                self._process_compressed_file(file_path)
            finally:
                self.root.after(0, self._close_progress)
        import threading
        threading.Thread(target=_bg, daemon=True).start()

    def _select_compressed_files(self):
        """整合的壓縮檔選擇功能（支援單一檔案、多個檔案或資料夾）"""
        # 提供選擇方式
        choice = messagebox.askyesnocancel(
            "壓縮檔處理方式", 
            "請選擇壓縮檔處理方式：\n\n" +
            "是(Y) - 選擇壓縮檔案（支援多選）\n" +
            "否(N) - 選擇壓縮檔資料夾（自動搜尋所有壓縮檔）\n" +
            "取消 - 取消操作\n\n" +
            "注意：選擇資料夾時會自動搜尋 .zip/.7z/.rar 檔案"
        )
        
        if choice is True:
            # 選擇壓縮檔案（支援多選）
            self._select_compressed_file()
        elif choice is False:
            # 選擇壓縮檔資料夾
            self._select_compressed_folder()
        # choice is None 表示取消

    def _select_compressed_folder(self):
        """選擇並處理含多個壓縮檔的資料夾（支援多層與內嵌壓縮）"""
        import tempfile
        import shutil
        
        # 取得預設目錄
        if self.settings.get('last_compressed_folder') and os.path.exists(self.settings.get('last_compressed_folder')):
            default_dir = self.settings.get('last_compressed_folder')
        else:
            default_dir = self._get_default_directory()
        
        folder_path = filedialog.askdirectory(title="選擇壓縮檔資料夾", initialdir=default_dir)
        if not folder_path:
            return
        
        # 先清除現有結果
        self._clear_enhanced_results()
        
        # 讓使用者挑選要處理的壓縮檔
        archives = []
        for root, dirs, files in os.walk(folder_path):
            for fn in files:
                if self._is_archive_file(fn):
                    archives.append(os.path.join(root, fn))
        
        if not archives:
            # 提供更詳細的提示和選項
            result = messagebox.askyesno(
                "未找到壓縮檔案", 
                f"在選擇的資料夾中未找到支援的壓縮檔案 (.zip/.7z/.rar)\n\n" +
                f"資料夾路徑: {folder_path}\n\n" +
                "可能的原因：\n" +
                "• 資料夾中沒有壓縮檔案\n" +
                "• 壓縮檔案在其他子資料夾中\n" +
                "• 壓縮檔案格式不支援\n\n" +
                "是否要重新選擇資料夾？"
            )
            if result:
                # 重新選擇資料夾
                self._select_compressed_folder()
            else:
                # 提供其他選項
                choice2 = messagebox.askyesno(
                    "其他選項", 
                    "是否要改為直接選擇壓縮檔案？"
                )
                if choice2:
                    self._select_compressed_file()
            return
        
        self._show_archive_preview(archives)
        selected_archives = self._choose_archives_dialog(archives)
        if not selected_archives:
            return

        # 背景處理整個壓縮資料夾
        self._show_progress("正在處理壓縮資料夾 (多選)", folder_path)
        def _bg():
            import tempfile, shutil
            temp_dir = None
            try:
                if self._cancel_flag:
                    return
                # 建立總暫存目錄
                temp_dir = tempfile.mkdtemp(prefix="log_archives_")
                extracted_root = os.path.join(temp_dir, "extracted")
                os.makedirs(extracted_root, exist_ok=True)
                
                # 逐一解壓到各自子目錄（顯示百分比）
                total = len(selected_archives)
                self.root.after(0, lambda: self._progress_set_determinate(total))
                for idx, apath in enumerate(selected_archives, 1):
                    if self._cancel_flag:
                        # 取消時清理暫存目錄
                        try:
                            shutil.rmtree(temp_dir, ignore_errors=True)
                        except Exception:
                            pass
                        return
                    base = os.path.splitext(os.path.basename(apath))[0]
                    target = os.path.join(extracted_root, f"{idx:03d}_{base}")
                    os.makedirs(target, exist_ok=True)
                    try:
                        self._update_progress(f"解壓中 {idx}/{total}: {os.path.basename(apath)}")
                        self._extract_archive(apath, target)
                        self._extract_all_archives(target, max_depth=5)
                    except Exception as e:
                        print(f"解壓失敗（略過）：{apath} -> {e}")
                        continue
                    # 更新進度百分比
                    self.root.after(0, lambda i=idx, n=total: self._progress_set_value(i, n))
                
                # 搜尋所有 .log
                log_files = self._find_log_files(extracted_root)
                if not log_files:
                    self.root.after(0, lambda: messagebox.showwarning("警告", "壓縮資料夾展開後未找到 .log 檔案"))
                    return
                
                def _apply_result():
                    if len(log_files) == 1:
                        self.current_mode = 'single'
                        self.current_log_path = log_files[0]
                        filename = os.path.basename(log_files[0])
                        self.file_info_label.config(text=f"已選擇：{filename} (來自壓縮資料夾)", fg='orange')
                    else:
                        self.current_mode = 'multi'
                        self.current_log_path = extracted_root
                        self.file_info_label.config(text=f"已選擇：{len(log_files)} 個LOG檔案 (來自壓縮資料夾)", fg='orange')
                    self.settings['last_compressed_folder'] = folder_path
                    self._save_settings_silent()
                    self._analyze_enhanced_log()
                self.temp_cleanup_path = temp_dir
                self.root.after(0, _apply_result)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("錯誤", f"處理壓縮資料夾時發生錯誤：\n{e}"))
                if temp_dir and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
            finally:
                self.root.after(0, self._close_progress)
        import threading
        threading.Thread(target=_bg, daemon=True).start()

    def _show_archive_preview(self, archives: list):
        """在頂部資訊區顯示即將處理的壓縮檔清單（僅預覽）"""
        try:
            lines = ["將處理以下壓縮檔：", ""]
            max_show = 30
            for i, p in enumerate(sorted(archives)[:max_show], 1):
                lines.append(f"  • {os.path.basename(p)}")
            if len(archives) > max_show:
                lines.append(f"... 其餘 {len(archives) - max_show} 個未列出")
            text = "\n".join(lines)
            if hasattr(self, 'file_info_label'):
                self.file_info_label.config(text=text, justify='left', wraplength=420, fg='#333')
        except Exception as e:
            print(f"顯示壓縮檔預覽失敗: {e}")

    def _choose_archives_dialog(self, archives: list) -> list:
        """彈出多選對話框，讓使用者挑選要處理的壓縮檔。回傳選中的清單。"""
        try:
            win = tk.Toplevel(self.root)
            win.title("選擇要處理的壓縮檔")
            win.geometry("520x420")
            win.transient(self.root)
            win.grab_set()
            frm = tk.Frame(win)
            frm.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)
            lbl = tk.Label(frm, text="請勾選要處理的壓縮檔：")
            lbl.pack(anchor='w')
            lb_frame = tk.Frame(frm)
            lb_frame.pack(fill=tk.BOTH, expand=1)
            canvas = tk.Canvas(lb_frame)
            vsb = tk.Scrollbar(lb_frame, orient="vertical", command=canvas.yview)
            inner = tk.Frame(canvas)
            inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0,0), window=inner, anchor='nw')
            canvas.configure(yscrollcommand=vsb.set)
            canvas.pack(side="left", fill="both", expand=True)
            vsb.pack(side="right", fill="y")

            vars_ = []
            for p in sorted(archives):
                var = tk.BooleanVar(value=True)
                cb = tk.Checkbutton(inner, text=os.path.basename(p), variable=var, anchor='w', justify='left')
                cb.pack(fill=tk.X, anchor='w')
                vars_.append((var, p))

            btns = tk.Frame(frm)
            btns.pack(fill=tk.X, pady=8)
            selected = []
            def on_ok():
                nonlocal selected
                selected = [p for (v,p) in vars_ if v.get()]
                win.destroy()
            def on_cancel():
                selected.clear()
                win.destroy()
            tk.Button(btns, text="全選", command=lambda: [v.set(True) for v,_ in vars_]).pack(side=tk.LEFT)
            tk.Button(btns, text="全不選", command=lambda: [v.set(False) for v,_ in vars_]).pack(side=tk.LEFT, padx=6)
            tk.Button(btns, text="確定", command=on_ok).pack(side=tk.RIGHT)
            tk.Button(btns, text="取消", command=on_cancel).pack(side=tk.RIGHT, padx=6)
            win.wait_window()
            return selected
        except Exception as e:
            print(f"選擇壓縮檔對話框失敗: {e}")
            return archives

    def _process_compressed_file(self, compressed_path):
        """處理壓縮檔案"""
        import tempfile
        import shutil
        
        try:
            # 建立暫存目錄
            temp_dir = tempfile.mkdtemp(prefix="log_analyzer_")
            
            # 檢查取消狀態
            if self._cancel_flag:
                shutil.rmtree(temp_dir, ignore_errors=True)
                return
            
            # 解壓縮
            file_ext = os.path.splitext(compressed_path)[1].lower()
            
            if file_ext == '.zip':
                self._extract_zip(compressed_path, temp_dir)
            elif file_ext == '.7z':
                self._extract_7z(compressed_path, temp_dir)
            elif file_ext == '.rar':
                self._extract_rar(compressed_path, temp_dir)
            else:
                messagebox.showerror("錯誤", "不支援的壓縮格式")
                shutil.rmtree(temp_dir, ignore_errors=True)
                return

            # 檢查取消狀態
            if self._cancel_flag:
                shutil.rmtree(temp_dir, ignore_errors=True)
                return

            # 遞迴展開內嵌壓縮檔
            try:
                self._extract_all_archives(temp_dir, max_depth=5)
            except Exception as sub_e:
                # 不阻斷主流程，僅提示
                print(f"遞迴解壓過程發生問題：{sub_e}")
            
            # 檢查取消狀態
            if self._cancel_flag:
                shutil.rmtree(temp_dir, ignore_errors=True)
                return
            
            # 搜尋 LOG 檔案
            log_files = self._find_log_files(temp_dir)
            
            if not log_files:
                messagebox.showwarning("警告", "壓縮檔中未找到 .log 檔案")
                return
            
            # 根據檔案數量決定處理模式
            if len(log_files) == 1:
                # 單檔模式
                self.current_mode = 'single'
                self.current_log_path = log_files[0]
                filename = os.path.basename(log_files[0])
                self.file_info_label.config(text=f"已選擇：{filename} (來自壓縮檔)", fg='orange')
            else:
                # 資料夾模式
                self.current_mode = 'multi'
                self.current_log_path = temp_dir
                self.file_info_label.config(text=f"已選擇：{len(log_files)} 個LOG檔案 (來自壓縮檔)", fg='orange')
            
            # 儲存選擇的路徑到設定
            # 儲存選擇的路徑到設定
            self.settings['last_compressed_path'] = compressed_path
            self._save_settings_silent()
            
            # 開始分析 (必須回到主執行緒執行，因為會更新UI)
            self.root.after(0, self._analyze_enhanced_log)
            
            # 註冊清理函數（分析完成後清理暫存檔案）
            self.temp_cleanup_path = temp_dir
            
        except Exception as e:
            messagebox.showerror("錯誤", f"處理壓縮檔案時發生錯誤：\n{str(e)}")
            # 清理暫存目錄
            if 'temp_dir' in locals() and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _extract_zip(self, zip_path, extract_to):
        """解壓縮 ZIP 檔案"""
        try:
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        except Exception as e:
            error_msg = f"ZIP檔案解壓縮失敗: {str(e)}\n\n檔案: {zip_path}\n\n可能的原因:\n"
            error_msg += "• 檔案損壞或格式不正確\n"
            error_msg += "• 檔案被密碼保護\n"
            error_msg += "• 檔案權限不足\n"
            error_msg += "• ZIP格式不相容\n\n"
            error_msg += "建議:\n"
            error_msg += "• 檢查檔案是否完整\n"
            error_msg += "• 嘗試使用其他工具解壓\n"
            error_msg += "• 檢查檔案是否被密碼保護"
            
            messagebox.showerror("ZIP解壓縮失敗", error_msg)
            raise

    def _extract_7z(self, sevenz_path, extract_to):
        """解壓縮 7Z 檔案（多種方式嘗試）"""
        try:
            import py7zr
            
            # 方法1：標準解壓縮
            try:
                with py7zr.SevenZipFile(sevenz_path, mode='r') as archive:
                    archive.extractall(path=extract_to)
                return
            except Exception as e1:
                print(f"標準7Z解壓縮失敗: {e1}")
                
                # 方法2：嘗試不同的模式
                try:
                    with py7zr.SevenZipFile(sevenz_path, mode='r', password=None) as archive:
                        archive.extractall(path=extract_to)
                    return
                except Exception as e2:
                    print(f"無密碼7Z解壓縮失敗: {e2}")
                    
                    # 方法3：嘗試讀取檔案列表
                    try:
                        with py7zr.SevenZipFile(sevenz_path, mode='r') as archive:
                            file_list = archive.getnames()
                            print(f"7Z檔案包含 {len(file_list)} 個檔案")
                            # 如果檔案列表可以讀取，但解壓失敗，可能是權限問題
                            raise Exception(f"無法解壓縮7Z檔案，但檔案列表可讀取。可能的原因：權限不足或檔案損壞")
                    except Exception as e3:
                        print(f"7Z檔案列表讀取失敗: {e3}")
                        raise e1  # 拋出原始錯誤
                        
        except ImportError:
            messagebox.showerror("錯誤", "需要安裝 py7zr 套件來支援 7Z 格式\n請執行：pip install py7zr")
            raise
        except Exception as e:
            error_msg = f"7Z檔案解壓縮失敗: {str(e)}\n\n檔案: {sevenz_path}\n\n可能的原因:\n"
            error_msg += "• 檔案損壞或格式不正確\n"
            error_msg += "• 檔案被密碼保護\n"
            error_msg += "• 檔案權限不足\n"
            error_msg += "• py7zr版本不相容\n"
            error_msg += "• 檔案被加密\n\n"
            error_msg += "建議:\n"
            error_msg += "• 檢查檔案是否完整\n"
            error_msg += "• 嘗試使用7-Zip軟體手動解壓\n"
            error_msg += "• 更新py7zr套件: pip install --upgrade py7zr\n"
            error_msg += "• 檢查檔案是否被密碼保護"
            
            messagebox.showerror("7Z解壓縮失敗", error_msg)
            raise

    def _extract_rar(self, rar_path, extract_to):
        """解壓縮 RAR 檔案"""
        try:
            import rarfile
            with rarfile.RarFile(rar_path) as rf:
                rf.extractall(extract_to)
        except ImportError:
            messagebox.showerror("錯誤", "需要安裝 rarfile 套件來支援 RAR 格式\n請執行：pip install rarfile")
            raise
        except Exception as e:
            error_msg = f"RAR檔案解壓縮失敗: {str(e)}\n\n檔案: {rar_path}\n\n可能的原因:\n"
            error_msg += "• 檔案損壞或格式不正確\n"
            error_msg += "• 檔案被密碼保護\n"
            error_msg += "• 檔案權限不足\n"
            error_msg += "• rarfile版本不相容\n\n"
            error_msg += "建議:\n"
            error_msg += "• 檢查檔案是否完整\n"
            error_msg += "• 嘗試使用其他工具解壓\n"
            error_msg += "• 更新rarfile套件: pip install --upgrade rarfile"
            
            messagebox.showerror("RAR解壓縮失敗", error_msg)
            raise

    def _is_archive_file(self, filename):
        """判斷是否為支援的壓縮檔案"""
        lower = filename.lower()
        return lower.endswith('.zip') or lower.endswith('.7z') or lower.endswith('.rar')

    def _extract_archive(self, archive_path, extract_to):
        """根據副檔名解壓縮檔案到指定目錄"""
        ext = os.path.splitext(archive_path)[1].lower()
        if ext == '.zip':
            self._extract_zip(archive_path, extract_to)
        elif ext == '.7z':
            self._extract_7z(archive_path, extract_to)
        elif ext == '.rar':
            self._extract_rar(archive_path, extract_to)

    def _extract_all_archives(self, root_dir, max_depth=5):
        """遞迴展開 root_dir 底下所有內嵌壓縮檔（限制深度避免無限循環）"""
        processed = set()
        depth = 0
        while depth < max_depth:
            found_new = False
            for current_root, dirs, files in os.walk(root_dir):
                for fname in files:
                    if not self._is_archive_file(fname):
                        continue
                    full_path = os.path.join(current_root, fname)
                    if full_path in processed:
                        continue
                    # 為每個壓縮檔建立對應資料夾（同名去副檔名加 _extracted）
                    base, _ = os.path.splitext(fname)
                    target_dir = os.path.join(current_root, f"{base}_extracted")
                    try:
                        os.makedirs(target_dir, exist_ok=True)
                        self._extract_archive(full_path, target_dir)
                        processed.add(full_path)
                        found_new = True
                    except Exception as e:
                        print(f"展開內嵌壓縮檔失敗：{full_path} -> {e}")
                        # 繼續嘗試其他檔案
                        continue
            if not found_new:
                break
            depth += 1

    def _find_log_files(self, directory):
        """搜尋目錄中的 LOG 檔案"""
        log_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.log'):
                    log_files.append(os.path.join(root, file))
        return log_files
    
    def _cleanup_temp_files(self):
        """清理壓縮檔解壓縮的暫存檔案"""
        import shutil
        try:
            if hasattr(self, 'temp_cleanup_path') and self.temp_cleanup_path:
                if os.path.exists(self.temp_cleanup_path):
                    shutil.rmtree(self.temp_cleanup_path, ignore_errors=True)
                    print(f"已清理暫存目錄: {self.temp_cleanup_path}")
                self.temp_cleanup_path = None
        except Exception as e:
            print(f"清理暫存檔案時發生錯誤: {e}")

    def _cleanup_temp_files_async(self):
        """在背景執行暫存清理，避免關閉視窗時卡頓"""
        try:
            import threading, os
            path = getattr(self, 'temp_cleanup_path', None)
            if not path or not os.path.exists(path):
                return
            def _bg():
                try:
                    self._cleanup_temp_files()
                except Exception as e:
                    print(f"背景清理失敗: {e}")
            threading.Thread(target=_bg, daemon=True).start()
        except Exception as e:
            print(f"啟動背景清理失敗: {e}")

    # ===== 背景處理與進度 =====
    def _show_progress(self, title: str, message: str = ""):
        try:
            if self._progress_win and self._progress_win.winfo_exists():
                return
            win = tk.Toplevel(self.root)
            win.title(title)
            win.geometry("450x160")
            win.transient(self.root)
            win.grab_set()
            frame = tk.Frame(win)
            frame.pack(fill=tk.BOTH, expand=1, padx=12, pady=12)
            
            # 主標籤
            lbl = tk.Label(frame, text=message or title, anchor='w', justify='left', font=('Arial', 10))
            lbl.pack(fill=tk.X)
            
            # 進度條
            from tkinter import ttk as _ttk
            bar = _ttk.Progressbar(frame, mode='indeterminate')
            bar.pack(fill=tk.X, pady=10)
            bar.start(12)
            
            # 時間估算標籤
            time_label = tk.Label(frame, text="預估剩餘時間: 計算中...", font=('Arial', 9), fg='gray')
            time_label.pack(anchor='w')
            
            def on_cancel():
                self._cancel_flag = True
                lbl.config(text="正在取消，請稍候…")
            btn = tk.Button(frame, text="取消", command=on_cancel)
            btn.pack(pady=(4,0))
            
            self._progress_win = win
            self._progress_label = lbl
            self._progress_bar = bar
            self._time_label = time_label
            self._start_time = None
        except Exception as e:
            print(f"顯示進度窗失敗: {e}")

    def _update_progress(self, text: str):
        try:
            if self._progress_win and self._progress_win.winfo_exists():
                self._progress_label.config(text=text)
        except Exception:
            pass

    def _close_progress(self):
        try:
            if self._progress_win and self._progress_win.winfo_exists():
                self._progress_win.destroy()
        except Exception:
            pass
        self._progress_win = None
        self._cancel_flag = False

    def _progress_set_determinate(self, maximum: int):
        """將進度條切換為可顯示百分比的 determinate 模式"""
        try:
            from tkinter import ttk as _ttk
            if not (self._progress_win and self._progress_win.winfo_exists()):
                return
            try:
                self._progress_bar.stop()
            except Exception:
                pass
            self._progress_bar.configure(mode='determinate', maximum=max(1, int(maximum)))
            self._progress_bar['value'] = 0
            self._start_time = time.time()  # 記錄開始時間
        except Exception as e:
            print(f"設定 determinate 進度失敗: {e}")

    def _progress_set_value(self, current: int, total: int):
        try:
            if not (self._progress_win and self._progress_win.winfo_exists()):
                return
            total = max(1, int(total))
            current = min(max(0, int(current)), total)
            self._progress_bar['value'] = current
            percent = int(current * 100 / total)
            self._progress_label.config(text=f"正在分析... {percent}%")
            
            # 計算剩餘時間
            if hasattr(self, '_start_time') and self._start_time and current > 0:
                elapsed_time = time.time() - self._start_time
                if current < total:
                    avg_time_per_item = elapsed_time / current
                    remaining_items = total - current
                    estimated_remaining = avg_time_per_item * remaining_items
                    
                    if estimated_remaining < 60:
                        time_text = f"預估剩餘時間: {int(estimated_remaining)} 秒"
                    else:
                        minutes = int(estimated_remaining // 60)
                        seconds = int(estimated_remaining % 60)
                        time_text = f"預估剩餘時間: {minutes} 分 {seconds} 秒"
                else:
                    time_text = "即將完成..."
                
                if hasattr(self, '_time_label'):
                    self._time_label.config(text=time_text)
            
            self._progress_win.update_idletasks()
        except Exception:
            pass
    
    def _clear_enhanced_results(self):
        """清除分析結果並清理暫存檔案"""
        try:
            # 清理壓縮檔解壓縮的暫存檔案
            self._cleanup_temp_files()
            
            # 清除當前選擇的路徑
            self.current_log_path = ''
            self.current_mode = 'single'
            
            # 清除 UI 顯示
            if hasattr(self, 'file_info_label'):
                self.file_info_label.config(text="尚未選擇檔案", fg='gray')
            
            # 清除分頁內容
            if hasattr(self, 'pass_tree'):
                for item in self.pass_tree.get_children():
                    self.pass_tree.delete(item)
            
            if hasattr(self, 'fail_tree'):
                for item in self.fail_tree.get_children():
                    self.fail_tree.delete(item)
            
            if hasattr(self, 'raw_text'):
                self.raw_text.delete(1.0, tk.END)
            
            print("已清除所有結果")
        except Exception as e:
            print(f"清除結果時發生錯誤: {e}")
    
    def _on_search_change(self, event):
        """搜尋內容改變時的即時搜尋"""
        try:
            print("搜尋內容改變事件觸發")
            # 如果輸入超過2個字元就開始搜尋
            search_text = self.search_var.get().strip()
            print(f"搜尋文字：'{search_text}'")
            if len(search_text) >= 2:
                self._search_next()
            elif len(search_text) == 0:
                self._clear_search()
        except Exception as e:
            print(f"搜尋改變事件錯誤: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_search_enter(self, event):
        """按下Enter鍵時執行搜尋"""
        try:
            print("Enter鍵搜尋事件觸發")
            self._search_next()
        except Exception as e:
            print(f"Enter搜尋事件錯誤: {e}")
            import traceback
            traceback.print_exc()
    
    def _search_next(self):
        """搜尋下一個匹配項目"""
        try:
            search_text = self.search_var.get().strip()
            if not search_text:
                return
            
            # 檢查當前選中的標籤頁
            current_tab = self.notebook.select()
            print(f"搜尋下一個 - 當前標籤頁：{current_tab}")
            
            # 獲取當前選中的標籤頁索引
            current_tab_index = self.notebook.index(current_tab)
            print(f"搜尋下一個 - 當前標籤頁索引：{current_tab_index}")
            
            if current_tab_index == 2:  # 原始LOG標籤頁
                # 在原始LOG標籤頁中搜尋
                if hasattr(self, 'log_text_enhanced') and hasattr(self.log_text_enhanced, 'text'):
                    self._search_next_in_text(self.log_text_enhanced.text, search_text)
                elif hasattr(self, 'raw_text'):
                    self._search_next_in_text(self.raw_text, search_text)
                else:
                    print("未找到原始LOG Text元件")
            else:
                # 在其他標籤頁中搜尋
                self._perform_search()
                
        except Exception as e:
            print(f"搜尋下一個時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
    
    def _search_prev(self):
        """搜尋上一個匹配項目"""
        try:
            search_text = self.search_var.get().strip()
            if not search_text:
                return
            
            # 檢查當前選中的標籤頁
            current_tab = self.notebook.select()
            print(f"搜尋上一個 - 當前標籤頁：{current_tab}")
            
            # 獲取當前選中的標籤頁索引
            current_tab_index = self.notebook.index(current_tab)
            print(f"搜尋上一個 - 當前標籤頁索引：{current_tab_index}")
            
            if current_tab_index == 2:  # 原始LOG標籤頁
                # 在原始LOG標籤頁中搜尋
                if hasattr(self, 'log_text_enhanced') and hasattr(self.log_text_enhanced, 'text'):
                    self._search_prev_in_text(self.log_text_enhanced.text, search_text)
                elif hasattr(self, 'raw_text'):
                    self._search_prev_in_text(self.raw_text, search_text)
                else:
                    print("未找到原始LOG Text元件")
            else:
                # 在其他標籤頁中搜尋
                self._perform_search()
                
        except Exception as e:
            print(f"搜尋上一個時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
    
    def _search_next_in_text(self, text_widget, search_text):
        """在Text元件中搜尋下一個"""
        try:
            print(f"在Text中搜尋下一個：'{search_text}'")
            
            # 檢查Text元件是否有內容
            content = text_widget.get('1.0', tk.END)
            print(f"Text內容長度：{len(content)}")
            
            if len(content) <= 1:  # 只有換行符
                print("Text元件為空，無法搜尋")
                self._update_search_count(0)
                return
            
            # 先清除之前的選取
            text_widget.tag_remove(tk.SEL, '1.0', tk.END)
            text_widget.tag_remove('search_highlight', '1.0', tk.END)
            
            # 設定搜尋高亮樣式
            text_widget.tag_configure('search_highlight', background='#FFFF00', foreground='#000000')
            
            # 計算總匹配數量
            count = 0
            pos = '1.0'
            while True:
                pos = text_widget.search(search_text, pos, tk.END, nocase=True)
                if not pos:
                    break
                count += 1
                end_pos = f"{pos}+{len(search_text)}c"
                text_widget.tag_add('search_highlight', pos, end_pos)
                pos = end_pos
            
            # 更新搜尋計數
            self._update_search_count(count)
            
            # 從當前游標位置開始搜尋
            pos = text_widget.search(search_text, tk.INSERT, tk.END, nocase=True)
            if pos:
                # 找到匹配項目
                end_pos = f"{pos}+{len(search_text)}c"
                text_widget.mark_set(tk.INSERT, end_pos)
                text_widget.see(pos)
                text_widget.tag_add(tk.SEL, pos, end_pos)
                print(f"找到下一個匹配項目：{pos}")
            else:
                # 從頭開始搜尋
                pos = text_widget.search(search_text, '1.0', tk.END, nocase=True)
                if pos:
                    end_pos = f"{pos}+{len(search_text)}c"
                    text_widget.mark_set(tk.INSERT, end_pos)
                    text_widget.see(pos)
                    text_widget.tag_add(tk.SEL, pos, end_pos)
                    print(f"從頭找到匹配項目：{pos}")
                else:
                    print("未找到匹配項目")
                    
        except Exception as e:
            print(f"搜尋下一個時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
    
    def _search_prev_in_text(self, text_widget, search_text):
        """在Text元件中搜尋上一個"""
        try:
            print(f"在Text中搜尋上一個：'{search_text}'")
            
            # 檢查Text元件是否有內容
            content = text_widget.get('1.0', tk.END)
            print(f"Text內容長度：{len(content)}")
            
            if len(content) <= 1:  # 只有換行符
                print("Text元件為空，無法搜尋")
                self._update_search_count(0)
                return
            
            # 先清除之前的選取
            text_widget.tag_remove(tk.SEL, '1.0', tk.END)
            text_widget.tag_remove('search_highlight', '1.0', tk.END)
            
            # 設定搜尋高亮樣式
            text_widget.tag_configure('search_highlight', background='#FFFF00', foreground='#000000')
            
            # 計算總匹配數量
            count = 0
            pos = '1.0'
            while True:
                pos = text_widget.search(search_text, pos, tk.END, nocase=True)
                if not pos:
                    break
                count += 1
                end_pos = f"{pos}+{len(search_text)}c"
                text_widget.tag_add('search_highlight', pos, end_pos)
                pos = end_pos
            
            # 更新搜尋計數
            self._update_search_count(count)
            
            # 從當前游標位置向前搜尋
            current_pos = text_widget.index(tk.INSERT)
            print(f"當前游標位置：{current_pos}")
            
            # 從當前位置向前搜尋（不包含當前位置）
            if current_pos != '1.0':
                prev_pos = text_widget.index(f"{current_pos}-1c")
                pos = text_widget.search(search_text, '1.0', prev_pos, nocase=True, backwards=True)
            else:
                # 如果已經在開頭，從末尾開始搜尋
                pos = text_widget.search(search_text, tk.END, '1.0', nocase=True, backwards=True)
            
            if pos:
                # 找到匹配項目
                end_pos = f"{pos}+{len(search_text)}c"
                text_widget.mark_set(tk.INSERT, pos)
                text_widget.see(pos)
                text_widget.tag_add(tk.SEL, pos, end_pos)
                print(f"找到上一個匹配項目：{pos}")
            else:
                print("未找到匹配項目")
                    
        except Exception as e:
            print(f"搜尋上一個時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
    
    def _simple_search_prev(self, text_widget, search_text):
        """簡單的向前搜尋邏輯"""
        try:
            # 先清除之前的選取
            text_widget.tag_remove(tk.SEL, '1.0', tk.END)
            text_widget.tag_remove('search_highlight', '1.0', tk.END)
            
            # 設定搜尋高亮樣式
            text_widget.tag_configure('search_highlight', background='#FFFF00', foreground='#000000')
            
            # 獲取當前游標位置
            current_pos = text_widget.index(tk.INSERT)
            print(f"當前游標位置：{current_pos}")
            
            # 從當前位置向前搜尋（不包含當前位置）
            # 先將游標向前移動一個字符
            if current_pos != '1.0':
                prev_pos = text_widget.index(f"{current_pos}-1c")
                pos = text_widget.search(search_text, '1.0', prev_pos, nocase=True, backwards=True)
            else:
                # 如果已經在開頭，從末尾開始搜尋
                pos = text_widget.search(search_text, tk.END, '1.0', nocase=True, backwards=True)
            
            if pos:
                # 找到匹配項目
                end_pos = f"{pos}+{len(search_text)}c"
                text_widget.mark_set(tk.INSERT, pos)
                text_widget.see(pos)
                text_widget.tag_add(tk.SEL, pos, end_pos)
                text_widget.tag_add('search_highlight', pos, end_pos)
                print(f"找到上一個匹配項目：{pos}")
            else:
                print("未找到匹配項目")
                self._update_search_count(0)
                    
        except Exception as e:
            print(f"簡單搜尋上一個時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
    
    def _perform_search(self):
        """執行搜尋功能"""
        try:
            search_text = self.search_var.get().strip().lower()
            print(f"開始搜尋：'{search_text}'")
            
            if not search_text:
                self._clear_search()
                return
            
            # 檢查當前選中的標籤頁
            current_tab = self.notebook.select()
            print(f"當前標籤頁：{current_tab}")
            
            # 根據當前標籤頁決定搜尋範圍
            # 獲取當前選中的標籤頁索引
            current_tab_index = self.notebook.index(current_tab)
            print(f"當前標籤頁索引：{current_tab_index}")
            
            # 根據索引判斷標籤頁類型
            if current_tab_index == 0:  # PASS標籤頁
                print("在PASS標籤頁中搜尋...")
                if hasattr(self, 'pass_tree_enhanced'):
                    self._search_in_tree(self.pass_tree_enhanced, search_text)
                else:
                    print("未找到PASS tree")
            elif current_tab_index == 1:  # FAIL標籤頁
                print("在FAIL標籤頁中搜尋...")
                if hasattr(self, 'fail_tree_enhanced'):
                    self._search_in_tree(self.fail_tree_enhanced, search_text)
                else:
                    print("未找到FAIL tree")
            elif current_tab_index == 2:  # 原始LOG標籤頁
                print("在原始LOG標籤頁中搜尋...")
                if hasattr(self, 'log_text_enhanced') and hasattr(self.log_text_enhanced, 'text'):
                    self._search_in_text(self.log_text_enhanced.text, search_text)
                elif hasattr(self, 'raw_text'):
                    self._search_in_text(self.raw_text, search_text)
                else:
                    print("未找到原始LOG Text元件")
            else:
                print(f"未知標籤頁索引：{current_tab_index}，嘗試搜尋原始LOG...")
                if hasattr(self, 'log_text_enhanced') and hasattr(self.log_text_enhanced, 'text'):
                    self._search_in_text(self.log_text_enhanced.text, search_text)
                elif hasattr(self, 'raw_text'):
                    self._search_in_text(self.raw_text, search_text)
                
        except Exception as e:
            print(f"搜尋時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
    
    def _search_in_tree(self, tree_enhanced, search_text):
        """在TreeView中搜尋"""
        try:
            tree = tree_enhanced.tree
            # 清除之前的選取
            tree.selection_remove(tree.selection())
            
            # 搜尋匹配的項目
            matches = []
            for item in tree.get_children():
                values = tree.item(item, 'values')
                # 檢查所有欄位是否包含搜尋文字
                for value in values:
                    if search_text in str(value).lower():
                        matches.append(item)
                        break
            
            # 更新搜尋計數
            self._update_search_count(len(matches))
            
            if matches:
                # 選取第一個匹配項目並滾動到該位置
                tree.selection_set(matches[0])
                tree.focus(matches[0])
                tree.see(matches[0])
                
                # 高亮顯示所有匹配項目
                for match in matches:
                    tree.selection_add(match)
                
                print(f"找到 {len(matches)} 個匹配項目")
            else:
                print("未找到匹配項目")
                
        except Exception as e:
            print(f"TreeView搜尋時發生錯誤: {e}")
    
    def _search_in_text(self, text_widget, search_text):
        """在Text元件中搜尋 - 使用內建搜尋功能"""
        try:
            print(f"在Text元件中搜尋：'{search_text}'")
            
            # 檢查Text元件是否有內容
            content = text_widget.get('1.0', tk.END)
            print(f"Text內容長度：{len(content)}")
            
            if len(content) <= 1:  # 只有換行符
                print("Text元件為空，無法搜尋")
                self._update_search_count(0)
                return
            
            # 先清除之前的搜尋
            text_widget.tag_remove(tk.SEL, '1.0', tk.END)
            text_widget.tag_remove('search_highlight', '1.0', tk.END)
            
            # 設定搜尋高亮樣式
            text_widget.tag_configure('search_highlight', background='#FFFF00', foreground='#000000')
            
            # 計算總匹配數量
            count = 0
            pos = '1.0'
            while True:
                pos = text_widget.search(search_text, pos, tk.END, nocase=True)
                if not pos:
                    break
                count += 1
                end_pos = f"{pos}+{len(search_text)}c"
                text_widget.tag_add('search_highlight', pos, end_pos)
                pos = end_pos
            
            # 更新搜尋計數
            self._update_search_count(count)
            
            if count > 0:
                # 找到第一個匹配項目並滾動到該位置
                first_pos = text_widget.search(search_text, '1.0', tk.END, nocase=True)
                if first_pos:
                    end_pos = f"{first_pos}+{len(search_text)}c"
                    text_widget.mark_set(tk.INSERT, end_pos)
                    text_widget.see(first_pos)
                    text_widget.tag_add(tk.SEL, first_pos, end_pos)
                    print(f"找到 {count} 個匹配項目，第一個在：{first_pos}")
            else:
                print("未找到匹配項目")
                
        except Exception as e:
            print(f"Text搜尋時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
    
    def _clear_search(self):
        """清除搜尋結果"""
        try:
            # 清除搜尋框
            self.search_var.set("")
            
            # 清除PASS樹狀檢視的選取
            if hasattr(self, 'pass_tree_enhanced'):
                self.pass_tree_enhanced.tree.selection_remove(self.pass_tree_enhanced.tree.selection())
            
            # 清除FAIL樹狀檢視的選取
            if hasattr(self, 'fail_tree_enhanced'):
                self.fail_tree_enhanced.tree.selection_remove(self.fail_tree_enhanced.tree.selection())
            
            # 清除原始LOG的選取和高亮
            if hasattr(self, 'log_text_enhanced') and hasattr(self.log_text_enhanced, 'text'):
                self.log_text_enhanced.text.tag_remove(tk.SEL, '1.0', tk.END)
                self.log_text_enhanced.text.tag_remove('search_highlight', '1.0', tk.END)
                # 重置游標到開頭
                self.log_text_enhanced.text.mark_set(tk.INSERT, '1.0')
            elif hasattr(self, 'raw_text'):
                self.raw_text.tag_remove(tk.SEL, '1.0', tk.END)
                self.raw_text.tag_remove('search_highlight', '1.0', tk.END)
                # 重置游標到開頭
                self.raw_text.mark_set(tk.INSERT, '1.0')
            
            # 清除搜尋計數
            if hasattr(self, 'search_count_label'):
                self.search_count_label.config(text="")
            
            print("已清除搜尋結果")
            
        except Exception as e:
            print(f"清除搜尋時發生錯誤: {e}")
    
    def _update_search_count(self, count):
        """更新搜尋結果計數"""
        try:
            if hasattr(self, 'search_count_label'):
                if count > 0:
                    self.search_count_label.config(text=f"找到 {count} 個匹配項目", fg='#2196F3')
                else:
                    self.search_count_label.config(text="未找到匹配項目", fg='#F44336')
        except Exception as e:
            print(f"更新搜尋計數時發生錯誤: {e}")
    
    def _analyze_enhanced_log(self):
        """分析log檔案並更新增強版GUI顯示 (Entry Point)"""
        if not self.current_log_path:
            messagebox.showwarning("警告", "請先選擇log檔案或資料夾")
            return
            
        # 1. 準備UI：清空現有內容、顯示進度條
        self.pass_tree_enhanced.clear()
        self.fail_tree_enhanced.clear()
        self.log_text_enhanced.clear()

        filename = os.path.basename(self.current_log_path)
        self._show_progress("正在分析LOG檔案", f"準備分析: {filename}")
        
        # 2. 啟動背景執行緒進行Heavy Lifting
        import threading
        t = threading.Thread(target=self._run_analysis_background, daemon=True)
        t.start()

    def _run_analysis_background(self):
        """背景執行緒：執行耗時的解析工作"""
        try:
            if self.current_mode == 'single':
                self._bg_analyze_single()
            else:
                self._bg_analyze_multiple()
        except Exception as e:
            # 發生錯誤，回主執行緒報錯
            self.root.after(0, lambda: self._handle_analysis_error(e))

    def _handle_analysis_error(self, e):
        """回主執行緒顯示錯誤"""
        self._close_progress()
        messagebox.showerror("分析錯誤", f"分析過程中發生錯誤：\n{str(e)}")

    def _thread_safe_update_progress(self, msg, value=None, max_value=None):
        """執行緒安全的進度更新"""
        self.root.after(0, lambda: self._update_progress(msg))
        if value is not None and max_value is not None:
             self.root.after(0, lambda: self._progress_set_determinate(max_value))
             self.root.after(0, lambda: self._progress_set_value(value, max_value))

    def _bg_analyze_single(self):
        """背景：單檔分析"""
        self._thread_safe_update_progress("正在解析LOG檔案內容...")
        
        # Heavy Parsing
        result = self.log_parser.parse_log_file(self.current_log_path)
        
        # Parsing Done, Schedule UI Update on Main Thread
        self.root.after(0, lambda: self._ui_render_single(result))

    def _ui_render_single(self, result):
        """主執行緒：渲染單檔結果"""
        try:
            pass_items = result['pass_items']
            fail_items = result['fail_items']
            raw_lines = result['raw_lines']
            fail_line_idx = result['fail_line_idx']

            self._update_progress(f"處理PASS項目 ({len(pass_items)} 個)...")
            for idx, item in enumerate(pass_items, 1):
                full_response = item.get('full_response', '')
                has_retry = item.get('has_retry_but_pass', False)
                self.pass_tree_enhanced.insert_pass_item(
                    (item['step_name'], item['command'], item['response'], item['result']),
                    step_number=idx,
                    full_response=full_response,
                    has_retry=has_retry
                )

            self._update_progress(f"處理FAIL項目 ({len(fail_items)} 個)...")
            for item in fail_items:
                is_main_fail = item.get('is_main_fail', False)
                full_response = item.get('full_response', '')
                self.fail_tree_enhanced.insert_fail_item(
                    (item['step_name'], item['command'], item['response'], item['retry'], item['error']),
                    full_response=full_response,
                    is_main_fail=is_main_fail
                )

            self._update_progress("處理原始LOG內容...")
            if raw_lines:
                log_content = '\n'.join(raw_lines)
                self.log_text_enhanced.insert_log_with_highlighting(log_content, {
                    'fail_line_idx': fail_line_idx,
                    'pass_items': pass_items,
                    'fail_items': fail_items
                })
                if fail_line_idx is not None and fail_line_idx < len(raw_lines):
                    self.log_text_enhanced.highlight_error_block(fail_line_idx + 1, fail_line_idx + 1)
                    self.log_text_enhanced.text.see(f"{fail_line_idx + 1}.0")

            self._update_progress("分析完成！")
            
            if fail_items:
                self.notebook.select(self.tab_fail)
                self.root.after(2000, self._switch_to_log_and_focus_error)
            else:
                self.notebook.select(self.tab_pass)
            
            self._update_tab_visibility(pass_items, fail_items)
            
        except Exception as e:
            self._handle_analysis_error(e)
        finally:
            self.root.after(100, self._close_progress)

    def _bg_analyze_multiple(self):
        """背景：多檔資料夾分析"""
        folder = self.current_log_path
        
        # 1. Scan files
        log_files = []
        for root, dirs, files in os.walk(folder):
            for fn in files:
                if fn.lower().endswith('.log'):
                    log_files.append(os.path.join(root, fn))
        
        total_files = len(log_files)
        self._thread_safe_update_progress(f"準備分析 {total_files} 個LOG檔案...", 0, total_files)
        
        try:
            # 預覽 (Optional: call back to main thread or skip)
            # self.root.after(0, lambda: self._show_log_file_preview(folder))
            pass 
        except: 
            pass

        pass_logs = []
        fail_logs = []
        
        # 2. Iterate & Parse
        for i, path in enumerate(log_files, 1):
            fn = os.path.basename(path)
            self._thread_safe_update_progress(f"分析檔案 {i}/{total_files}: {fn}", i, total_files)
            
            res = self.log_parser.parse_log_file(path)
            
            # Pack data
            entry = {
                'file_path': path,
                'file_name': fn,
                'raw_lines': res.get('raw_lines') or [],
                'ui_annotations': res.get('ui_annotations') or [],
                'pass_items': res.get('pass_items') or [],
                'fail_items': res.get('fail_items') or [],
                'summary': self._extract_file_summary(res, path),
                'step_marks': self._build_step_marks(res.get('raw_lines') or [])
            }
            
            if 'PASS' in fn.upper():
                pass_logs.append(entry)
            else:
                if res.get('fail_items'):
                    main_error = self._extract_main_fail_reason_from_items(res['fail_items'])
                    entry['summary']['FAIL原因'] = main_error
                fail_logs.append(entry)
        
        # All parsed. Send to UI.
        self.root.after(0, lambda: self._ui_render_multiple(pass_logs, fail_logs, total_files, folder))

    def _ui_render_multiple(self, pass_logs, fail_logs, total_files, folder):
        """主執行緒：渲染多檔結果 & 匯出 Excel"""
        try:
            self._display_folder_analysis_preview(pass_logs, fail_logs)

            # 更新 TreeViews for preview (aggregated)
            for idx, entry in enumerate(pass_logs, 1):
                for j, item in enumerate(entry['pass_items'], 1):
                    self.pass_tree_enhanced.insert_pass_item(
                        (item['step_name'], item['command'], item['response'], item['result']),
                        step_number=j,
                        full_response=item.get('full_response', ''),
                        has_retry=item.get('has_retry_but_pass', False)
                    )
            for entry in fail_logs:
                for item in entry['fail_items']:
                    self.fail_tree_enhanced.insert_fail_item(
                        (item['step_name'], item['command'], item['response'], item['retry'], item['error']),
                        full_response=item.get('full_response', ''),
                        is_main_fail=item.get('is_main_fail', False)
                    )
            
            # Raw LOG merging
            if fail_logs:
                all_raw_lines = []
                all_fail_items = []
                all_pass_items = []
                for entry in fail_logs:
                    all_raw_lines.extend(entry.get('raw_lines', []))
                    all_fail_items.extend(entry.get('fail_items', []))
                    all_pass_items.extend(entry.get('pass_items', []))
                
                if all_raw_lines:
                    log_content = '\n'.join(all_raw_lines)
                    self.log_text_enhanced.insert_log_with_highlighting(log_content, {
                        'fail_line_idx': None,
                        'pass_items': all_pass_items,
                        'fail_items': all_fail_items
                    })
                self.notebook.select(self.tab_log)

            # Export Excel
            try:
                out_dir = build_output_dir(folder, 'LOG集總整理')
                pass_path, fail_path = self.excel_writer.export_pass_fail_workbooks(out_dir, pass_logs, fail_logs)
                
                # Clear Trees after export (as per original logic for multi-file)
                self.pass_tree_enhanced.clear()
                self.fail_tree_enhanced.clear()
                
                self._show_open_folder_prompt(out_dir, total_files, len(pass_logs), len(fail_logs), pass_path, fail_path)
            except Exception as e:
                messagebox.showerror("匯出失敗", f"產生Excel時發生錯誤：\n{e}")

        except Exception as e:
            self._handle_analysis_error(e)
        finally:
            self.root.after(100, self._close_progress)

    # 為了保持兼容性，原有的單檔/多檔入口如果被其他地方調用，可以保留或作廢。
    # 上面的 _analyze_enhanced_log 已經取代了它們的調用邏輯。
    # 以下兩個僅保留空殼或改名以避免誤用，或者直接移除。
    # 這裡選擇直接移除舊方法內容，避免重複代碼。


    def _display_folder_analysis_preview(self, pass_logs, fail_logs):
        """在左側視窗顯示資料夾分析預覽"""
        try:
            preview_text = "=== 資料夾分析預覽 ===\n\n"
            
            # 顯示 PASS 檔案
            if pass_logs:
                preview_text += "✅ PASS 檔案:\n"
                for entry in pass_logs:
                    preview_text += f"  • {entry['file_name']}\n"
                preview_text += "\n"
            
            # 顯示 FAIL 檔案與主要錯誤原因
            if fail_logs:
                preview_text += "❌ FAIL 檔案與主要錯誤原因:\n"
                for entry in fail_logs:
                    filename = entry['file_name']
                    main_error = entry['summary'].get('FAIL原因', '未知錯誤')
                    preview_text += f"  📄 {filename}\n"
                    
                    # 突出顯示錯誤原因
                    if "doesn't match" in main_error.lower():
                        preview_text += f"     🔴 主要錯誤: {main_error}\n"
                    else:
                        preview_text += f"     ⚠️  主要錯誤: {main_error}\n"
                    preview_text += "\n"
            
            # 統計資訊
            preview_text += f"📊 統計:\n"
            preview_text += f"  PASS: {len(pass_logs)} 個檔案\n"
            preview_text += f"  FAIL: {len(fail_logs)} 個檔案\n"
            preview_text += f"  總計: {len(pass_logs) + len(fail_logs)} 個檔案\n"
            
            # 在左側面板顯示
            if hasattr(self, 'file_info_label'):
                self.file_info_label.config(text=preview_text, justify='left', wraplength=250)
            
        except Exception as e:
            print(f"顯示資料夾分析預覽失敗: {e}")

    def _extract_main_fail_reason_from_items(self, fail_items):
        """從FAIL項目列表中提取主要錯誤原因"""
        if not fail_items:
            return "未知錯誤"
        
        # 優先找到包含 "is Fail" 的項目
        for item in fail_items:
            full_response = item.get('full_response', '')
            if full_response:
                lines = full_response.split('\n')
                for line in lines:
                    # 移除行號前綴（如 "370. "）
                    clean_line = line
                    if '. ' in line and line.split('. ', 1)[0].strip().isdigit():
                        clean_line = line.split('. ', 1)[1]
                    
                    # 找到包含 "is Fail" 的行
                    if "is Fail" in clean_line:
                        # 處理類似 "VSCH026-043:Chec Frimware version is Fail ! <ErrorCode: BSFR18>" 的格式
                        if ':' in clean_line and "is Fail" in clean_line:
                            # 擷取冒號後的部分
                            after_colon = clean_line.split(":", 1)[1].strip()
                            # 找到 "is Fail" 的位置
                            if "is Fail" in after_colon:
                                fail_pos = after_colon.find("is Fail")
                                # 擷取到 "is Fail" 結束的部分，去掉後面的 <ErrorCode: xxx> 和時間戳記
                                test_name_with_fail = after_colon[:fail_pos + 7].strip()  # 7 = len("is Fail")
                                
                                # 移除時間戳記（如 "2025/08/07 08:53:36 [1]" 格式）
                                if '[' in test_name_with_fail and ']' in test_name_with_fail:
                                    bracket_start = test_name_with_fail.find('[')
                                    bracket_end = test_name_with_fail.find(']')
                                    if bracket_start != -1 and bracket_end != -1:
                                        # 檢查括號前是否有時間戳記格式
                                        before_bracket = test_name_with_fail[:bracket_start].strip()
                                        if '/' in before_bracket and ':' in before_bracket:
                                            # 移除時間戳記部分
                                            test_name_with_fail = test_name_with_fail[bracket_end + 1:].strip()
                                
                                return test_name_with_fail
                        elif "is Fail" in clean_line:
                            # 如果沒有冒號但有 "is Fail"，直接擷取到 "is Fail" 結束
                            fail_pos = clean_line.find("is Fail")
                            if fail_pos != -1:
                                # 找到 <ErrorCode: 的位置
                                error_code_pos = clean_line.find("<ErrorCode:")
                                if error_code_pos != -1:
                                    return clean_line[:error_code_pos].strip()
                                else:
                                    return clean_line[:fail_pos + 7].strip()
        
        # 如果沒有找到 "is Fail"，嘗試找到其他錯誤資訊
        for item in fail_items:
            full_response = item.get('full_response', '')
            if full_response:
                lines = full_response.split('\n')
                for line in lines:
                    clean_line = line
                    if '. ' in line and line.split('. ', 1)[0].strip().isdigit():
                        clean_line = line.split('. ', 1)[1]
                    
                    # 尋找包含 "All Test Aborted" 的行
                    if "All Test Aborted" in clean_line:
                        return clean_line
                    
                    # 尋找其他嚴重錯誤
                    line_lower = clean_line.lower()
                    if any(critical_error in line_lower for critical_error in [
                        'segmentation fault', 'core dumped', 'executes fail', 
                        "doesn't match", 'timeout', 'exception'
                    ]):
                        return clean_line
        
        # 如果都沒有找到，返回第一個項目的錯誤信息
        return fail_items[0].get('error', '未知錯誤')

    def _extract_file_summary(self, parse_result: dict, file_path: str) -> dict:
        """從檔名或檔案內容提取測試日期時間、SFIS狀態、測試總時間、主要FAIL原因（若有）"""
        name = os.path.basename(file_path)
        # 從檔名猜測日期時間（yyyyMMddHHmmss）
        import re
        dt = ''
        m = re.search(r'(20\d{12})', name)
        if m:
            s = m.group(1)
            try:
                dt = f"{s[0:4]}-{s[4:6]}-{s[6:8]} {s[8:10]}:{s[10:12]}:{s[12:14]}"
            except Exception:
                dt = ''
        # SFIS 狀態：簡單從內容找 ON/OFF 關鍵詞
        raw_lines = parse_result.get('raw_lines') or []
        sfis = ''
        for line in raw_lines[:200]:  # 前200行掃描
            if 'SFIS' in line.upper():
                if 'ON' in line.upper():
                    sfis = 'ON'
                    break
                if 'OFF' in line.upper():
                    sfis = 'OFF'
                    break
        # 測試總時間：從最後 200 行抓取 pattern 例如 "TestTime: 00:05:32" 或 "Total time: 12.3s"
        total_time = ''
        for line in (raw_lines[-200:] if raw_lines else []):
            if 'TestTime' in line or 'Total time' in line or '總時間' in line:
                total_time = line.strip()
                break
        return {
            '測試日期時間': dt,
            'SFIS': sfis,
            '測試總時間': total_time,
        }

    def _build_step_marks(self, raw_lines: list) -> dict:
        """建立步驟起始行的標號對照，key 為 raw_lines 索引，value 為 1..n"""
        marks = {}
        import re
        step_re = re.compile(r'Do\s+@STEP\d+@')
        count = 0
        for idx, line in enumerate(raw_lines):
            if step_re.search(line):
                count += 1
                marks[idx] = count
        return marks
    
    def _set_fail_pane_position(self, position):
        """設定FAIL分割視窗位置"""
        try:
            if hasattr(self, 'fail_paned'):
                self.fail_paned.sash_place(0, 0, position)
        except Exception as e:
            print(f"設定FAIL分割視窗位置失敗: {e}")
    
    def _on_fail_pane_adjust(self, event):
        """處理FAIL分割視窗調整事件"""
        try:
            if hasattr(self, 'fail_paned'):
                position = self.fail_paned.sash_coord(0)[1]
                self.settings['fail_pane_position'] = position
                save_settings(self.settings)
        except Exception as e:
            print(f"保存FAIL分割視窗位置失敗: {e}")
    
    def _auto_select_first_fail(self):
        """自動選擇第一個FAIL項目並顯示FAIL原因"""
        try:
            if hasattr(self, 'fail_tree_enhanced'):
                children = self.fail_tree_enhanced.tree.get_children()
                if children:
                    first_item = children[0]
                    self.fail_tree_enhanced.tree.selection_set(first_item)
                    # 自動觸發選擇事件，顯示FAIL原因
                    self._on_fail_item_select(None)
        except Exception as e:
            print(f"自動選擇第一個FAIL項目失敗: {e}")
    
    def _auto_display_fail_reason(self):
        """自動顯示FAIL錯誤原因（不需要點擊）"""
        try:
            if hasattr(self, 'fail_tree_enhanced') and self.fail_tree_enhanced.tree:
                items = self.fail_tree_enhanced.tree.get_children()
                if items:
                    # 自動選擇第一個項目並顯示錯誤原因
                    first_item = items[0]
                    self.fail_tree_enhanced.tree.selection_set(first_item)
                    self.fail_tree_enhanced.tree.see(first_item)
                    
                    # 直接顯示錯誤原因，不需要點擊
                    self._display_fail_reason_for_item(first_item)
        except Exception as e:
            print(f"自動顯示FAIL錯誤原因失敗: {e}")
    
    def _display_fail_reason_for_item(self, item_id):
        """為指定項目顯示FAIL錯誤原因"""
        try:
            values = self.fail_tree_enhanced.tree.item(item_id, 'values')
            
            if values:
                step_name = values[0]
                error_code = values[4] if len(values) > 4 else "未知錯誤"
                
                # 從存儲中獲取完整內容
                full_content = self.fail_tree_enhanced.full_content_storage.get(item_id, '')
                
                # 提取主要的FAIL原因作為大字體標題
                main_error = self._extract_main_fail_reason(full_content)
                
                # 顯示大字體紅色文字白底
                self.fail_error_title.config(text=main_error, 
                                            font=('Arial', 20, 'bold'), fg='red', bg='white')
                
                # 提取FAIL原因部分顯示在下方
                fail_reason_content = self._extract_fail_reason(full_content)
                
                # 更新錯誤內容
                self.fail_error_text.config(state=tk.NORMAL)
                self.fail_error_text.delete('1.0', tk.END)
                self._insert_formatted_fail_content(fail_reason_content)
                self.fail_error_text.config(state=tk.NORMAL)
            else:
                self.fail_error_title.config(text="無詳細錯誤資訊")
                self.fail_error_text.config(state=tk.NORMAL)
                self.fail_error_text.delete('1.0', tk.END)
                self.fail_error_text.insert('1.0', "沒有詳細錯誤內容可顯示")
                self.fail_error_text.config(state=tk.NORMAL)
        except Exception as e:
            print(f"顯示FAIL錯誤原因失敗: {e}")
    
    def _on_fail_item_select(self, event):
        """處理FAIL項目選擇事件"""
        try:
            selection = self.fail_tree_enhanced.tree.selection()
            if selection:
                item_id = selection[0]
                values = self.fail_tree_enhanced.tree.item(item_id, 'values')
                
                if values:
                    step_name = values[0]
                    error_code = values[4] if len(values) > 4 else "未知錯誤"
                    
                    # 從存儲中獲取完整內容，優先找到包含 "is Fail" 的行作為標題
                    full_content = self.fail_tree_enhanced.full_content_storage.get(item_id, '')
                    
                    # 優先從完整內容中找到包含 "is Fail" 的行作為大字體標題
                    main_error = self._extract_main_fail_reason(full_content)
                    
                    # 顯示大字體紅色文字白底
                    self.fail_error_title.config(text=main_error, 
                                                font=('Arial', 20, 'bold'), fg='red', bg='white')
                    
                    # 提取FAIL原因部分顯示在下方
                    fail_reason_content = self._extract_fail_reason(full_content)
                    
                    # 更新錯誤內容
                    self.fail_error_text.config(state=tk.NORMAL)
                    self.fail_error_text.delete('1.0', tk.END)
                    self._insert_formatted_fail_content(fail_reason_content)
                    self.fail_error_text.config(state=tk.NORMAL)
                else:
                    self.fail_error_title.config(text="無詳細錯誤資訊")
                    self.fail_error_text.config(state=tk.NORMAL)
                    self.fail_error_text.delete('1.0', tk.END)
                    self.fail_error_text.insert('1.0', "沒有詳細錯誤內容可顯示")
                    self.fail_error_text.config(state=tk.NORMAL)
        except Exception as e:
            print(f"處理FAIL項目選擇失敗: {e}")
    
    def _extract_fail_reason(self, full_content):
        """提取FAIL原因部分，包含更多錯誤關鍵字"""
        if not full_content:
            return "沒有詳細錯誤內容可顯示"
        
        lines = full_content.split('\n')
        fail_reason_lines = []
        is_fail_lines = []
        
        # 優先找到包含 "is Fail" 的行
        for line in lines:
            # 移除行號前綴（如 "370. "）
            clean_line = line
            if '. ' in line and line.split('. ', 1)[0].strip().isdigit():
                clean_line = line.split('. ', 1)[1]
            
            # 優先提取包含 "is Fail" 的行
            if "is Fail" in clean_line:
                is_fail_lines.append(clean_line)
            # 其他包含重要錯誤資訊的行，使用統一的錯誤關鍵字
            elif self._is_error_line(clean_line):
                fail_reason_lines.append(clean_line)
        
        # 優先顯示包含 "is Fail" 的行，然後是其他錯誤資訊
        result_lines = is_fail_lines + fail_reason_lines
        return '\n'.join(result_lines) if result_lines else full_content
    
    def _extract_main_fail_reason(self, full_content):
        """提取主要的FAIL原因作為大字體標題"""
        if not full_content:
            return "無詳細錯誤資訊"
        
        lines = full_content.split('\n')
        
        # 優先找到包含 "is Fail" 的行
        for line in lines:
            # 移除行號前綴（如 "370. "）
            clean_line = line
            if '. ' in line and line.split('. ', 1)[0].strip().isdigit():
                clean_line = line.split('. ', 1)[1]
            
            # 找到包含 "is Fail" 的行
            if "is Fail" in clean_line:
                # 處理類似 "VSCH026-043:Chec Frimware version is Fail ! <ErrorCode: BSFR18>" 的格式
                if ':' in clean_line and "is Fail" in clean_line:
                    # 擷取冒號後的部分
                    after_colon = clean_line.split(":", 1)[1].strip()
                    # 找到 "is Fail" 的位置
                    if "is Fail" in after_colon:
                        fail_pos = after_colon.find("is Fail")
                        # 擷取到 "is Fail" 結束的部分，去掉後面的 <ErrorCode: xxx> 和時間戳記
                        test_name_with_fail = after_colon[:fail_pos + 7].strip()  # 7 = len("is Fail")
                        
                        # 移除時間戳記（如 "2025/08/07 08:53:36 [1]" 格式）
                        if '[' in test_name_with_fail and ']' in test_name_with_fail:
                            bracket_start = test_name_with_fail.find('[')
                            bracket_end = test_name_with_fail.find(']')
                            if bracket_start != -1 and bracket_end != -1:
                                # 檢查括號前是否有時間戳記格式
                                before_bracket = test_name_with_fail[:bracket_start].strip()
                                if '/' in before_bracket and ':' in before_bracket:
                                    # 移除時間戳記部分
                                    test_name_with_fail = test_name_with_fail[bracket_end + 1:].strip()
                        
                        return test_name_with_fail
                elif "is Fail" in clean_line:
                    # 如果沒有冒號但有 "is Fail"，直接擷取到 "is Fail" 結束
                    fail_pos = clean_line.find("is Fail")
                    if fail_pos != -1:
                        # 找到 <ErrorCode: 的位置
                        error_code_pos = clean_line.find("<ErrorCode:")
                        if error_code_pos != -1:
                            return clean_line[:error_code_pos].strip()
                        else:
                            return clean_line[:fail_pos + 7].strip()
        
        # 如果沒有找到 "is Fail"，嘗試找到其他錯誤資訊
        for line in lines:
            clean_line = line
            if '. ' in line and line.split('. ', 1)[0].strip().isdigit():
                clean_line = line.split('. ', 1)[1]
            
            # 尋找包含 "All Test Aborted" 的行
            if "All Test Aborted" in clean_line:
                return clean_line
        
        return "未知錯誤"
    
    def _is_error_line(self, line):
        """統一的錯誤行識別邏輯"""
        if not line:
            return False
        
        line_lower = line.lower()
        # 統一的錯誤關鍵字列表
        error_keywords = [
            'Result:', 'validation:', 'type of', 'TestTime:', 
            'ErrorCode:', 'Test Completed', 'Test Aborted', 'TotalCount:', 
            'Report name:', 'Execute Phase', 'FAIL', 'ERROR', 'NACK',
            'fail', 'error', 'wrong', 'segmentation fault', 'core dumped',
            'executes fail', "doesn't match", 'timeout', 'exception'
        ]
        
        return any(keyword in line_lower for keyword in error_keywords)
    
    def _switch_to_log_and_focus_error(self):
        """切換到原始LOG標籤頁並聚焦到錯誤位置"""
        try:
            # 切換到原始LOG標籤頁
            self.notebook.select(self.tab_log)
            
            # 尋找第一個錯誤行並聚焦
            if hasattr(self, 'log_text_enhanced') and self.log_text_enhanced:
                self.log_text_enhanced.focus_first_error_line()
        except Exception as e:
            print(f"切換到LOG標籤頁並聚焦錯誤失敗: {e}")
    
    def _insert_formatted_fail_content(self, content):
        """插入格式化的FAIL內容，顯示所有錯誤"""
        # 先插入標題
        self.fail_error_text.insert(tk.END, "===============錯誤原因====================\n", 'error_title')
        
        lines = content.split('\n')
        error_lines = []
        doesnt_match_lines = []
        
        # 收集所有錯誤行，特別標記 "doesn't match"
        for line in lines:
            line_lower = line.lower()
            
            # 檢查不同類型的錯誤
            if ("is Fail" in line or 
                any(critical_error in line_lower for critical_error in [
                    'segmentation fault', 'core dumped', 'executes fail', 
                    "doesn't match", 'timeout', 'exception'
                ]) or
                any(error_keyword in line_lower for error_keyword in [
                    'error', 'fail', 'wrong'
                ]) or
                any(keyword in line_lower for keyword in [
                    'errorcode:', 'test aborted', 'all test aborted'
                ])):
                error_lines.append(line)
                
                # 特別標記 "doesn't match" 相關行
                if "doesn't match" in line_lower:
                    doesnt_match_lines.append(line)
        
        # 優先顯示 "doesn't match" 錯誤
        if doesnt_match_lines:
            self.fail_error_text.insert(tk.END, "\n🔴 突出錯誤 (doesn't match):\n", 'highlight_title')
            for line in doesnt_match_lines:
                self.fail_error_text.insert(tk.END, line + '\n', 'doesnt_match_error')
            self.fail_error_text.insert(tk.END, "\n" + "=" * 50 + "\n\n", 'separator')
        
        # 顯示所有其他錯誤行
        for line in error_lines:
            if line not in doesnt_match_lines:  # 避免重複顯示
                line_lower = line.lower()
                
                # 檢查不同類型的錯誤並用不同顏色標記
                if "is Fail" in line:
                    # 主要錯誤：紅色粗體
                    self.fail_error_text.insert(tk.END, line + '\n', 'fail_red')
                elif any(critical_error in line_lower for critical_error in [
                    'segmentation fault', 'core dumped', 'executes fail', 
                    'timeout', 'exception'
                ]):
                    # 嚴重錯誤：深紅色粗體
                    self.fail_error_text.insert(tk.END, line + '\n', 'critical_error')
                elif any(error_keyword in line_lower for error_keyword in [
                    'error', 'fail', 'wrong'
                ]) and not "is Fail" in line:
                    # 一般錯誤關鍵字：橙紅色
                    self.fail_error_text.insert(tk.END, line + '\n', 'error_keyword')
                elif any(keyword in line_lower for keyword in [
                    'errorcode:', 'test aborted', 'all test aborted'
                ]):
                    # 錯誤代碼：橙色
                    self.fail_error_text.insert(tk.END, line + '\n', 'error_code')
                else:
                    # 其他錯誤：紅色
                    self.fail_error_text.insert(tk.END, line + '\n', 'fail_red')
        
        # 設定不同的文字標籤樣式
        self.fail_error_text.tag_configure('error_title', foreground='red', font=('Arial', 14, 'bold'))
        self.fail_error_text.tag_configure('highlight_title', foreground='darkred', font=('Arial', 12, 'bold'))
        self.fail_error_text.tag_configure('doesnt_match_error', foreground='darkred', font=('Consolas', 12, 'bold'), background='#FFE6E6')
        self.fail_error_text.tag_configure('separator', foreground='gray', font=('Consolas', 10))
        self.fail_error_text.tag_configure('fail_red', foreground='red', font=('Consolas', 12, 'bold'))
        self.fail_error_text.tag_configure('critical_error', foreground='darkred', font=('Consolas', 12, 'bold'))
        self.fail_error_text.tag_configure('error_keyword', foreground='orangered', font=('Consolas', 11, 'bold'))
        self.fail_error_text.tag_configure('error_code', foreground='darkorange', font=('Consolas', 11, 'bold'))
    
    def _apply_font_size(self):
        """套用字體大小"""
        # 更新介面文字大小
        self.font_scaler.set_font_size(self.ui_font_size)
        
        # 更新左側面板中的字體大小標籤
        if hasattr(self, 'ui_font_size_label'):
            self.ui_font_size_label.config(text=str(self.ui_font_size), font=('Arial', self.ui_font_size))
        
        if hasattr(self, 'content_font_size_label'):
            self.content_font_size_label.config(text=str(self.content_font_size), font=('Arial', self.content_font_size))
        # 檔案名稱顯示應跟隨內容字體大小
        if hasattr(self, 'file_info_label'):
            try:
                self.file_info_label.configure(font=('Arial', self.content_font_size))
            except Exception:
                pass
        
        # 更新設定標籤頁中的字體大小標籤
        if hasattr(self, 'settings_ui_font_size_label'):
            self.settings_ui_font_size_label.config(text=str(self.ui_font_size), font=('Arial', self.ui_font_size))
        
        if hasattr(self, 'settings_content_font_size_label'):
            self.settings_content_font_size_label.config(text=str(self.content_font_size), font=('Arial', self.content_font_size))
        
        # 更新設定頁面中所有元件的字體大小
        self._apply_settings_page_fonts()
        
        # 更新標籤頁名稱字體（介面文字控制）
        style = ttk.Style()
        style.configure('TNotebook.Tab', font=('Arial', self.ui_font_size))
        # 重新設定標籤頁懸停效果
        style.map('TNotebook.Tab', background=[('active', '#00FF00')], foreground=[('active', 'black')])
        
        # 更新增強型元件的內容字體（內容字體控制）
        if hasattr(self, 'log_text_enhanced'):
            self.log_text_enhanced.text.configure(font=('Consolas', self.content_font_size))
        
        # 更新TreeView內容字體（內容字體控制）
        if hasattr(self, 'pass_tree_enhanced'):
            self._apply_treeview_font(self.pass_tree_enhanced.tree)
        if hasattr(self, 'fail_tree_enhanced'):
            self._apply_treeview_font(self.fail_tree_enhanced.tree)
        
        # 更新匯總 Summary Tree 字體
        if hasattr(self, 'pass_summary_tree'):
            style = ttk.Style()
            style.configure('Treeview', font=('Arial', self.content_font_size))
            style.configure('Treeview.Heading', font=('Arial', self.content_font_size, 'bold'))
        
        # 更新錯誤詳情面板內容字體
        if hasattr(self, 'fail_details'):
            self.fail_details.error_text.configure(font=('Consolas', self.content_font_size))
        
        # 更新FAIL錯誤顯示區域字體
        if hasattr(self, 'fail_error_text'):
            self.fail_error_text.configure(font=('Consolas', self.content_font_size))
        if hasattr(self, 'fail_error_title'):
            self.fail_error_title.configure(font=('Arial', self.ui_font_size + 4, 'bold'))
        
        # 更新TreeView展開視窗的內容字體
        if hasattr(self, 'pass_tree_enhanced'):
            try:
                self.pass_tree_enhanced.set_font_size(self.content_font_size)
            except Exception:
                pass
        if hasattr(self, 'fail_tree_enhanced'):
            try:
                self.fail_tree_enhanced.set_font_size(self.content_font_size)
            except Exception:
                pass

    def _apply_settings_page_fonts(self):
        """更新設定頁面中所有元件的字體大小"""
        try:
            if not hasattr(self, 'settings_frame'):
                return
                
            # 遞迴更新所有元件的字體
            def update_widget_font(widget):
                """遞迴更新元件的字體大小"""
                try:
                    # 根據元件的標識符更新字體
                    if hasattr(widget, '_is_settings_title'):
                        # 設定頁面標題（介面文字控制）
                        widget.config(font=('Arial', self.ui_font_size + 4, 'bold'))
                    elif hasattr(widget, '_is_settings_label'):
                        # 設定標籤（介面文字控制）
                        widget.config(font=('Arial', self.ui_font_size))
                    elif hasattr(widget, '_is_settings_button'):
                        # 設定按鈕（介面文字控制）
                        widget.config(font=('Arial', self.ui_font_size))
                    elif hasattr(widget, '_is_settings_checkbutton'):
                        # 設定核取方塊（介面文字控制）
                        widget.config(font=('Arial', self.ui_font_size))
                    elif hasattr(widget, '_is_settings_entry'):
                        # 設定輸入框（介面文字控制）
                        widget.config(font=('Arial', self.ui_font_size))
                    elif hasattr(widget, '_is_info_label'):
                        # 說明文字（內容字體控制）
                        widget.config(font=('Arial', self.content_font_size))
                    elif hasattr(widget, '_is_font_size_label'):
                        # 字體大小標籤（保持原樣，不更新）
                        pass
                    elif isinstance(widget, tk.LabelFrame):
                        # LabelFrame 標題（介面文字控制）
                        widget.config(font=('Arial', self.ui_font_size))
                    elif isinstance(widget, tk.Label) and not hasattr(widget, '_is_font_size_label') and not hasattr(widget, '_is_info_label'):
                        # 一般標籤（介面文字控制）
                        widget.config(font=('Arial', self.ui_font_size))
                    elif isinstance(widget, tk.Button):
                        # 一般按鈕（介面文字控制）
                        widget.config(font=('Arial', self.ui_font_size))
                    elif isinstance(widget, tk.Checkbutton):
                        # 一般核取方塊（介面文字控制）
                        widget.config(font=('Arial', self.ui_font_size))
                    elif isinstance(widget, tk.Entry):
                        # 一般輸入框（介面文字控制）
                        widget.config(font=('Arial', self.ui_font_size))
                    
                    # 遞迴處理子元件
                    for child in widget.winfo_children():
                        update_widget_font(child)
                        
                except Exception as e:
                    print(f"更新元件字體時發生錯誤: {e}")
            
            # 從根元件開始遞迴更新
            update_widget_font(self.settings_frame)
            
        except Exception as e:
            print(f"更新設定頁面字體時發生錯誤: {e}")
    
    def _apply_treeview_font(self, treeview):
        """套用TreeView字體"""
        # 同步展開視窗內容字體
        if hasattr(self, 'pass_tree_enhanced'):
            try:
                self.pass_tree_enhanced.set_font_size(self.content_font_size)
            except Exception:
                pass
        if hasattr(self, 'fail_tree_enhanced'):
            try:
                self.fail_tree_enhanced.set_font_size(self.content_font_size)
            except Exception:
                pass
    
    def _save_settings_silent(self):
        """無聲儲存設定（不顯示確認視窗）"""
        self.settings['ui_font_size'] = self.ui_font_size
        self.settings['content_font_size'] = self.content_font_size
        if hasattr(self, 'gui_header_var'):
            self.settings['gui_header'] = self.gui_header_var.get().strip() or 'ONLY FOR CENTIMANIA LOG'
        # 保存面板寬度
        if hasattr(self, 'left_frame'):
            left_width = self.left_frame.winfo_width()
            if left_width > 0:
                self.settings['pane_width'] = left_width
        # 保存視窗大小
        self.settings['window_width'] = self.root.winfo_width()
        self.settings['window_height'] = self.root.winfo_height()
        
        save_settings(self.settings)
    
    def _save_settings(self):
        """儲存設定並即時顯示（顯示確認視窗）"""
        self.settings['ui_font_size'] = self.ui_font_size
        self.settings['content_font_size'] = self.content_font_size
        # 保存面板寬度
        if hasattr(self, 'left_frame'):
            left_width = self.left_frame.winfo_width()
            if left_width > 0:
                self.settings['pane_width'] = left_width
        # 保存視窗大小
        self.settings['window_width'] = self.root.winfo_width()
        self.settings['window_height'] = self.root.winfo_height()
        # 保存其他設定
        if hasattr(self, 'auto_analyze_var'):
            self.settings['auto_analyze'] = self.auto_analyze_var.get()
        if hasattr(self, 'remember_path_var'):
            self.settings['remember_path'] = self.remember_path_var.get()
        
        # 保存標題
        if hasattr(self, 'app_title_var'):
            self.settings['app_title'] = self.app_title_var.get().strip() or 'PEGA test log Aanlyser'
        if hasattr(self, 'gui_header_var'):
            self.settings['gui_header'] = self.gui_header_var.get().strip() or 'ONLY FOR CENTIMANIA LOG'
        # 保存版本號碼
        if hasattr(self, 'version_var'):
            self.settings['version'] = self.version_var.get().strip() or 'V1.5.6'
        
        save_settings(self.settings)
        
        # 立即套用所有設定變更
        try:
            # 套用標題和版本號碼
            app_title = self.settings['app_title']
            version = self.settings.get('version', 'V1.5.6')
            self.root.title(f"{app_title} {version}")
            
            # 套用左側標題
            if hasattr(self, 'left_title_label'):
                self.left_title_label.config(text=self.settings['gui_header'])
            
            # 套用字體大小到所有元件
            self._apply_font_size()
            
            # 套用左側面板寬度
            if hasattr(self, 'paned_window') and 'pane_width' in self.settings:
                target_width = self.settings['pane_width']
                current_width = self.paned_window.sashpos(0)
                if abs(current_width - target_width) > 5:  # 如果差異超過5px才調整
                    self.paned_window.sashpos(0, target_width)
                    if hasattr(self, 'pane_width_label'):
                        self.pane_width_label.config(text=f"{target_width}px")
            
            # 更新設定頁面的字體大小標籤
            if hasattr(self, 'settings_ui_font_size_label'):
                self.settings_ui_font_size_label.config(text=str(self.ui_font_size))
            if hasattr(self, 'settings_content_font_size_label'):
                self.settings_content_font_size_label.config(text=str(self.content_font_size))
                
        except Exception as e:
            print(f"套用設定時發生錯誤: {e}")
            
        messagebox.showinfo("設定保存", "所有設定已成功保存並立即生效！")

    def _clear_enhanced_results(self):
        """清除增強版分析結果（供左側按鈕呼叫）"""
        try:
            self.pass_tree_enhanced.clear()
            self.fail_tree_enhanced.clear()
            self.log_text_enhanced.clear()
            if hasattr(self, 'pass_summary_tree'):
                self.pass_summary_tree.delete(*self.pass_summary_tree.get_children())
            if hasattr(self, 'fail_summary_tree'):
                self.fail_summary_tree.delete(*self.fail_summary_tree.get_children())
            # 清除FAIL錯誤顯示區域
            if hasattr(self, 'fail_error_title'):
                self.fail_error_title.config(text="選擇FAIL項目查看詳細錯誤")
            if hasattr(self, 'fail_error_text'):
                self.fail_error_text.config(state=tk.NORMAL)
                self.fail_error_text.delete('1.0', tk.END)
                self.fail_error_text.config(state=tk.NORMAL)
            self.file_info_label.config(text="未選擇檔案", fg='#666')
            self.current_log_path = ''
            self.current_mode = 'single'
        except Exception:
            pass

    def _open_markdown_help(self):
        """開啟並顯示 dioc/README.md 或 QUICK_START.md 內容"""
        try:
            md_path = get_resource_path(os.path.join('dioc', 'README.md'))
            content = ''
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                alt_path = get_resource_path(os.path.join('dioc', 'QUICK_START.md'))
                with open(alt_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            self._show_text_viewer_window("README 說明", content)
        except Exception as e:
            try:
                messagebox.showerror("錯誤", f"無法讀取說明：{e}")
            except Exception:
                pass

    def _open_html_help(self):
        """以系統預設瀏覽器開啟操作說明 HTML（docs/USER_GUIDE.html）"""
        try:
            html_path = get_resource_path(os.path.join('docs', 'USER_GUIDE.html'))
            if not os.path.exists(html_path):
                # 後備使用 README
                return self._open_markdown_help()
            webbrowser.open(f"file:///{html_path}")
        except Exception as e:
            try:
                messagebox.showerror("錯誤", f"無法開啟操作說明：{e}")
            except Exception:
                pass

    def _show_text_viewer_window(self, title: str, content: str):
        """顯示純文字視窗（使用內容字體大小）"""
        win = tk.Toplevel(self.root)
        win.title(title)
        # 設定最小和最大尺寸
        win.minsize(600, 400)
        win.maxsize(1200, 900)
        win.geometry("800x600")
        
        # 讓視窗居中顯示
        win.transient(self.root)
        win.grab_set()
        win.update_idletasks()
        
        frame = tk.Frame(win)
        frame.pack(fill=tk.BOTH, expand=1)
        text = tk.Text(frame, wrap=tk.WORD, font=('Consolas', self.content_font_size))
        vs = tk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
        hs = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=text.xview)
        text.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        text.grid(row=0, column=0, sticky='nsew')
        vs.grid(row=0, column=1, sticky='ns')
        hs.grid(row=1, column=0, sticky='ew')
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        text.insert('1.0', content)
        text.config(state=tk.NORMAL)
        
        # 自動調整視窗大小以適應內容
        self._auto_resize_text_window(win, text)

    # === UI 字體調整 ===
    def _increase_ui_font(self):
        """增加介面文字字體大小"""
        if self.ui_font_size < 15:
            self.ui_font_size += 1
            self._apply_font_size()
            self._save_settings_silent()

    def _decrease_ui_font(self):
        """減少介面文字字體大小"""
        if self.ui_font_size > 10:
            self.ui_font_size -= 1
            self._apply_font_size()
            self._save_settings_silent()

    def _increase_content_font(self):
        """增加內容字體大小"""
        if self.content_font_size < 15:
            self.content_font_size += 1
            self._apply_font_size()
            self._save_settings_silent()

    def _decrease_content_font(self):
        """減少內容字體大小"""
        if self.content_font_size > 10:
            self.content_font_size -= 1
            self._apply_font_size()
            self._save_settings_silent()

    # === 左側面板寬度調整 ===
    def _decrease_pane_width(self):
        """減少左側面板寬度"""
        current_width = self.settings.get('pane_width', 250)
        if current_width > 100:  # 至少保留一個最小寬度
            new_width = current_width - 10
            self.settings['pane_width'] = new_width
            if hasattr(self, 'pane_width_label'):
                self.pane_width_label.config(text=f"{new_width}px")
            # 更新分割視窗的面板寬度
            if hasattr(self, 'left_frame'):
                self.left_frame.configure(width=new_width)
                self.paned.update_idletasks()
            save_settings(self.settings)

    def _increase_pane_width(self):
        """增加左側面板寬度"""
        current_width = self.settings.get('pane_width', 250)
        if current_width < 500:  # 最大寬度限制
            new_width = current_width + 10
            self.settings['pane_width'] = new_width
            if hasattr(self, 'pane_width_label'):
                self.pane_width_label.config(text=f"{new_width}px")
            # 更新分割視窗的面板寬度
            if hasattr(self, 'left_frame'):
                self.left_frame.configure(width=new_width)
                self.paned.update_idletasks()
            save_settings(self.settings)

    def _reset_pane_width(self):
        """重置左側面板寬度為預設值"""
        default_width = 250
        self.settings['pane_width'] = default_width
        if hasattr(self, 'pane_width_label'):
            self.pane_width_label.config(text=f"{default_width}px")
        # 更新分割視窗的面板寬度
        if hasattr(self, 'left_frame'):
            self.left_frame.configure(width=default_width)
            self.paned.update_idletasks()
        save_settings(self.settings)

    def _show_log_file_preview(self, folder):
        """顯示將被處理的 .log 檔清單預覽"""
        try:
            log_files = []
            for root, dirs, files in os.walk(folder):
                for fn in files:
                    if fn.lower().endswith('.log'):
                        log_files.append(fn)
            
            if log_files:
                preview_text = f"將處理 {len(log_files)} 個 .log 檔案:\n"
                preview_text += "\n".join(f"  • {fn}" for fn in sorted(log_files))
                # 可以在這裡顯示預覽，例如更新左側面板的某個標籤
                # 但目前先保持簡單
                print(preview_text)
        except Exception as e:
            print(f"顯示LOG檔案預覽失敗: {e}")

    def _auto_resize_text_window(self, win, text_widget):
        """根據文字內容自動調整文字視窗大小，確保導航按鈕始終可見"""
        try:
            # 獲取文字內容的行數和最大行寬度
            content = text_widget.get('1.0', tk.END)
            lines = content.split('\n')
            max_line_length = max(len(line) for line in lines) if lines else 0
            total_lines = len(lines)
            
            # 計算合適的視窗尺寸
            # 每行大約需要 8-10 像素寬度，每行大約需要 16-18 像素高度
            char_width = 8  # 每個字符的寬度
            char_height = 16  # 每行的高度
            
            # 計算文字區域的寬度和高度（更緊湊的計算）
            text_width = min(max_line_length * char_width + 80, 800)   # 減少邊距，最大800
            text_height = min(total_lines * char_height + 150, 600)    # 減少邊距，最大600
            
            # 設定視窗大小（更緊湊）
            window_width = max(600, text_width + 40)   # 減少額外寬度
            window_height = max(400, text_height + 80)  # 減少額外高度，確保導航按鈕可見
            
            # 限制最大尺寸（更嚴格，避免視窗過大）
            window_width = min(window_width, 900)   # 從1200減少到900
            window_height = min(window_height, 700)  # 從900減少到700
            
            # 更新視窗大小
            win.geometry(f"{window_width}x{window_height}")
            
            # 重新居中視窗
            win.update_idletasks()
            x = (win.winfo_screenwidth() // 2) - (window_width // 2)
            y = (win.winfo_screenheight() // 2) - (window_height // 2)
            win.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
        except Exception as e:
            print(f"自動調整文字視窗大小失敗: {e}")

    def _show_open_folder_prompt(self, out_dir: str, total_files: int, pass_count: int, fail_count: int, pass_path: str, fail_path: str):
        """白底視窗，加入打勾選項選擇要開啟的檔案"""
        win = tk.Toplevel(self.root)
        win.title("匯出完成")
        win.geometry("700x400")
        
        # 讓視窗居中顯示
        win.transient(self.root)
        win.grab_set()
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (700 // 2)
        y = (win.winfo_screenheight() // 2) - (400 // 2)
        win.geometry(f"700x400+{x}+{y}")
        
        try:
            win.configure(bg='white')
        except Exception:
            pass
        
        # 主要資訊
        info = (
            f"匯出完成 / 共 {total_files} 個檔案\n\n"
            f"PASS: {pass_count}\nFAIL: {fail_count}\n\n"
            f"已產生：\n{pass_path}\n{fail_path}\n"
        )
        lbl_info = tk.Label(win, text=info, bg='white', fg='black', font=('Microsoft JhengHei', 11))
        lbl_info.pack(fill=tk.BOTH, expand=1, padx=16, pady=(16, 6))
        
        # 選擇要開啟的檔案
        lbl_ask = tk.Label(win, text="選擇要開啟的檔案：", bg='#FFF176', fg='black', font=('Microsoft JhengHei', 11, 'bold'))
        lbl_ask.pack(fill=tk.X, padx=16, pady=(0, 8))
        
        # 打勾選項框架
        check_frame = tk.Frame(win, bg='white')
        check_frame.pack(fill=tk.X, padx=16, pady=(0, 16))
        
        # 建立打勾變數（預設都打勾）
        open_folder_var = tk.BooleanVar(value=True)
        open_pass_var = tk.BooleanVar(value=True)
        open_fail_var = tk.BooleanVar(value=True)
        
        # 打勾選項
        cb_folder = tk.Checkbutton(check_frame, text="開啟輸出資料夾", variable=open_folder_var, 
                                  bg='white', fg='black', font=('Microsoft JhengHei', 10))
        cb_folder.pack(anchor='w', pady=2)
        
        cb_pass = tk.Checkbutton(check_frame, text="開啟 PASS匯總.xlsx", variable=open_pass_var, 
                                bg='white', fg='black', font=('Microsoft JhengHei', 10))
        cb_pass.pack(anchor='w', pady=2)
        
        cb_fail = tk.Checkbutton(check_frame, text="開啟 FAIL匯總.xlsx", variable=open_fail_var, 
                                bg='white', fg='black', font=('Microsoft JhengHei', 10))
        cb_fail.pack(anchor='w', pady=2)
        
        # 按鈕框架
        btns = tk.Frame(win, bg='white')
        btns.pack(pady=8)
        
        def on_confirm():
            try:
                # 開啟資料夾
                if open_folder_var.get():
                    os.startfile(out_dir)
                
                # 開啟 PASS 檔案
                if open_pass_var.get() and os.path.exists(pass_path):
                    os.startfile(pass_path)
                
                # 開啟 FAIL 檔案
                if open_fail_var.get() and os.path.exists(fail_path):
                    os.startfile(fail_path)
                    
            except Exception as e:
                print(f"開啟檔案時發生錯誤: {e}")
            win.destroy()
            
        def on_cancel():
            win.destroy()
            
        btn_confirm = tk.Button(btns, text="確定", command=on_confirm, bg='#4CAF50', fg='white', font=('Microsoft JhengHei', 10))
        btn_cancel = tk.Button(btns, text="取消", command=on_cancel, bg='#F44336', fg='white', font=('Microsoft JhengHei', 10))
        btn_confirm.pack(side=tk.LEFT, padx=10)
        btn_cancel.pack(side=tk.LEFT, padx=10)

    def start_csv_processing(self):
        """開始CSV檔案處理"""
        try:
            from csv_processor import CSVProcessor
            processor = CSVProcessor(self)
            
            # 提供選擇方式
            choice = messagebox.askyesnocancel(
                "CSV處理方式", 
                "請選擇CSV檔案處理方式：\n\n" +
                "是(Y) - 選擇資料夾（自動搜尋CSV檔案）\n" +
                "否(N) - 直接選擇CSV檔案（支援多選）\n" +
                "取消 - 取消操作"
            )
            
            if choice is True:
                # 選擇資料夾
                processor.select_directory()
            elif choice is False:
                # 直接選擇檔案
                processor.select_files()
            # choice is None 表示取消
            
        except ImportError as e:
            messagebox.showerror("錯誤", f"無法載入CSV處理模組: {e}")
        except Exception as e:
            messagebox.showerror("錯誤", f"CSV處理發生錯誤: {e}")


def main_enhanced():
    """增強版主程式"""
    root = tk.Tk()
    app = EnhancedLogAnalyzerApp(root)
    root.mainloop()

if __name__ == '__main__':
    main_enhanced() 