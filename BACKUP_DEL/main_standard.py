#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試Log分析器GUI應用程式 - 標準版
提供基本的圖形使用者介面來分析測試log檔案
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
from settings_loader import load_settings, save_settings
from log_parser import LogParser
from excel_writer import ExcelWriter
from ui_components import FontScaler

class LogAnalyzerApp:
    """標準版LOG分析器應用程式"""
    
    def __init__(self, root):
        """初始化標準版應用程式"""
        self.root = root
        self.root.title("測試Log分析器 - 標準版")
        self.settings = load_settings()
        self.font_size = self.settings.get('font_size', 11)
        self.font_scaler = FontScaler(root, default_size=self.font_size)
        self.log_parser = LogParser()
        self.excel_writer = ExcelWriter()
        self.current_mode = 'single'  # 'single' or 'multi'
        self.current_log_path = ''
        self._build_ui()
        self._apply_font_size()
        # 綁定關閉事件以保存設定
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _build_ui(self):
        """建立標準版UI"""
        # PanedWindow左右分割
        self.paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        self.paned.pack(fill=tk.BOTH, expand=1)
        # 左側：檔案選擇與字體調整
        self.left_frame = tk.Frame(self.paned)
        self._build_left_panel(self.left_frame)
        self.paned.add(self.left_frame, minsize=220)
        # 右側：Notebook(Tab)
        self.right_frame = tk.Frame(self.paned)
        self._build_right_panel(self.right_frame)
        self.paned.add(self.right_frame, minsize=600)
        # 綁定分隔線調整事件，調整後即時保存
        self.paned.bind('<ButtonRelease-1>', self._on_pane_adjust)
        # 初始套用左側寬度
        pane_width = self.settings.get('pane_width', 250)
        self.root.after(100, lambda: self._apply_initial_pane_width(pane_width))

    def _build_left_panel(self, parent):
        """建立左側面板"""
        # 檔案/資料夾選擇
        label = tk.Label(parent, text="選擇Log檔案或資料夾：")
        label.pack(pady=(15, 5), anchor='w')
        self.font_scaler.register(label)
        btn_file = tk.Button(parent, text="選擇檔案", command=self._select_file)
        btn_file.pack(fill=tk.X, padx=10, pady=2)
        self.font_scaler.register(btn_file)
        btn_folder = tk.Button(parent, text="選擇資料夾", command=self._select_folder)
        btn_folder.pack(fill=tk.X, padx=10, pady=2)
        self.font_scaler.register(btn_folder)
        
        # 將左三個按鈕字體加粗與加入hover效果
        try:
            from ui_components import make_bold, apply_button_hover
            make_bold(btn_file)
            make_bold(btn_folder)
        except Exception:
            pass
        try:
            apply_button_hover(btn_file, hover_bg="#e8f4fd")
            apply_button_hover(btn_folder, hover_bg="#e8f4fd")
        except Exception:
            pass
        
        # 測試腳本選擇
        script_label = tk.Label(parent, text="選擇測試腳本Excel（可選）：")
        script_label.pack(pady=(15, 5), anchor='w')
        self.font_scaler.register(script_label)
        
        btn_script = tk.Button(parent, text="選擇腳本", command=self._select_script)
        btn_script.pack(fill=tk.X, padx=10, pady=2)
        self.font_scaler.register(btn_script)
        
        # 第三個按鈕也加粗與hover
        try:
            make_bold(btn_script)
            apply_button_hover(btn_script, hover_bg="#e8f4fd")
        except Exception:
            pass
        
        # 查看說明（Markdown）
        help_btn = tk.Button(parent, text="📖 查看說明(README)", command=self._open_markdown_help, bg="#607D8B", fg="white")
        help_btn.pack(fill=tk.X, padx=10, pady=(6, 6))
        self.font_scaler.register(help_btn)
        try:
            make_bold(help_btn)
            apply_button_hover(help_btn, hover_bg="#78909C", hover_fg='white', normal_bg='#607D8B', normal_fg='white')
        except Exception:
            pass
        
        self.script_path = ""
        self.script_label = tk.Label(parent, text="未選擇腳本", fg="#888")
        self.script_label.pack(pady=(2, 10), anchor='w')
        self.font_scaler.register(self.script_label)
        
        # 分析按鈕
        self.analyze_btn = tk.Button(parent, text="開始分析", command=self._analyze_log, bg="#4CAF50", fg="white")
        self.analyze_btn.pack(fill=tk.X, padx=10, pady=(10, 2))
        self.font_scaler.register(self.analyze_btn)
        self.analyze_btn.config(state=tk.DISABLED)
        
        # 拖拉支援
        drag_label = tk.Label(parent, text="(可拖拉檔案/資料夾進視窗)", fg="#888")
        drag_label.pack(pady=(5, 15), anchor='w')
        self.font_scaler.register(drag_label)
        
        # 字體大小調整
        font_frame = tk.Frame(parent)
        font_frame.pack(pady=10)
        tk.Label(font_frame, text="字體大小：").pack(side=tk.LEFT)
        btn_minus = tk.Button(font_frame, text="-", width=2, command=self._decrease_font)
        btn_minus.pack(side=tk.LEFT, padx=2)
        btn_plus = tk.Button(font_frame, text="+", width=2, command=self._increase_font)
        btn_plus.pack(side=tk.LEFT, padx=2)
        self.font_scaler.register(font_frame)
        self.font_scaler.register(btn_minus)
        self.font_scaler.register(btn_plus)
        
        # 顯示目前字體大小
        self.font_size_label = tk.Label(parent, text=f"目前字體：{self.font_size}")
        self.font_size_label.pack(pady=(5, 0))
        self.font_scaler.register(self.font_size_label)

    def _apply_initial_pane_width(self, width: int):
        """在UI建立後設定左側面板寬度"""
        try:
            if width and width > 0:
                try:
                    self.paned.paneconfigure(self.left_frame, width=width)
                except Exception:
                    pass
                # 直接放置sash位置
                try:
                    self.paned.update_idletasks()
                    self.paned.sash_place(0, width, 1)
                except Exception:
                    pass
        except Exception:
            pass

    def _on_pane_adjust(self, event=None):
        """分隔線調整後保存左側寬度到設定"""
        try:
            if hasattr(self, 'left_frame'):
                left_width = self.left_frame.winfo_width()
                if left_width and left_width > 0:
                    self.settings['pane_width'] = left_width
                    save_settings(self.settings)
        except Exception:
            pass

    def _on_closing(self):
        """關閉視窗時保存設定"""
        try:
            # 保存目前左側寬度與字體大小
            if hasattr(self, 'left_frame'):
                lw = self.left_frame.winfo_width()
                if lw and lw > 0:
                    self.settings['pane_width'] = lw
            self.settings['font_size'] = getattr(self, 'font_size', 11)
            save_settings(self.settings)
        except Exception:
            pass
        self.root.destroy()

    def _on_drop(self, event):
        """處理拖拉檔案/資料夾"""
        # 簡化版拖拉處理
        pass

    def _build_right_panel(self, parent):
        """建立右側面板"""
        # Notebook(Tab)
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=1)
        
        # Tab1: PASS測項
        self.tab_pass = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_pass, text="✅ PASS測項")
        
        # PASS TreeView
        pass_columns = ("Step Name", "指令", "回應", "結果")
        self.pass_tree = ttk.Treeview(self.tab_pass, columns=pass_columns, show='headings')
        for col in pass_columns:
            self.pass_tree.heading(col, text=col)
            self.pass_tree.column(col, width=150)
        
        # PASS滾動條
        pass_scrollbar = ttk.Scrollbar(self.tab_pass, orient=tk.VERTICAL, command=self.pass_tree.yview)
        self.pass_tree.configure(yscrollcommand=pass_scrollbar.set)
        self.pass_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        pass_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # PASS雙擊事件
        self.pass_tree.bind('<Double-1>', self._on_pass_expand)
        self.pass_tree.bind('<Motion>', self._on_pass_tree_hover)
        self._pass_full_map = {}
        
        # Tab2: FAIL測項
        self.tab_fail = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_fail, text="❌ FAIL測項")
        
        # FAIL TreeView
        fail_columns = ("Step Name", "指令", "錯誤回應", "Retry次數", "FAIL原因")
        self.fail_tree = ttk.Treeview(self.tab_fail, columns=fail_columns, show='headings')
        for col in fail_columns:
            self.fail_tree.heading(col, text=col)
            self.fail_tree.column(col, width=150)
        
        # FAIL滾動條
        fail_scrollbar = ttk.Scrollbar(self.tab_fail, orient=tk.VERTICAL, command=self.fail_tree.yview)
        self.fail_tree.configure(yscrollcommand=fail_scrollbar.set)
        self.fail_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        fail_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # FAIL雙擊事件
        self.fail_tree.bind('<Double-1>', self._on_fail_expand)
        self.fail_tree.bind('<Motion>', self._on_fail_tree_hover)
        self._fail_full_map = {}
        
        # Tab3: 原始LOG
        self.tab_log = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_log, text="📄 原始LOG")
        
        # 原始LOG文字框
        self.log_text = tk.Text(self.tab_log, wrap=tk.NONE)
        log_scrollbar_v = ttk.Scrollbar(self.tab_log, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scrollbar_h = ttk.Scrollbar(self.tab_log, orient=tk.HORIZONTAL, command=self.log_text.xview)
        self.log_text.configure(yscrollcommand=log_scrollbar_v.set, xscrollcommand=log_scrollbar_h.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        log_scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        log_scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Tab4: 腳本比對
        self.tab_script = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_script, text="📊 腳本比對")
        
        # 腳本比對TreeView
        script_columns = ("Test ID", "狀態", "備註")
        self.script_tree = ttk.Treeview(self.tab_script, columns=script_columns, show='headings')
        for col in script_columns:
            self.script_tree.heading(col, text=col)
            self.script_tree.column(col, width=150)
        
        # 腳本比對滾動條
        script_scrollbar = ttk.Scrollbar(self.tab_script, orient=tk.VERTICAL, command=self.script_tree.yview)
        self.script_tree.configure(yscrollcommand=script_scrollbar.set)
        self.script_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        script_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 匯出按鈕
        self.export_btn = tk.Button(parent, text="📊 匯出Excel報告", command=self._export_excel, bg="#607D8B", fg="white")
        self.export_btn.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        self.export_btn.config(state=tk.DISABLED)
        self.font_scaler.register(self.export_btn)

    def _on_pass_expand(self, event):
        """PASS項目雙擊展開"""
        item = self.pass_tree.selection()[0] if self.pass_tree.selection() else None
        if item:
            content = self._pass_full_map.get(item)
            if content:
                self._show_full_content_window("測項指令內容 (PASS)", content)

    def _on_fail_expand(self, event):
        """FAIL項目雙擊展開"""
        item = self.fail_tree.selection()[0] if self.fail_tree.selection() else None
        if item:
            content = self._fail_full_map.get(item)
            if content:
                self._show_full_content_window("測項指令內容 (FAIL)", content)

    def _show_full_content_window(self, title, content):
        """顯示完整內容視窗"""
        win = tk.Toplevel(self.root)
        # 先取得摘要與步驟名稱，更新標題
        summary, step_label = self._build_cmd_resp_summary_and_label(content)
        if step_label:
            title = f"{step_label} +測項指令內容"
        win.title(title)
        # 視窗背景深藍色
        try:
            win.configure(bg="#0B1D39")
        except Exception:
            pass
        # 設定最小和最大尺寸
        win.minsize(600, 400)
        win.maxsize(1200, 900)
        win.geometry("800x600")
        
        # 讓視窗居中顯示
        win.transient(self.root)
        win.grab_set()
        win.update_idletasks()
        
        # 頂部標題（顯示步驟名稱 +測項指令內容）
        header_text = title
        header = tk.Label(win, text=header_text, font=('Arial', 14, 'bold'), fg='#FFFFFF', bg="#0B1D39")
        header.pack(pady=(10, 0))
        
        # 文字框與滾動條
        frame = tk.Frame(win, bg="#0B1D39")
        frame.pack(fill=tk.BOTH, expand=1, padx=8, pady=8)
        text = tk.Text(frame, wrap=tk.NONE, font=('Consolas', self.font_size), bg='#0B1D39', fg='#FFFFFF', highlightthickness=0, borderwidth=0, insertbackground='#FFFFFF')
        
        # 垂直滾動條 - 做大一點，靠近文字區
        vs = tk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview, width=20)
        vs.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # 水平滾動條 - 做大一點
        hs = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=text.xview, width=20)
        hs.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        
        text.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        
        # 內容
        separator = "************************我是分隔線**************************************"
        merged = summary + f"\n\n{separator}\n\n" + content if summary.strip() else content
        text.insert('1.0', merged)
        # 可選複製
        text.config(state=tk.NORMAL)
        
        # 自動調整視窗大小以適應內容
        self._auto_resize_content_window(win, text)
        
        # 底部按鈕
        btn_frame = tk.Frame(win, bg="#0B1D39")
        btn_frame.pack(fill=tk.X)
        tk.Button(btn_frame, text="複製全部", command=lambda: self._copy_to_clipboard(merged)).pack(side=tk.LEFT, padx=6, pady=6)
        tk.Button(btn_frame, text="關閉", command=win.destroy).pack(side=tk.RIGHT, padx=6, pady=6)

    def _build_cmd_resp_summary_and_label(self, content: str):
        """回傳 (summary_text, step_label)"""
        try:
            import re
            groups = []
            current = None
            step_label = None
            for raw in content.splitlines():
                # 去掉可能的行號前綴 "   1. "
                line = re.sub(r'^\s*\d+\.\s*', '', raw)
                # 嘗試抓步驟標題（行內包含 Do @STEPxxx@）
                if step_label is None and 'Do @STEP' in line:
                    try:
                        pos = line.index('Do @STEP')
                        step_label = line[pos:].strip()
                    except Exception:
                        step_label = line.strip()
                m_cmd = re.search(r'>\s*(.+)$', line)
                m_resp = re.search(r'<\s*(.*)$', line)
                if m_cmd:
                    if current:
                        groups.append(current)
                    current = {'cmd': m_cmd.group(1), 'resps': []}
                    continue
                if m_resp:
                    if not current:
                        current = {'cmd': '', 'resps': []}
                    current['resps'].append(m_resp.group(1))
            if current:
                groups.append(current)
            count = len(groups)
            header = "[指令/回應整理]" if step_label is None else f"{step_label}    [指令/回應整理 {count}筆]"
            out_lines = [header] if step_label else [f"[指令/回應整理 {count}筆]"]
            if not groups:
                out_lines.append("(未偵測到 >/< 指令或回應)")
                return ("\n".join(out_lines), step_label)
            for idx, g in enumerate(groups, 1):
                out_lines.append(f"指令{idx}.")
                out_lines.append(f"> {g.get('cmd','')}")
                for r in g.get('resps', []):
                    out_lines.append(f"< {r}")
                out_lines.append("")
            return ("\n".join(out_lines).rstrip(), step_label)
        except Exception:
            return ("[指令/回應整理]\n(產生摘要時發生例外)", None)

    def _build_cmd_resp_summary(self, content: str) -> str:
        """從內容中擷取所有 > 與其後續的 < 行，條列 1,2,3... 顯示"""
        try:
            summary, _ = self._build_cmd_resp_summary_and_label(content)
            return summary
        except Exception:
            return "[指令/回應整理]\n(產生摘要時發生例外)"

    def _on_pass_tree_hover(self, event):
        """PASS TreeView懸停事件"""
        self._handle_tree_hover(event, self.pass_tree, self._pass_full_map, target_col='#3', title='測項指令內容 (PASS)')

    def _on_fail_tree_hover(self, event):
        """FAIL TreeView懸停事件"""
        self._handle_tree_hover(event, self.fail_tree, self._fail_full_map, target_col='#3', title='測項指令內容 (FAIL)')

    def _handle_tree_hover(self, event, tree, content_map, target_col='#3', title='內容'):
        """處理TreeView懸停事件"""
        # 放寬條件：整列只要有完整內容即可顯示
        row = tree.identify_row(event.y)
        if not row:
            self._hover_row = None
            self._hide_hover_popup()
            return
        content = content_map.get(row)
        if not content:
            # 該列沒有可展開內容
            if self._hover_row != row:
                self._hover_row = None
                self._hide_hover_popup()
            return
        # 位置計算 - 檢查是否靠近下方
        abs_x = tree.winfo_rootx() + event.x + 12
        abs_y = tree.winfo_rooty() + event.y + 12
        
        # 檢查是否靠近螢幕下方，如果是則往上顯示
        screen_height = tree.winfo_screenheight()
        popup_height = 400
        if abs_y + popup_height > screen_height - 50:  # 距離底部50像素時往上顯示
            abs_y = screen_height - popup_height - 50
        
        if self._hover_row == row and self._hover_popup and self._hover_popup.winfo_exists():
            try:
                self._hover_popup.geometry(f"700x400+{abs_x}+{abs_y}")
            except Exception:
                pass
            return
        # 顯示或更新內容
        self._hover_row = row
        self._show_hover_popup(title, content, abs_x, abs_y)

    def _show_hover_popup(self, title, content, x, y):
        """顯示懸停彈窗"""
        # 若已有彈窗，更新位置與內容
        if self._hover_popup and self._hover_popup.winfo_exists():
            try:
                self._hover_text.config(state=tk.NORMAL)
                self._hover_text.delete('1.0', tk.END)
                self._hover_text.insert('1.0', content)
                self._hover_text.config(font=('Consolas', self.font_size))
                self._hover_popup.geometry(f"700x400+{x}+{y}")
                # 重新應用語法高亮
                self._apply_syntax_highlighting(self._hover_text, content)
                return
            except Exception:
                try:
                    self._hover_popup.destroy()
                except Exception:
                    pass
                self._hover_popup = None
        # 建立新彈窗
        self._hover_popup = tk.Toplevel(self.root)
        self._hover_popup.overrideredirect(True)
        self._hover_popup.attributes('-topmost', True)
        self._hover_popup.geometry(f"700x400+{x}+{y}")
        # 框架與文字
        frame = tk.Frame(self._hover_popup, bd=1, relief=tk.SOLID)
        frame.pack(fill=tk.BOTH, expand=1)
        text = tk.Text(frame, wrap=tk.NONE, font=('Consolas', self.font_size))
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
        # 應用語法高亮
        self._apply_syntax_highlighting(text, content)
        # 互斥關閉：離開彈窗或TreeView即自動關閉
        self._hover_popup.bind('<Leave>', lambda e: self._hide_hover_popup())
        self._hover_text = text

    def _hide_hover_popup(self):
        """隱藏懸停彈窗"""
        if getattr(self, '_hover_popup', None) and self._hover_popup.winfo_exists():
            try:
                self._hover_popup.destroy()
            except Exception:
                pass
        self._hover_popup = None
        self._hover_row = None

    def _copy_to_clipboard(self, content):
        """複製內容到剪貼簿"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(str(content))
        except Exception:
            pass

    def _apply_syntax_highlighting(self, text_widget, content):
        """對詳細內容應用語法高亮"""
        try:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                line_start = f"{i+1}.0"
                line_end = f"{i+1}.end"
                
                # UART指令 - 藍色
                if '(UART) >' in line or '> ' in line:
                    text_widget.tag_add('cmd', line_start, line_end)
                    text_widget.tag_configure('cmd', foreground='blue', font=('Consolas', self.font_size, 'bold'))
                
                # UART回應 - 紫色
                elif '(UART) <' in line or '< ' in line:
                    text_widget.tag_add('resp', line_start, line_end)
                    text_widget.tag_configure('resp', foreground='purple')
                
                # 錯誤行 - 紅色
                elif any(keyword in line.upper() for keyword in ['FAIL', 'ERROR', 'NACK']):
                    text_widget.tag_add('error', line_start, line_end)
                    text_widget.tag_configure('error', foreground='red', font=('Consolas', self.font_size, 'bold'))
                
                # Step行 - 綠色
                elif 'Do @STEP' in line or '@STEP' in line:
                    text_widget.tag_add('step', line_start, line_end)
                    text_widget.tag_configure('step', foreground='green', font=('Consolas', self.font_size, 'bold'))
                
                # PASS - 綠色
                elif 'PASS' in line.upper():
                    text_widget.tag_add('pass', line_start, line_end)
                    text_widget.tag_configure('pass', foreground='green', font=('Consolas', self.font_size, 'bold'))
        except Exception as e:
            print(f"語法高亮應用失敗: {e}")

    def _apply_font_size(self):
        """套用字體大小"""
        self.font_scaler.set_font_size(self.font_size)
        self.font_size_label.config(text=f"目前字體：{self.font_size}")

    def _increase_font(self):
        """增加字體大小"""
        if self.font_size < 15:
            self.font_size += 1
            self._apply_font_size()

    def _decrease_font(self):
        """減少字體大小"""
        if self.font_size > 10:
            self.font_size -= 1
            self._apply_font_size()

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
        default_dir = self._get_default_directory()
        file_path = filedialog.askopenfilename(
            title="選擇Log檔案", 
            filetypes=[("Log檔案", "*.log"), ("所有檔案", "*.*")],
            initialdir=default_dir
        )
        if file_path:
            self.current_mode = 'single'
            self.current_log_path = file_path
            self.analyze_btn.config(state=tk.NORMAL)
            # 自動開始分析
            self._analyze_log()

    def _select_folder(self):
        """選擇資料夾"""
        default_dir = self._get_default_directory()
        folder_path = filedialog.askdirectory(
            title="選擇Log資料夾",
            initialdir=default_dir
        )
        if folder_path:
            self.current_mode = 'multi'
            self.current_log_path = folder_path
            self.analyze_btn.config(state=tk.NORMAL)
            messagebox.showinfo("資料夾已選擇", f"已選擇資料夾：\n{os.path.basename(folder_path)}")

    def _select_script(self):
        """選擇測試腳本"""
        default_dir = self._get_default_directory()
        script_path = filedialog.askopenfilename(
            title="選擇測試腳本Excel檔案", 
            filetypes=[("Excel檔案", "*.xlsx"), ("Excel檔案", "*.xls"), ("所有檔案", "*.*")],
            initialdir=default_dir
        )
        if script_path:
            self.script_path = script_path
            self.script_label.config(text=f"已選擇：{os.path.basename(script_path)}", fg="green")
            messagebox.showinfo("腳本已選擇", f"已選擇腳本：\n{os.path.basename(script_path)}")

    def _analyze_log(self):
        """分析log檔案並更新GUI顯示"""
        if not self.current_log_path:
            messagebox.showwarning("警告", "請先選擇log檔案或資料夾")
            return
            
        # 清空現有內容
        self.pass_tree.delete(*self.pass_tree.get_children())
        self.fail_tree.delete(*self.fail_tree.get_children())
        self.script_tree.delete(*self.script_tree.get_children())
        self.log_text.delete(1.0, tk.END)
        self._pass_full_map.clear()
        self._fail_full_map.clear()
        
        try:
            # 載入腳本（如果有選擇）
            script_data = None
            if self.script_path and os.path.exists(self.script_path):
                script_data = self._load_script_excel(self.script_path)
            
            # 分析log
            if self.current_mode == 'single':
                self._analyze_single_file(script_data)
            else:
                self._analyze_multiple_files(script_data)
                
        except Exception as e:
            messagebox.showerror("分析錯誤", f"分析過程中發生錯誤：\n{str(e)}")

    def _analyze_single_file(self, script_data):
        """分析單一檔案"""
        result = self.log_parser.parse_log_file(self.current_log_path)
        pass_items = result['pass_items']
        fail_items = result['fail_items']
        raw_lines = result['raw_lines']
        last_fail = result['last_fail']
        fail_line_idx = result['fail_line_idx']
        
        # Tab1: PASS - 顯示所有通過的測項
        for item in pass_items:
            display_resp = item['response'] + ('  [+點擊詳細]' if item.get('full_response') else '')
            iid = self.pass_tree.insert('', 'end', values=(item['step_name'], item['command'], display_resp, item['result']))
            if item.get('full_response'):
                self._pass_full_map[iid] = item['full_response']
        
        # Tab2: FAIL - 顯示所有FAIL區塊（第一個為主要FAIL，其餘為歷史FAIL）
        for idx, item in enumerate(fail_items):
            step_name = item.get('step_name', '')
            display_resp = item.get('response', '') + ('  [+點擊詳細]' if item.get('full_response') else '')
            command = item.get('command', '')
            iid = self.fail_tree.insert('', 'end', values=(step_name, command, display_resp, item.get('retry',0), item.get('error','')))
            
            # 標色：檢查是否有未找到指令的情況
            if idx == 0 or item.get('is_main_fail', False):
                if '未找到指令' in command:
                    # 未找到指令用黑色
                    self.fail_tree.tag_configure('fail_main_black', foreground='black')
                    self.fail_tree.item(iid, tags=('fail_main_black',))
                else:
                    # 正常FAIL用紅色
                    self.fail_tree.tag_configure('fail_main', foreground='red')
                    self.fail_tree.item(iid, tags=('fail_main',))
            else:
                # 歷史FAIL用橘色
                self.fail_tree.tag_configure('fail_hist', foreground='#CC6600')
                self.fail_tree.item(iid, tags=('fail_hist',))
            
            if item.get('full_response'):
                self._fail_full_map[iid] = item['full_response']
        
        # Tab3: 原始LOG，標紅錯誤行並自動跳轉（單一檔案模式）
        self._show_log_with_highlight(raw_lines, fail_line_idx)
        
        # Tab4: 腳本比對（如果有載入腳本）
        if script_data:
            self._compare_with_script(pass_items, fail_items, script_data)
        
        # 單一檔案模式禁用Excel匯出
        self.export_btn.config(state=tk.DISABLED)
        
        # 自動切換到相關Tab
        if fail_items:
            self.notebook.select(self.tab_fail)
        else:
            self.notebook.select(self.tab_pass)

    def _analyze_multiple_files(self, script_data):
        """分析多個檔案"""
        result = self.log_parser.parse_log_folder(self.current_log_path)
        pass_items = result['pass_items']
        fail_items = result['fail_items']
        
        # Tab1: PASS - 顯示所有通過的測項
        for item in pass_items:
            display_resp = item['response'] + ('  [+點擊詳細]' if item.get('full_response') else '')
            iid = self.pass_tree.insert('', 'end', values=(item['step_name'], item['command'], display_resp, item['result']))
            if item.get('full_response'):
                self._pass_full_map[iid] = item['full_response']
        
        # Tab2: FAIL - 顯示所有失敗的測項
        for item in fail_items:
            display_resp = item.get('response','') + ('  [+點擊詳細]' if item.get('full_response') else '')
            iid = self.fail_tree.insert('', 'end', values=(item['step_name'], item['command'], display_resp, item['retry'], item['error']))
            if item.get('full_response'):
                self._fail_full_map[iid] = item['full_response']
        
        # Tab3: 腳本比對（如果有載入腳本）
        if script_data:
            self._compare_with_script(pass_items, fail_items, script_data)
        
        # Tab3: 清空原始LOG（多檔案模式不顯示原始內容）
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, "多檔案分析模式：請查看PASS/FAIL分頁檢視結果")
        
        # Tab4: 腳本比對（如果有載入腳本）
        if script_data:
            self._compare_with_script(pass_items, fail_items, script_data)
        
        # 多檔案模式啟用Excel匯出
        self.export_btn.config(state=tk.NORMAL if (pass_items or fail_items) else tk.DISABLED)
        
        # 自動切換到PASS分頁
        self.notebook.select(self.tab_pass)

    def _show_log_with_highlight(self, lines, fail_line_idx):
        """顯示原始LOG並高亮錯誤行"""
        self.log_text.delete(1.0, tk.END)
        for idx, line in enumerate(lines):
            self.log_text.insert(tk.END, line + '\n')
        if fail_line_idx is not None:
            # 標紅該行
            start = f"{fail_line_idx+1}.0"
            end = f"{fail_line_idx+1}.end"
            self.log_text.tag_add('fail', start, end)
            self.log_text.tag_config('fail', foreground='red', background='#ffecec')
            # 自動跳轉
            self.log_text.see(start)

    def _export_excel(self):
        """匯出分析結果到Excel檔案"""
        if self.current_mode != 'multi':
            messagebox.showwarning("警告", "單一檔案模式不支援匯出Excel")
            return
        
        # 取得目前的分析結果
        result = self.log_parser.parse_log_folder(self.current_log_path)
        pass_items = result['pass_items']
        fail_items = result['fail_items']
        
        if not pass_items and not fail_items:
            messagebox.showwarning("警告", "沒有分析結果可匯出")
            return
        
        # 選擇儲存位置
        file_path = filedialog.asksaveasfilename(
            title="儲存Excel檔案",
            defaultextension=".xlsx",
            filetypes=[("Excel檔案", "*.xlsx"), ("所有檔案", "*.*")]
        )
        
        if file_path:
            try:
                self.excel_writer.export(pass_items, fail_items, file_path)
                messagebox.showinfo("成功", f"Excel檔案已儲存至：\n{file_path}")
            except Exception as e:
                messagebox.showerror("錯誤", f"匯出Excel失敗：\n{str(e)}")

    def _load_script_excel(self, script_path):
        """載入測試腳本Excel檔案"""
        try:
            import pandas as pd
            df = pd.read_excel(script_path)
            # 假設第一欄是Test ID
            test_ids = df.iloc[:, 0].dropna().tolist()
            return test_ids
        except Exception as e:
            messagebox.showerror("錯誤", f"載入腳本失敗：\n{str(e)}")
            return None

    def _compare_with_script(self, pass_items, fail_items, script_data):
        """比對腳本與實際執行結果"""
        if not script_data:
            return
        
        # 清空腳本比對結果
        self.script_tree.delete(*self.script_tree.get_children())
        
        # 收集所有執行的測試ID
        all_executed_ids = set()
        for item in pass_items:
            test_id = self._extract_test_id(item['step_name'])
            if test_id:
                all_executed_ids.add(test_id)
        for item in fail_items:
            test_id = self._extract_test_id(item['step_name'])
            if test_id:
                all_executed_ids.add(test_id)
        
        # 腳本中的測試ID
        script_ids = set(script_data)
        
        # 顯示比對結果
        for test_id in script_ids:
            if test_id in all_executed_ids:
                # 檢查是否為FAIL
                is_fail = any(
                    self._extract_test_id(item['step_name']) == test_id 
                    for item in fail_items
                )
                if is_fail:
                    status = "❌ FAIL"
                    note = "已執行但失敗"
                    tag = 'fail'
                else:
                    status = "✅ PASS"
                    note = "已執行且通過"
                    tag = 'pass'
            else:
                status = "⚠️ NOT EXECUTED"
                note = "腳本中有但未執行"
                tag = 'not_executed'
            
            iid = self.script_tree.insert('', 'end', values=(test_id, status, note))
            
            # 設定顏色標籤
            if tag == 'fail':
                self.script_tree.tag_configure('fail', foreground='red')
                self.script_tree.item(iid, tags=('fail',))
            elif tag == 'not_executed':
                self.script_tree.tag_configure('not_executed', foreground='orange')
                self.script_tree.item(iid, tags=('not_executed',))
        
        # 顯示額外執行的測試（在log中但不在腳本中）
        extra_executed = all_executed_ids - script_ids
        for test_id in extra_executed:
            status = "➕ EXTRA"
            note = "執行但腳本中沒有"
            iid = self.script_tree.insert('', 'end', values=(test_id, status, note))
            self.script_tree.tag_configure('extra', foreground='blue')
            self.script_tree.item(iid, tags=('extra',))

    def _extract_test_id(self, step_name):
        """從測項名稱中提取測試ID（簡化版）"""
        import re
        # 尋找類似 B7PL025-002 的模式
        match = re.search(r'[A-Z0-9]+-\d+', step_name)
        if match:
            return match.group(0)
        return None

    def _open_markdown_help(self):
        """開啟並顯示 dioc/README.md 內容"""
        try:
            from ui_components import get_resource_path
            md_path = get_resource_path(os.path.join('dioc', 'README.md'))
            content = ''
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                # 若 README.md 不存在，嘗試 QUICK_START.md
                alt_path = get_resource_path(os.path.join('dioc', 'QUICK_START.md'))
                with open(alt_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            self._show_text_viewer_window("README 說明", content)
        except Exception as e:
            try:
                messagebox.showerror("錯誤", f"無法讀取說明：{e}")
            except Exception:
                pass

    def _auto_resize_content_window(self, win, text_widget):
        """根據文字內容自動調整內容視窗大小，確保導航按鈕始終可見"""
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
            print(f"自動調整內容視窗大小失敗: {e}")

    def _show_text_viewer_window(self, title: str, content: str):
        """顯示純文字的查看視窗（簡易Markdown檢視）"""
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
        text = tk.Text(frame, wrap=tk.WORD)
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
        self._auto_resize_content_window(win, text)

def main():
    """標準版主程式"""
    root = tk.Tk()
    app = LogAnalyzerApp(root)
    root.mainloop()

if __name__ == '__main__':
    main() 