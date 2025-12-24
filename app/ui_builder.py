# -*- coding: utf-8 -*-
"""
UI Builder Module
Handles construction of the UI components (Mixin)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import webbrowser
from .ui_components import FontScaler, build_output_dir, get_resource_path
from .ui_enhanced_fixed import EnhancedTreeview, EnhancedText
from .enhanced_settings import build_settings_content
from .enhanced_left_panel import build_left_panel
from .settings_loader import save_settings

class UIBuilderMixin:
    """Mixin for handling UI construction in the Log Analyzer"""
    
    def _build_status_bar(self):
        """建立底部狀態列 (進度條與狀態文字)"""
        # 使用更深色的背景以便識別 (基於主題)
        self.status_frame = ttk.Frame(self.root, style='secondary.TFrame')
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 狀態文字標籤
        self.status_label = ttk.Label(self.status_frame, text="就緒", font=('Arial', 10), style='inverse-secondary')
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)
        if hasattr(self, 'font_scaler'):
            self.font_scaler.register(self.status_label)
        
        # 百分比標籤
        self.percentage_label = ttk.Label(self.status_frame, text="0%", font=('Arial', 10, 'bold'), style='inverse-secondary')
        self.percentage_label.pack(side=tk.RIGHT, padx=5)
        if hasattr(self, 'font_scaler'):
            self.font_scaler.register(self.percentage_label)
        
        # 進度條 (加長一點)
        self.main_progress_bar = ttk.Progressbar(self.status_frame, orient=tk.HORIZONTAL, length=300, mode='determinate', style='info.Horizontal.TProgressbar')
        self.main_progress_bar.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def _build_enhanced_ui(self):
        """建立增強版UI"""
        # 主要分割視窗 - 使用 ttk.Panedwindow 以獲得更好的外觀
        self.paned = ttk.Panedwindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=1)
        
        # 左側控制面板
        pane_width = self.settings.get('pane_width', 250)
        self.left_frame = ttk.Frame(self.paned, width=pane_width)
        self._build_enhanced_left_panel(self.left_frame)
        self.paned.add(self.left_frame, weight=0) # weight=0 讓左側面板保持固定大小或由使用者調整
        
        # 右側結果顯示區域
        self.right_frame = ttk.Frame(self.paned)
        self._build_enhanced_right_panel(self.right_frame)
        self.paned.add(self.right_frame, weight=1)
        
        # 綁定分割視窗調整事件
        self.paned.bind('<ButtonRelease-1>', self._on_pane_adjust)
        self.paned.bind('<B1-Motion>', self._on_pane_adjust)  # 拖動時也保存
        
        # 建立狀態列
        self._build_status_bar()
        
        # 設定初始面板寬度（使用after確保UI已建立）
        self.root.after(100, lambda: self._set_initial_pane_width(pane_width))
        
    def _on_tab_changed(self, event):
        """標籤切換時的處理"""
        # 同步更新字體大小設定，確保樣式一致
        if hasattr(self, '_apply_font_size'):
            self._apply_font_size()
        
        # 當切換到 FAIL TAB 時，自動折疊原始LOG中的 PASS 項目
        try:
            selected_tab = self.notebook.select()
            if hasattr(self, 'tab_fail') and selected_tab == str(self.tab_fail):
                if hasattr(self, 'log_text_enhanced') and hasattr(self.log_text_enhanced, 'fold_all_pass_items'):
                    self.log_text_enhanced.fold_all_pass_items()
            # 當切換到 原始LOG TAB 時，自動聚焦錯誤位置
            elif hasattr(self, 'tab_log') and selected_tab == str(self.tab_log):
                if hasattr(self, 'log_text_enhanced'):
                    self.log_text_enhanced.focus_first_error_line()
        except Exception as e:
            print(f"TAB切換折疊處理失敗: {e}")
    
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
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # 檔案資訊標籤 (放在左側，佔滿剩餘空間)
        # User requested black color for better visibility
        self.file_info_label = tk.Label(top_frame, text="尚未選擇檔案", fg='black', anchor='w', font=('Arial', 10, 'bold'))
        self.file_info_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.font_scaler.register(self.file_info_label)
        
        # 建立標籤頁
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=1)
        
        # 綁定標籤切換事件
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)
        
        # 設定標籤頁樣式
        self._setup_tab_styles()
        
        # 建立各標籤頁
        self._build_enhanced_pass_tab()
        self._build_enhanced_fail_tab()
        self._build_enhanced_log_tab()
        self._build_enhanced_settings_tab()
        
        # 初始隱藏 PASS / FAIL 標籤 (使用者要求：剛打開不顯示)
        self.notebook.hide(self.tab_pass)
        self.notebook.hide(self.tab_fail)
        
        # 預設選中「原始LOG」
        self.notebook.select(self.tab_log)
    
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
        
        # 創建上下分割視窗 - 使用 ttk.Panedwindow
        self.fail_paned = ttk.Panedwindow(self.tab_fail, orient=tk.VERTICAL)
        self.fail_paned.pack(fill=tk.BOTH, expand=1)
        
        # 上半部 - FAIL測項列表
        self.fail_upper_frame = ttk.Frame(self.fail_paned)
        fail_columns = ("測項名稱", "指令", "錯誤回應", "Retry次數", "FAIL原因")
        self.fail_tree_enhanced = EnhancedTreeview(self.fail_upper_frame, fail_columns)
        self.fail_tree_enhanced.pack_with_scrollbars(fill=tk.BOTH, expand=1)
        self.fail_paned.add(self.fail_upper_frame, weight=3) # 分配權重
        
        # 下半部 - FAIL錯誤詳細資訊
        self.fail_lower_frame = ttk.Frame(self.fail_paned)
        
        # 錯誤標題
        self.fail_error_title = ttk.Label(self.fail_lower_frame, text="選擇FAIL項目查看詳細錯誤", 
                                        font=('Arial', 16, 'bold'), foreground='red')
        self.fail_error_title.pack(pady=10)
        
        # 錯誤內容文字框
        error_text_frame = ttk.Frame(self.fail_lower_frame)
        error_text_frame.pack(fill=tk.BOTH, expand=1, padx=10, pady=5)
        
        self.fail_error_text = tk.Text(error_text_frame, wrap=tk.WORD, 
                                      bg='#FFF0F0', fg='darkred', font=('Consolas', 12),
                                      relief=tk.FLAT, padx=8, pady=8)
        self.fail_error_text.grid(row=0, column=0, sticky='nsew')
        
        # 滾動條
        error_scrollbar = ttk.Scrollbar(error_text_frame, command=self.fail_error_text.yview)
        error_scrollbar.grid(row=0, column=1, sticky='ns')
        self.fail_error_text.config(yscrollcommand=error_scrollbar.set)
        
        error_text_frame.grid_rowconfigure(0, weight=1)
        error_text_frame.grid_columnconfigure(0, weight=1)
        
        self.fail_paned.add(self.fail_lower_frame, weight=2)
        
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
        """建立設定標籤頁 (移除捲軸)"""
        self.tab_settings = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_settings, text="⚙️ 設定")
        
        # 建立內容框架
        container = ttk.Frame(self.tab_settings)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 直接建構內容
        build_settings_content(self, container)
    
    def _build_settings_content(self, parent):
        """建立設定內容（抽離至模組）"""
        build_settings_content(self, parent)
    
    
    def _update_tabs_visibility(self, pass_count, fail_count, is_multiple=True):
        """根據分析結果動態顯示標籤頁"""
        # 先獲取目前的標籤列表（用於判斷是否已存在）
        visible_tabs = self.notebook.tabs()
        
        # 單一檔案模式：pass/fail 都顯示 (由使用者要求)
        if not is_multiple:
            if str(self.tab_pass) not in visible_tabs:
                self.notebook.insert(0, self.tab_pass, text="✅ PASS測項")
            if str(self.tab_fail) not in visible_tabs:
                self.notebook.insert(1, self.tab_fail, text="❌ FAIL測項")
            return

        # 多檔案模式：有資料才顯示
        if pass_count > 0:
            if str(self.tab_pass) not in visible_tabs:
                self.notebook.insert(0, self.tab_pass, text="✅ PASS測項")
        else:
            self.notebook.hide(self.tab_pass)
            
        if fail_count > 0:
            if str(self.tab_fail) not in visible_tabs:
                # 確保在 PASS 之後，LOG 之前
                pos = 1 if str(self.tab_pass) in self.notebook.tabs() else 0
                self.notebook.insert(pos, self.tab_fail, text="❌ FAIL測項")
        else:
            self.notebook.hide(self.tab_fail)
        
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

    def _show_open_folder_prompt(self, out_dir: str, total_files: int, pass_count: int, fail_count: int, pass_path: str, fail_path: str, fail_path_new: str = None):
        """白底視窗，加入打勾選項選擇要開啟的檔案"""
        win = tk.Toplevel(self.root)
        win.title("匯出完成")
        win.geometry("750x480")
        
        # 讓視窗居中顯示
        win.transient(self.root)
        win.grab_set()
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (750 // 2)
        y = (win.winfo_screenheight() // 2) - (480 // 2)
        win.geometry(f"750x480+{x}+{y}")
        
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
        if fail_path_new:
             info += f"{fail_path_new} (新版)\n"
             
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
        open_fail_new_var = tk.BooleanVar(value=True)
        
        # 打勾選項
        cb_folder = tk.Checkbutton(check_frame, text="開啟輸出資料夾", variable=open_folder_var, 
                                  bg='white', fg='black', font=('Microsoft JhengHei', 10))
        cb_folder.pack(anchor='w', pady=2)
        
        cb_pass = tk.Checkbutton(check_frame, text="開啟 PASS匯總.xlsx", variable=open_pass_var, 
                                bg='white', fg='black', font=('Microsoft JhengHei', 10))
        cb_pass.pack(anchor='w', pady=2)
        
        cb_fail = tk.Checkbutton(check_frame, text="開啟 FAIL匯總.xlsx (舊版)", variable=open_fail_var, 
                                bg='white', fg='black', font=('Microsoft JhengHei', 10))
        cb_fail.pack(anchor='w', pady=2)
        
        if fail_path_new:
            cb_fail_new = tk.Checkbutton(check_frame, text="開啟 FAIL匯總_新版.xlsx (Dashboard)", variable=open_fail_new_var, 
                                    bg='white', font=('Microsoft JhengHei', 10, 'bold'), fg='blue')
            cb_fail_new.pack(anchor='w', pady=2)
        
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

                # 開啟 FAIL 新版檔案
                if fail_path_new and open_fail_new_var.get() and os.path.exists(fail_path_new):
                    os.startfile(fail_path_new)
                    
            except Exception as e:
                print(f"開啟檔案時發生錯誤: {e}")
            finally:
                try:
                    win.grab_release()
                except:
                    pass
                win.destroy()
            
        def on_cancel():
            try:
                win.grab_release()
            except:
                pass
            win.destroy()
        
        # 綁定視窗關閉事件
        win.protocol("WM_DELETE_WINDOW", on_cancel)
            
        btn_confirm = tk.Button(btns, text="確定", command=on_confirm, bg='#4CAF50', fg='white', font=('Microsoft JhengHei', 10))
        btn_cancel = tk.Button(btns, text="取消", command=on_cancel, bg='#F44336', fg='white', font=('Microsoft JhengHei', 10))
        btn_confirm.pack(side=tk.LEFT, padx=10)
        btn_cancel.pack(side=tk.LEFT, padx=10)

    def start_csv_processing(self):
        """開始CSV檔案處理"""
        try:
            from .csv_processor import CSVProcessor
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
