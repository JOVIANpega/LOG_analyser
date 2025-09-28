#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試Log分析器GUI應用程式 - 增強版 (修正搜尋功能)
提供現代化的圖形使用者介面來分析測試log檔案
支援雙字體控制、視窗大小記憶、預覽視窗等功能
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import json
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
        # 先載入設定再設定標題
        self.settings = load_settings()
        app_title = self.settings.get('app_title', 'PEGA test log Aanlyser')
        version = self.settings.get('version', 'V1.5.6')
        self.root.title(f"{app_title} {version}")
        
        # 載入設定（其餘）
        self.ui_font_size = self.settings.get('ui_font_size', 11)
        self.content_font_size = self.settings.get('content_font_size', 11)
        
        # 設定視窗大小
        window_width = self.settings.get('window_width', 1400)
        window_height = self.settings.get('window_height', 900)
        self.root.geometry(f"{window_width}x{window_height}")
        
        # 初始化模組
        self.font_scaler = FontScaler(root, default_size=self.ui_font_size)
        self.log_parser = LogParser()
        self.excel_writer = ExcelWriter()
        
        # 狀態變數
        self.current_mode = 'single'
        self.current_log_path = ''
        self.temp_cleanup_path = None  # 壓縮檔解壓縮的暫存路徑
        
        # 建立UI
        self._build_enhanced_ui()
        self._apply_font_size()
        
        # 綁定視窗關閉事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
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
        
        # 清理壓縮檔解壓縮的暫存檔案
        self._cleanup_temp_files()
        
        self.root.destroy()
    
    def _build_enhanced_ui(self):
        """建立增強版UI"""
        # 主要分割視窗
        self.paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        self.paned.pack(fill=tk.BOTH, expand=1)
        
        # 左側控制面板
        self.left_frame = tk.Frame(self.paned, bg='#F0F0F0', width=300)
        self.paned.add(self.left_frame, minsize=250)
        
        # 右側內容面板
        self.right_frame = tk.Frame(self.paned)
        self.paned.add(self.right_frame, minsize=400)
        
        # 分割視窗位置設定
        pane_width = self.settings.get('pane_width', 300)
        self.root.after(100, lambda: self.paned.sash_place(0, pane_width, 0))
        
        # 建立左側面板內容
        build_left_panel(self.left_frame, self)
        
        # 建立右側面板內容
        self._build_enhanced_right_panel(self.right_frame)
    
    def _build_enhanced_right_panel(self, parent):
        """建立增強版右側面板"""
        # 檔案資訊標籤（置於最上方）
        self.file_info_label = tk.Label(parent, text="尚未選擇檔案", font=('Arial', 10), 
                                      fg='gray', anchor='w', justify='left', wraplength=600)
        self.file_info_label.pack(fill=tk.X, padx=10, pady=5)
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
                            ('!active', '#1565C0'),      # 非活動：深藍底
                            ('!selected', '#1565C0')],   # 未選中：深藍底
                 foreground=[('selected', 'white'),      # 選中：白字
                            ('active', 'white'),         # hover：白字
                            ('!active', 'white'),        # 非活動：白字
                            ('!selected', 'white')])     # 未選中：白字
    
    def _build_enhanced_pass_tab(self):
        """建立PASS標籤頁"""
        self.tab_pass = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_pass, text="✅ PASS測項")
        
        # 使用增強型TreeView
        pass_columns = ("Step", "指令", "回應", "結果")
        self.pass_tree_enhanced = EnhancedTreeview(self.tab_pass, pass_columns)
        self.pass_tree_enhanced.tree.pack(fill=tk.BOTH, expand=1)
    
    def _build_enhanced_fail_tab(self):
        """建立FAIL標籤頁 - 分割成上下兩個視窗"""
        self.tab_fail = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_fail, text="❌ FAIL測項")
        
        # 垂直分割視窗
        self.fail_paned = tk.PanedWindow(self.tab_fail, orient=tk.VERTICAL, sashrelief=tk.RAISED)
        self.fail_paned.pack(fill=tk.BOTH, expand=1)
        
        # 上方：FAIL測項列表
        self.fail_upper_frame = tk.Frame(self.fail_paned)
        fail_columns = ("Step", "指令", "錯誤回應", "Retry", "錯誤原因")
        self.fail_tree_enhanced = EnhancedTreeview(self.fail_upper_frame, fail_columns)
        self.fail_tree_enhanced.tree.pack(fill=tk.BOTH, expand=1)
        self.fail_paned.add(self.fail_upper_frame, minsize=150)
        
        # 下方：詳細錯誤內容
        self.fail_lower_frame = tk.Frame(self.fail_paned)
        
        # 錯誤詳細資訊標籤
        error_title = tk.Label(self.fail_lower_frame, text="🔍 詳細錯誤內容", 
                              font=('Arial', 12, 'bold'), fg='red', anchor='w')
        error_title.pack(fill=tk.X, padx=5, pady=(5, 2))
        self.font_scaler.register(error_title)
        
        # 錯誤內容文字框架
        error_text_frame = tk.Frame(self.fail_lower_frame)
        error_text_frame.pack(fill=tk.BOTH, expand=1, padx=5, pady=5)
        
        # 使用FailDetailsPanel來顯示詳細錯誤
        self.fail_details_panel = FailDetailsPanel(error_text_frame)
        self.fail_details_panel.grid(row=0, column=0, sticky='nsew')
        
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
        # 建立設定標籤頁
        self.tab_settings = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_settings, text="⚙️ 設定")
        
        # 建立設定內容
        build_settings_content(self.tab_settings, self)
    
    # 修改搜尋功能 - 使用內建的 Ctrl+F
    def _perform_search(self):
        """執行搜尋功能 - 使用內建搜尋"""
        try:
            search_text = self.search_var.get().strip()
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
                    # 使用內建的搜尋功能
                    self._trigger_builtin_search(search_text)
                else:
                    print("未找到原始LOG Text元件")
            else:
                print(f"未知標籤頁索引：{current_tab_index}，嘗試搜尋原始LOG...")
                if hasattr(self, 'log_text_enhanced') and hasattr(self.log_text_enhanced, 'text'):
                    self._trigger_builtin_search(search_text)
                
        except Exception as e:
            print(f"搜尋時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
    
    def _trigger_builtin_search(self, search_text):
        """觸發內建搜尋功能"""
        try:
            text_widget = self.log_text_enhanced.text
            
            # 設定搜尋變數
            if hasattr(self.log_text_enhanced, 'search_var'):
                self.log_text_enhanced.search_var.set(search_text)
            
            # 觸發內建搜尋對話框
            # 模擬Ctrl+F按鍵
            event = tk.Event()
            event.keysym = 'f'
            event.state = 4  # Control key
            self.log_text_enhanced._show_search_dialog(event)
            
            print(f"觸發內建搜尋：'{search_text}'")
            
        except Exception as e:
            print(f"觸發內建搜尋失敗: {e}")
            import traceback
            traceback.print_exc()
    
    def _search_next(self):
        """搜尋下一個匹配項目 - 使用內建功能"""
        try:
            search_text = self.search_var.get().strip()
            if not search_text:
                return
            
            # 檢查當前選中的標籤頁
            current_tab = self.notebook.select()
            current_tab_index = self.notebook.index(current_tab)
            
            if current_tab_index == 2:  # 原始LOG標籤頁
                if hasattr(self, 'log_text_enhanced') and hasattr(self.log_text_enhanced, 'text'):
                    # 使用內建的搜尋下一個功能
                    self._trigger_builtin_search_next()
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
        """搜尋上一個匹配項目 - 使用內建功能"""
        try:
            search_text = self.search_var.get().strip()
            if not search_text:
                return
            
            # 檢查當前選中的標籤頁
            current_tab = self.notebook.select()
            current_tab_index = self.notebook.index(current_tab)
            
            if current_tab_index == 2:  # 原始LOG標籤頁
                if hasattr(self, 'log_text_enhanced') and hasattr(self.log_text_enhanced, 'text'):
                    # 使用內建的搜尋上一個功能
                    self._trigger_builtin_search_prev()
                else:
                    print("未找到原始LOG Text元件")
            else:
                # 在其他標籤頁中搜尋
                self._perform_search()
                
        except Exception as e:
            print(f"搜尋上一個時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
    
    def _trigger_builtin_search_next(self):
        """觸發內建搜尋下一個功能"""
        try:
            if hasattr(self.log_text_enhanced, 'search_next'):
                self.log_text_enhanced.search_next()
            else:
                print("EnhancedText 沒有 search_next 方法")
        except Exception as e:
            print(f"觸發內建搜尋下一個失敗: {e}")
    
    def _trigger_builtin_search_prev(self):
        """觸發內建搜尋上一個功能"""
        try:
            if hasattr(self.log_text_enhanced, 'search_prev'):
                self.log_text_enhanced.search_prev()
            else:
                print("EnhancedText 沒有 search_prev 方法")
        except Exception as e:
            print(f"觸發內建搜尋上一個失敗: {e}")
    
    def _search_in_tree(self, tree_widget, search_text):
        """在TreeView中搜尋"""
        try:
            print(f"在TreeView中搜尋：'{search_text}'")
            
            # 清除之前的選取
            tree_widget.tree.selection_remove(tree_widget.tree.selection())
            
            # 遍歷所有項目
            for item in tree_widget.tree.get_children():
                values = tree_widget.tree.item(item, 'values')
                for value in values:
                    if search_text.lower() in str(value).lower():
                        # 找到匹配項目
                        tree_widget.tree.selection_set(item)
                        tree_widget.tree.focus(item)
                        tree_widget.tree.see(item)
                        print(f"找到匹配項目：{values}")
                        return
            
            print("未找到匹配項目")
            
        except Exception as e:
            print(f"TreeView搜尋時發生錯誤: {e}")
    
    def _clear_search(self):
        """清除搜尋結果"""
        try:
            # 清除搜尋框
            if hasattr(self, 'search_var'):
                self.search_var.set('')
            
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
            
            print("已清除搜尋結果")
            
        except Exception as e:
            print(f"清除搜尋時發生錯誤: {e}")
    
    def _on_search_change(self, event=None):
        """搜尋框內容變更時的處理"""
        # 可以選擇是否實時搜尋
        # self._perform_search()
        pass
    
    def _on_search_enter(self, event=None):
        """按下Enter鍵時執行搜尋"""
        self._perform_search()
    
    # 其餘方法保持不變...
    # (這裡包含所有其他的方法，為了節省空間省略)

def main_enhanced():
    """啟動增強版GUI應用程式"""
    root = tk.Tk()
    app = EnhancedLogAnalyzerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main_enhanced()
