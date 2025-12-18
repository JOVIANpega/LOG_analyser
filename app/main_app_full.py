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
        app_title = self.config_manager.get('app_title', 'PEGA test log Aanlyser')
        version = self.config_manager.get('version', 'V1.5.6')
        self.root.title(f"{app_title} {version}")
        
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
            # Check for optional status_light and left_title_label
            status_light_widget = getattr(self, 'status_light', None)
            header_label_widget = getattr(self, 'left_title_label', None)
            self.progress_manager.set_widgets(
                self.status_label, 
                self.main_progress_bar, 
                status_light_widget,
                header_label_widget
            )
        
        # Events
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _apply_font_size(self):
        """應用字體設定"""
        if hasattr(self, 'font_scaler'):
            self.font_scaler.set_font_size(self.ui_font_size)
        
        # 更新設定頁面中的數字顯示
        if hasattr(self, 'settings_ui_font_size_label'):
            self.settings_ui_font_size_label.config(text=str(self.ui_font_size))
        if hasattr(self, 'settings_content_font_size_label'):
            self.settings_content_font_size_label.config(text=str(self.content_font_size))
            
        # 更新某些特定元件的字體
        style = ttk.Style()
        style.configure('TNotebook.Tab', font=('Arial', self.ui_font_size))
        
        # Update text widgets if they exist
        if hasattr(self, 'log_text_enhanced') and hasattr(self.log_text_enhanced, 'text'):
             self.log_text_enhanced.text.configure(font=('Consolas', self.content_font_size))
             
        if hasattr(self, 'fail_error_text'):
             self.fail_error_text.configure(font=('Consolas', 12)) # Fixed size or scaled?

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
                 
            self.config_manager.save()
            print("設定已保存")
            
        except Exception as e:
            print(f"保存設定失敗: {e}")
            
        self._cancel_flag = True
        self._cleanup_temp_files_async()
        self.root.destroy()
    
    # === Delegate Methods for ProgressManager ===
    def _show_progress(self, title, message=""):
        self.progress_manager.show_progress(title, message)
        
    def _update_progress(self, text):
         self.progress_manager.update_progress(text)
         
    def _close_progress(self):
        self.progress_manager.close_progress()
        
    def _progress_set_determinate(self, maximum):
        self.progress_manager.set_determinate(maximum)
        
    def _progress_set_value(self, current, total):
        self.progress_manager.set_value(current, total)
        
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

    def _save_settings(self):
        """手動保存所有設定"""
        try:
            # 更新其他設定值
            if hasattr(self, 'version_var'):
                 self.config_manager.set('version', self.version_var.get())
            if hasattr(self, 'auto_analyze_var'):
                 self.config_manager.set('auto_analyze', self.auto_analyze_var.get())
            if hasattr(self, 'remember_path_var'):
                 self.config_manager.set('remember_path', self.remember_path_var.get())
            
            # 保存
            self.config_manager.save()
            messagebox.showinfo("成功", "設定已保存！")
            
            # 更新標題版本
            app_title = self.config_manager.get('app_title', 'PEGA test log Aanlyser')
            version = self.config_manager.get('version', 'V1.5.6')
            self.root.title(f"{app_title} {version}")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"保存設定失敗: {e}")
