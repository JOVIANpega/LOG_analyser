#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試Log分析器GUI應用程式 - 增強版 (模組化重構)
提供現代化的圖形使用者介面來分析測試log檔案
整合 ConfigManager, ProgressManager, AnalysisEngine, UIBuilder, SearchHandler, ResultDisplay 等模組
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import threading
import shutil

# Import modules and mixins
from .config_manager import ConfigManager
from .progress_manager import ProgressManager
from .search_handler import SearchHandlerMixin
from .result_display import ResultDisplayMixin
from .analysis_engine import AnalysisEngineMixin
from .ui_builder import UIBuilderMixin
from .file_handlers import FileHandlerMixin

from .log_parser import LogParser
from .excel_writer import ExcelWriter
from .ui_components import FontScaler

class EnhancedLogAnalyzerApp(FileHandlerMixin, SearchHandlerMixin, ResultDisplayMixin, 
                           AnalysisEngineMixin, UIBuilderMixin):
    """增強版LOG分析器應用程式"""
    
    def __init__(self, root):
        """初始化增強版應用程式"""
        self.root = root
        
        # 1. Config Manager & Settings
        self.config_manager = ConfigManager(root)
        if not self.config_manager.check_encryption():
            return
            
        self.settings = self.config_manager.settings
        
        # Apply window settings
        self.config_manager.load_window_geometry()
        from .version import VERSION
        app_title = self.config_manager.get('app_title', 'PEGA test log Analyser')
        self.root.title(f"{app_title} {VERSION}")
        
        # Load font settings
        self.ui_font_size = self.config_manager.get('ui_font_size', 11)
        self.content_font_size = self.config_manager.get('content_font_size', 11)
        
        # 2. Managers & Components
        self.progress_manager = ProgressManager(root)
        self.font_scaler = FontScaler(root, default_size=self.ui_font_size)
        self.log_parser = LogParser()
        self.excel_writer = ExcelWriter()
        
        # 3. State Variables
        self.current_mode = 'single'
        self.current_log_path = ''
        self.temp_cleanup_path = None
        self._cancel_flag = False
        self._search_cache = {'text': '', 'count': 0}
        
        # 4. Build UI (UIBuilderMixin)
        self._build_enhanced_ui()
        self._apply_font_size()
        
        # Connect Progress Manager to Status Bar
        if hasattr(self, 'status_label') and hasattr(self, 'main_progress_bar'):
            header_label_widget = getattr(self, 'left_title_label', None)
            header_frame_widget = getattr(self, 'left_title_frame', None)
            percentage_label_widget = getattr(self, 'percentage_label', None)
            self.progress_manager.set_widgets(
                self.status_label, 
                self.main_progress_bar, 
                header_label_widget,
                header_frame_widget,
                percentage_label_widget
            )
        
        # Events
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # 🎯 核心懸停連動：直接綁定 Motion 事件，確保即時預覽 (不依賴回調)
        if hasattr(self, 'fail_tree_enhanced'):
            self._fail_hover_after_id = None # 用於延遲觸發的 ID
            self._last_fail_hover_item = None
            
            # 強制重新綁定 Motion 事件 (add='+' 確保不衝突)
            self.fail_tree_enhanced.tree.bind('<Motion>', self._on_fail_tree_motion_direct, add='+')
            # 點擊選擇也同步更新 (點擊是最高優先權，立即開發)
            self.fail_tree_enhanced.tree.bind('<<TreeviewSelect>>', self._on_fail_item_select_instant, add='+')

    def _on_fail_tree_motion_direct(self, event):
        """懸停處理：實作快速延遲預覽 (200ms)，確保流暢且不閃爍"""
        try:
            # 1. 識別目前滑鼠下的項目
            item = self.fail_tree_enhanced.tree.identify_row(event.y)
            
            # 2. 如果滑鼠離開項目，取消待處理計時
            if not item:
                if getattr(self, '_fail_hover_after_id', None):
                    self.root.after_cancel(self._fail_hover_after_id)
                    self._fail_hover_after_id = None
                self._last_fail_hover_item = None
                return
                
            # 3. 如果還在同一個項目上，不需要重複計時
            if item == getattr(self, '_last_fail_hover_item', None):
                return
            
            # 4. 取消之前的計時器
            if getattr(self, '_fail_hover_after_id', None):
                self.root.after_cancel(self._fail_hover_after_id)
            
            self._last_fail_hover_item = item
            
            # 5. 排除 Phase Header (藍色條)
            tags = self.fail_tree_enhanced.tree.item(item, 'tags')
            if 'phase_header' in tags:
                self._fail_hover_after_id = None
                return 
            
            # 6. 設定 200ms 延遲觸發 (比 1 秒快得多，幾乎即時但有防抖)
            def trigger_preview():
                self._display_fail_reason_for_item(item)
                self._fail_hover_after_id = None

            self._fail_hover_after_id = self.root.after(200, trigger_preview)
            
        except Exception:
            pass 

    def _on_fail_item_select_instant(self, event):
        """點擊選擇時：立即更新，並取消任何待處理的延遲懸停"""
        if getattr(self, '_fail_hover_after_id', None):
            self.root.after_cancel(self._fail_hover_after_id)
            self._fail_hover_after_id = None
        
        selection = self.fail_tree_enhanced.tree.selection()
        if selection:
            item_id = selection[0]
            self._last_fail_hover_item = item_id # 防止懸停重複觸發
            self._display_fail_reason_for_item(item_id)

    def _apply_font_size(self):
        """應用字體設定並更新介面"""
        if hasattr(self, 'font_scaler'):
            self.font_scaler.set_font_size(self.ui_font_size)
        
        # 1. 更新設定頁面中的數字顯示
        if hasattr(self, 'settings_ui_font_size_label'):
            self.settings_ui_font_size_label.config(text=str(self.ui_font_size))
        if hasattr(self, 'settings_content_font_size_label'):
            self.settings_content_font_size_label.config(text=str(self.content_font_size))
            
        # 2. 更新 Text 編輯器字體
        if hasattr(self, 'log_text_enhanced') and hasattr(self.log_text_enhanced, 'text'):
             self.log_text_enhanced.text.configure(font=('Consolas', self.content_font_size))
             
        if hasattr(self, 'fail_error_text'):
             self.fail_error_text.configure(font=('Consolas', 12))
             
        # 3. 更新 Treeview 
        if hasattr(self, 'result_tree'):
            self.font_scaler.apply_to_treeview(self.result_tree.tree)

    def _cleanup_temp_files_async(self):
        """非同步清理暫存檔案"""
        if self.temp_cleanup_path and os.path.exists(self.temp_cleanup_path):
            path = self.temp_cleanup_path
            def _clean():
                try:
                    shutil.rmtree(path, ignore_errors=True)
                except Exception:
                    pass
            threading.Thread(target=_clean, daemon=True).start()

    def _on_closing(self):
        """處理視窗關閉事件"""
        try:
            # Save settings via ConfigManager
            self.config_manager.save_window_geometry()
            
            # Save other settings
            self.config_manager.set('ui_font_size', self.ui_font_size)
            self.config_manager.set('content_font_size', self.content_font_size)
            self.config_manager.set('last_log_path', self.settings.get('last_log_path'))
            self.config_manager.set('last_folder_path', self.settings.get('last_folder_path'))
            self.config_manager.set('last_compressed_path', self.settings.get('last_compressed_path'))
            self.config_manager.set('last_compressed_folder', self.settings.get('last_compressed_folder'))
            
            if hasattr(self, 'auto_analyze_var'):
                self.config_manager.set('auto_analyze', self.auto_analyze_var.get())
            if hasattr(self, 'remember_path_var'):
                 self.config_manager.set('remember_path', self.remember_path_var.get())
            if hasattr(self, 'skip_no_test_time_var'):
                 self.config_manager.set('skip_no_test_time', self.skip_no_test_time_var.get())
            if hasattr(self, 'show_hover_preview_var'):
                 self.config_manager.set('show_hover_preview', self.show_hover_preview_var.get())
                 
            self.config_manager.save()
            print("設定已保存")
            
        except Exception as e:
            print(f"保存設定失敗: {e}")
            
        self._cancel_flag = True
        self._cleanup_temp_files_async()
        self.root.destroy()
    
    # === Delegate Methods for ProgressManager ===
    def _show_progress(self, title, message=""):
        self.root.after(0, lambda: self.progress_manager.show_progress(title, message))
        
    def _update_progress(self, text):
         self.root.after(0, lambda: self.progress_manager.update_progress(text))
         
    def _close_progress(self):
        self.root.after(0, self.progress_manager.close_progress)
        
    def _progress_set_determinate(self, maximum):
        self.root.after(0, lambda: self.progress_manager.set_determinate(maximum))
        
    def _progress_set_value(self, current, total):
        self.root.after(0, lambda: self.progress_manager.set_value(current, total))
        
    def _safe_update_progress_mode(self, mode):
        """Thread-safe: Set progress mode"""
        if mode == 'determinate':
             self.root.after(0, lambda: self.progress_manager.set_determinate(100))
        else:
             self.root.after(0, self.progress_manager.set_indeterminate)

    def _safe_update_progress_max(self, total):
        """Thread-safe: Set progress maximum"""
        self.root.after(0, lambda: self.progress_manager.set_determinate(total))

    def _safe_update_progress(self, current, total, text):
        """Thread-safe: Update progress value and text"""
        self.root.after(0, lambda: self.progress_manager.set_value(current, total))
        if text:
            self.root.after(0, lambda: self.progress_manager.update_progress(text))

    def _safe_update_progress_text(self, text):
        """Thread-safe: Update progress text only"""
        self.root.after(0, lambda: self.progress_manager.update_progress(text))

    def _save_settings_silent(self):
        self.config_manager.save()

    def _on_theme_change(self, event=None):
        """當主題選擇改變時"""
        theme_name = self.theme_var.get()
        # 使用 ttkbootstrap 視窗內建的 style 進行切換
        if hasattr(self.root, 'style'):
            self.root.style.theme_use(theme_name)
        else:
            import ttkbootstrap as ttk
            ttk.Style().theme_use(theme_name)
        
        # 4. 標題背景也需要同步更新 (因為它是特殊的 tk.Frame)
        try:
            import ttkbootstrap as ttk
            colors = ttk.Style().colors
            header_bg = colors.primary
            header_fg = colors.inversefg if hasattr(colors, 'inversefg') else 'white'
            if hasattr(self, 'left_title_label'):
                self.left_title_label.config(bg=header_bg, fg=header_fg)
            if hasattr(self, 'left_title_frame'):
                self.left_title_frame.config(bg=header_bg)
        except:
            pass
            
        # 5. 主題切換後強制重新套用字體大小，確保樣式刷新
        self._apply_font_size()
            
    def _save_settings(self):
        """手動保存所有設定"""
        try:
            # 更新其他設定值
            if hasattr(self, 'version_var'):
                 self.config_manager.set('version', self.version_var.get())
            if hasattr(self, 'theme_var'):
                 self.config_manager.set('theme', self.theme_var.get())
            if hasattr(self, 'auto_analyze_var'):
                 self.config_manager.set('auto_analyze', self.auto_analyze_var.get())
            if hasattr(self, 'remember_path_var'):
                 self.config_manager.set('remember_path', self.remember_path_var.get())
            if hasattr(self, 'skip_no_test_time_var'):
                 self.config_manager.set('skip_no_test_time', self.skip_no_test_time_var.get())
            
            # 保存
            self.config_manager.save()
            messagebox.showinfo("成功", "設定已保存！")
            
            # 更新標題版本
            app_title = self.config_manager.get('app_title', 'PEGA test log Aanlyser')
            version = self.config_manager.get('version', 'V1.5.6')
            self.root.title(f"{app_title} {version}")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"保存設定失敗: {e}")
