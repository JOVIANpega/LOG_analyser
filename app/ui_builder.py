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
        # 使用精簡的欄位定義
        pass_columns = ("比對項目細節", "判定結果")
        self.pass_tree_enhanced = EnhancedTreeview(self.tab_pass, pass_columns, settings=self.settings)
        self.pass_tree_enhanced.pack_with_scrollbars(fill=tk.BOTH, expand=1)
        self.pass_tree_enhanced.auto_fit_columns()
    
    def _build_enhanced_fail_tab(self):
        """建立FAIL標籤頁 - 分割成上下兩個視窗"""
        self.tab_fail = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_fail, text="❌ FAIL測項")
        
        # 創建上下分割視窗 - 使用 ttk.Panedwindow
        self.fail_paned = ttk.Panedwindow(self.tab_fail, orient=tk.VERTICAL)
        self.fail_paned.pack(fill=tk.BOTH, expand=1)
        
        self.fail_upper_frame = ttk.Frame(self.fail_paned)
        fail_columns = ("測項名稱", "FAIL原因")
        self.fail_tree_enhanced = EnhancedTreeview(self.fail_upper_frame, fail_columns, settings=self.settings)
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
                                      bg='white', fg='#333333', font=('Consolas', 12),
                                      relief=tk.FLAT, padx=10, pady=10)
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
        
        if not is_multiple:
            # 單一檔案模式：一律顯示 PASS 與 FAIL 標籤 (使用者改回：不論有無內容都要看到 TAB)
            if str(self.tab_pass) not in visible_tabs:
                self.notebook.insert(0, self.tab_pass, text="✅ PASS測項")
            else:
                self.notebook.add(self.tab_pass) # 確保取消 hide 狀態
                
            if str(self.tab_fail) not in visible_tabs:
                pos = 1 if str(self.tab_pass) in self.notebook.tabs() else 0
                self.notebook.insert(pos, self.tab_fail, text="❌ FAIL測項")
            else:
                self.notebook.add(self.tab_fail) # 確保取消 hide 狀態
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
        """以系統預設方式開啟操作說明 HTML（docs/USER_GUIDE.html）"""
        try:
            html_path = get_resource_path(os.path.join('docs', 'USER_GUIDE.html'))
            
            if not os.path.exists(html_path):
                # 如果找不到 HTML，後備使用文字版的 README
                return self._open_markdown_help()
            
            # 使用 Windows 原生的 os.startfile，這是開啟本地檔案最穩定的方式
            # 它會直接呼叫系統預設瀏覽器開啟檔案，且對路徑中的特殊字元(如括號)支援度最高
            os.startfile(html_path)
            
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

    def _show_open_folder_prompt(self, out_dir: str, total_files: int, pass_count: int, fail_count: int, report_list: list):
        """精簡化報表完成對話框：支援多站別、預設不勾選、路徑清晰"""
        import tkinter as tk
        from tkinter import ttk
        
        win = tk.Toplevel(self.root)
        win.title("匯出完成")
        win.configure(bg='white')
        
        # 根據字體調整視窗大小 (增加一些緩衝空間)
        base_size = self.settings.get('ui_font_size', 12)
        win_w = max(860, int(860 * (base_size / 12)))
        win_h = max(550, int(600 * (base_size / 12))) # 增加高度基準
        
        # 居中與旗標
        win.transient(self.root)
        win.attributes("-topmost", True)
        win.grab_set()
        x = (win.winfo_screenwidth() // 2) - (win_w // 2)
        y = (win.winfo_screenheight() // 2) - (win_h // 2)
        win.geometry(f"{win_w}x{win_h}+{x}+{y}")
        
        main_frame = tk.Frame(win, bg='white', padx=40, pady=20) # 減少 pady
        main_frame.pack(fill=tk.BOTH, expand=True)

        # === 關鍵修正：先 Pack 按鈕區，確保永遠在最底部且可見 ===
        btn_frame = tk.Frame(main_frame, bg='white', pady=10)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 1. 簡約標題
        tk.Label(main_frame, text="✅ 報表匯出完成", font=('Microsoft JhengHei', base_size + 6, 'bold'), 
                 fg='#1B5E20', bg='white').pack(anchor='w', pady=(0, 10))
        
        # 2. 統計訊息 (精簡一行)
        stats_text = f"共分析 {total_files} 個 Log 檔案 | PASS: {pass_count} | FAIL: {fail_count}"
        tk.Label(main_frame, text=stats_text, font=('Microsoft JhengHei', base_size), 
                 bg='white', fg='#424242').pack(anchor='w', pady=(0, 15))

        # 3. 輸出路徑提示
        path_hint = tk.Frame(main_frame, bg='#FAFAFA', padx=10, pady=5)
        path_hint.pack(fill=tk.X, pady=(0, 15))
        tk.Label(path_hint, text=f"📂 輸出目錄: {out_dir}", font=('Consolas', base_size - 1), 
                 bg='#FAFAFA', fg='#455A64').pack(side=tk.LEFT)

        # 4. 報表清單 (捲動區域)
        tk.Label(main_frame, text="產生的 Excel 報表列表：", 
                 font=('Microsoft JhengHei', base_size, 'bold'), bg='white').pack(anchor='w', pady=(5, 5))
        
        list_container = tk.Frame(main_frame, bg='white', bd=1, relief=tk.SOLID)
        list_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        canvas = tk.Canvas(list_container, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # 建立清單 (包含勾選框，預設不打勾)
        check_vars = [] # 儲存 (var, path)
        
        for station, p_path, f_path in report_list:
            items = []
            if p_path and os.path.exists(p_path):
                items.append(('PASS', p_path, '#2E7D32'))
            if f_path and os.path.exists(f_path):
                items.append(('FAIL', f_path, '#C62828'))
            
            for type_label, full_path, color in items:
                fname = os.path.basename(full_path)
                var = tk.BooleanVar(value=False) # 🟢 預設不打勾
                
                row = tk.Frame(scrollable_frame, bg='white', padx=10, pady=4)
                row.pack(fill=tk.X, anchor='w')
                
                cb = tk.Checkbutton(row, text=f" {station} {type_label} 匯總 ", variable=var,
                                   font=('Microsoft JhengHei', base_size), bg='white', activebackground='white')
                cb.pack(side=tk.LEFT)
                
                tk.Label(row, text=f"({fname})", font=('Consolas', base_size - 2), 
                         fg='#757575', bg='white').pack(side=tk.LEFT, padx=15)
                
                check_vars.append((var, full_path))

        def on_close():
            win.destroy()
            
        def on_open_selected():
            try:
                opened = 0
                # 1. 開啟勾選的 Excel
                for var, p in check_vars:
                    if var.get() and os.path.exists(p):
                        os.startfile(p)
                        opened += 1
                
                # 2. 視需要開啟資料夾
                if folder_var.get(): 
                    os.startfile(out_dir)
                    opened += 1
                
                # 若完全沒勾點執行，就直接關閉
                win.destroy()
            except Exception as e:
                print(f"開啟失敗: {e}")
                win.destroy()

        # 按鈕反向放置於底部框架
        btn_ok = tk.Button(btn_frame, text=" 打 開 勾 選 的 Excel 報 表 ", font=('Microsoft JhengHei', base_size, 'bold'), 
                            bg='#0288D1', fg='white', width=28, pady=8, relief=tk.FLAT, cursor='hand2', command=on_open_selected)
        btn_ok.pack(side=tk.RIGHT, padx=5)

        btn_cancel = tk.Button(btn_frame, text=" 僅 關 閉 視 窗 ", font=('Microsoft JhengHei', base_size), 
                            bg='#EEEEEE', fg='#424242', width=15, pady=8, relief=tk.FLAT, cursor='hand2', command=on_close)
        btn_cancel.pack(side=tk.RIGHT, padx=5)

        # 5. 資料夾選項 (放在按鈕上方)
        folder_var = tk.BooleanVar(value=False)
        tk.Checkbutton(main_frame, text=" 打開輸出資料夾 (Explorer)", variable=folder_var, 
                       font=('Microsoft JhengHei', base_size), bg='white', activebackground='white'
                       ).pack(side=tk.BOTTOM, anchor='w', pady=10)

        win.protocol("WM_DELETE_WINDOW", win.destroy)
        win.wait_window()


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
