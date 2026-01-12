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
            # 點擊/鍵盤選擇也同步更新 (立即顯示)
            self.fail_tree_enhanced.tree.bind('<<TreeviewSelect>>', self._on_fail_item_select_instant, add='+')
            
            # ⌨️ 鍵盤增強：當焦點在 Treeview 時，Ctrl+上下鍵/Page可以滾動下方 Detail
            self.fail_tree_enhanced.tree.bind('<Control-Up>', lambda e: self.fail_error_text.yview_scroll(-1, "units"))
            self.fail_tree_enhanced.tree.bind('<Control-Down>', lambda e: self.fail_error_text.yview_scroll(1, "units"))
            self.fail_tree_enhanced.tree.bind('<Control-Prior>', lambda e: self.fail_error_text.yview_scroll(-1, "pages"))
            self.fail_tree_enhanced.tree.bind('<Control-Next>', lambda e: self.fail_error_text.yview_scroll(1, "pages"))

        # 🟢 PASS 列表連動：點擊比對項目時跳轉到原始 LOG
        if hasattr(self, 'pass_tree_enhanced'):
            self.pass_tree_enhanced.tree.bind('<<TreeviewSelect>>', self._on_pass_item_select_jump, add='+')

        # 🔄 標籤切換時自動聚焦，確保鍵盤立即可以使用
        if hasattr(self, 'notebook'):
            self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)

        # 📄 原始 LOG 鍵盤增強：上下鍵改為「翻頁」模式 (User Requested: 一次翻轉一個頁面)
        if hasattr(self, 'log_text_enhanced'):
            # 將上下鍵綁定為翻頁
            self.log_text_enhanced.text.bind('<Down>', lambda e: self.log_text_enhanced.text.yview_scroll(1, "pages") or "break")
            self.log_text_enhanced.text.bind('<Up>', lambda e: self.log_text_enhanced.text.yview_scroll(-1, "pages") or "break")
            
            # 將章節跳轉移動到 Alt + PageUp/Down
            self.log_text_enhanced.text.bind('<Alt-Prior>', lambda e: self._jump_to_text_mark(self.log_text_enhanced.text, 'header_style', 'prev'))
            self.log_text_enhanced.text.bind('<Alt-Next>', lambda e: self._jump_to_text_mark(self.log_text_enhanced.text, 'header_style', 'next'))
            
        # ❌ FAIL 詳情鍵盤增強
        if hasattr(self, 'fail_error_text'):
            # 上下鍵翻頁
            self.fail_error_text.bind('<Down>', lambda e: self.fail_error_text.yview_scroll(1, "pages") or "break")
            self.fail_error_text.bind('<Up>', lambda e: self.fail_error_text.yview_scroll(-1, "pages") or "break")
            
            # 章節跳轉也移動到 Alt + PageUp/Down
            self.fail_error_text.bind('<Alt-Prior>', lambda e: self._jump_to_text_mark(self.fail_error_text, 'fail_text', 'prev'))
            self.fail_error_text.bind('<Alt-Next>', lambda e: self._jump_to_text_mark(self.fail_error_text, 'fail_text', 'next'))

    def _jump_to_text_mark(self, widget, tag, direction):
        """輔助函式：在指定的 Text Widget 中依據標籤跳轉 (支援 Content Switching)"""
        try:
            current_pos = widget.index(tk.INSERT)
            ranges = widget.tag_ranges(tag)
            if not ranges: return None
            
            # 取得所有區段的起始位置
            positions = [widget.index(ranges[i]) for i in range(0, len(ranges), 2)]
            
            target_pos = None
            if direction == 'next':
                for p in positions:
                    if widget.compare(p, '>', current_pos):
                        target_pos = p
                        break
                if not target_pos and positions: target_pos = positions[0] # 回到第一個
            else:
                for p in reversed(positions):
                    if widget.compare(p, '<', current_pos):
                        target_pos = p
                        break
                if not target_pos and positions: target_pos = positions[-1] # 回到最後一個
            
            if target_pos:
                widget.see(target_pos)
                widget.mark_set(tk.INSERT, target_pos)
                # 📢 觸發反黃高亮跟隨 (如果有該方法)
                if hasattr(self, 'log_text_enhanced'):
                    # 嘗試從物件實例中調用高亮更新
                    for attr in ['log_text_enhanced', 'fail_error_text']:
                        obj = getattr(self, attr, None)
                        if obj and hasattr(obj, 'text') and obj.text == widget:
                             obj._on_cursor_move()
                             break
        except: pass
        return "break" # 攔截預設的 1 line 移動

    # 🚀 全域快捷導航實作 (由左側面板按鈕調用)
    def _global_scroll_top(self):
        """全域置頂：根據目前標籤頁進行置頂"""
        tab_text = self._get_current_tab_text()
        if "FAIL" in tab_text: self.fail_tree_enhanced.scroll_to_top()
        elif "PASS" in tab_text: self.pass_tree_enhanced.scroll_to_top()
        elif "原始" in tab_text: self.log_text_enhanced.text.see("1.0")

    def _global_scroll_bottom(self):
        """全域置底：根據目前標籤頁進行置底"""
        tab_text = self._get_current_tab_text()
        if "FAIL" in tab_text: self.fail_tree_enhanced.scroll_to_bottom()
        elif "PASS" in tab_text: self.pass_tree_enhanced.scroll_to_bottom()
        elif "原始" in tab_text: self.log_text_enhanced.text.see(tk.END)

    def _global_scroll_pgup(self):
        """全域上一頁：標準翻頁行為 (例如：51-100 -> 0-50)"""
        tab_text = self._get_current_tab_text()
        if "FAIL" in tab_text: self.fail_tree_enhanced.page_up()
        elif "PASS" in tab_text: self.pass_tree_enhanced.page_up()
        elif "原始" in tab_text: self.log_text_enhanced.text.yview_scroll(-1, "pages")

    def _global_scroll_pgdn(self):
        """全域下一頁：標準翻頁行為 (例如：0-50 -> 51-100)"""
        tab_text = self._get_current_tab_text()
        if "FAIL" in tab_text: self.fail_tree_enhanced.page_down()
        elif "PASS" in tab_text: self.pass_tree_enhanced.page_down()
        elif "原始" in tab_text: self.log_text_enhanced.text.yview_scroll(1, "pages")

    def _get_current_tab_text(self):
        try:
            return self.notebook.tab(self.notebook.select(), "text")
        except: return ""

    def _on_tab_changed(self, event):
        """當切換分頁時，自動聚焦到該頁面的主要列表中"""
        selected_tab = self.notebook.select()
        tab_text = self.notebook.tab(selected_tab, "text")
        
        if "FAIL" in tab_text and hasattr(self, 'fail_tree_enhanced'):
            self.fail_tree_enhanced.tree.focus_set()
        elif "PASS" in tab_text and hasattr(self, 'pass_tree_enhanced'):
            self.pass_tree_enhanced.tree.focus_set()
        elif "原始" in tab_text and hasattr(self, 'log_text_enhanced'):
            self.log_text_enhanced.text.focus_set()

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
            
            # 🟢 新增：如果是比對項目 (Validation Item)，則跳轉到原始 LOG
            line_idx = self.fail_tree_enhanced.validation_line_indices.get(item_id)
            if line_idx is not None:
                if hasattr(self, 'log_text_enhanced'):
                    # 執行跳轉
                    self.log_text_enhanced._jump_to_log_line(line_idx)
            
            # 顯示原有詳細資訊
            self._display_fail_reason_for_item(item_id)

    def _on_pass_item_select_jump(self, event):
        """當 PASS 列表中的比對項目被選中時，自動跳轉到原始 LOG 對應行"""
        try:
            selection = self.pass_tree_enhanced.tree.selection()
            if not selection: return
            
            item_id = selection[0]
            # 從 validation_line_indices 中獲取儲存的 line_idx
            line_idx = self.pass_tree_enhanced.validation_line_indices.get(item_id)
            
            if line_idx is not None and hasattr(self, 'log_text_enhanced'):
                    # 切換到「原始LOG」分頁
                    if hasattr(self, 'notebook') and hasattr(self, 'tab_log'):
                        # 找到索引
                        tabs = self.notebook.tabs()
                        for i, tab in enumerate(tabs):
                            if self.notebook.tab(tab, 'text') == "📖 原始LOG":
                                self.notebook.select(i)
                                break
                    
                    # 執行跳轉
                    self.log_text_enhanced._jump_to_log_line(line_idx)
        except Exception as e:
            print(f"PASS項目跳轉失敗: {e}")

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
            
        # 4. 更新下拉選單字體 (左側面板)
        if hasattr(self, 'selection_menu'):
            self.selection_menu.configure(font=('Arial', self.ui_font_size))

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
            
            # 圖片檢索設定
            if hasattr(self, 'image_root_var'):
                self.config_manager.set('image_search_root', self.image_root_var.get())
            if hasattr(self, 'image_dir_name_var'):
                self.config_manager.set('image_search_dir_name', self.image_dir_name_var.get())
            if hasattr(self, 'image_sub_dir_var'):
                self.config_manager.set('image_search_sub_dir', self.image_sub_dir_var.get())
                 
            self.config_manager.save()
            print("設定已保存")
            
        except Exception as e:
            print(f"保存設定失敗: {e}")
            
        self._cancel_flag = True
        self._cleanup_temp_files_async()
        self.root.destroy()
    
    # === Delegate Methods for ProgressManager ===
    def _show_progress(self, title, message="", force_popup=False):
        self.root.after(0, lambda: self.progress_manager.show_progress(title, message, force_popup))
        
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
            
            # 圖片檢索設定
            if hasattr(self, 'image_root_var'):
                self.config_manager.set('image_search_root', self.image_root_var.get())
            if hasattr(self, 'image_dir_name_var'):
                self.config_manager.set('image_search_dir_name', self.image_dir_name_var.get())
            if hasattr(self, 'image_sub_dir_var'):
                self.config_manager.set('image_search_sub_dir', self.image_sub_dir_var.get())
            
            # 保存
            self.config_manager.save()
            messagebox.showinfo("成功", "設定已保存！")
            
            # 更新標題版本
            app_title = self.config_manager.get('app_title', 'PEGA test log Aanlyser')
            version = self.config_manager.get('version', 'V1.5.6')
            self.root.title(f"{app_title} {version}")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"保存設定失敗: {e}")

    def _search_images_by_isn(self):
        """依據 ISN 檢索圖片 (支援取消、強制彈窗、且不分大小寫)"""
        print("DEBUG: _search_images_by_isn triggered")
        try:
            raw_isn = self.isn_image_var.get().strip()
            print(f"DEBUG: Searching for ISN(s): {raw_isn}")
            if not raw_isn:
                messagebox.showwarning("提示", "請輸入 ISN 進行檢索")
                return
            
            # 🟢 支援多個 ISN (以逗號或空格分隔)
            import re
            isn_list = [i.strip() for i in re.split(r'[,\s]+', raw_isn) if i.strip()]
            
            root_dir = self.config_manager.get('image_search_root', 'D:\\')
            target_dir_keyword = self.config_manager.get('image_search_dir_name', 'STATION_RECORD').lower()
            sub_dir_keyword = self.config_manager.get('image_search_sub_dir', '').lower()
            extensions = tuple(ext.strip().lower() for ext in self.config_manager.get('image_search_extensions', 'jpg,png,yuv,bmp').split(','))
            
            if not os.path.exists(root_dir):
                messagebox.showerror("錯誤", f"搜尋根路徑不存在: {root_dir}")
                return
                
            self._cancel_flag = False
            results = []
            
            # UI 字體自適應
            from .ui_components import FontScaler
            ui_font_size = self.config_manager.get('ui_font_size', 12)
            
            self._show_progress("正在搜尋圖片", f"階段 1: 預備掃描磁碟目標...\n搜尋起點: {root_dir}\n目標關鍵字: {target_dir_keyword}", force_popup=True)
        
            def _search_thread():
                try:
                    target_folders = []
                    # 🟢 標準化起點路徑，移除末端反斜線以便正確認別 basename
                    search_base = os.path.normpath(root_dir)
                    
                    # 1. 找出符合 STATION_RECORD 的資料夾
                    # 如果使用者關鍵字留空，或是起點路徑本身就包含關鍵字，則直接將起點列為目標
                    if not target_dir_keyword or target_dir_keyword in os.path.basename(search_base).lower():
                        target_folders.append(search_base)
                        print(f"DEBUG: Root directory is already a target: {search_base}")
                    else:
                        for root, dirs, files in os.walk(root_dir):
                            if self._cancel_flag or self.progress_manager.is_cancelled:
                                self._cancel_flag = True
                                break
                            
                            self._safe_update_progress_text(f"搜尋起點: {root_dir}\n掃描路徑: {os.path.basename(root)}\n已找到 {len(target_folders)} 個目標...")
                            
                            current_basename = os.path.basename(os.path.normpath(root)).lower()
                            if target_dir_keyword in current_basename:
                                target_folders.append(root)
                                # 找到目標資料夾後，不再深挖其子目錄尋找同名資料夾 (剪枝)
                                dirs[:] = []
                    
                    if self._cancel_flag:
                        self.root.after(0, self._close_progress)
                        return

                    # 2. 檢索圖片 (智慧型剪枝)
                    total_folders = len(target_folders)
                    for idx, folder in enumerate(target_folders, 1):
                        if self._cancel_flag or self.progress_manager.is_cancelled:
                            self._cancel_flag = True
                            break
                            
                        self._safe_update_progress_text(f"階段 2: 智慧檢索 ({idx}/{total_folders})\n目標: {folder}\nISN: {', '.join(isn_list[:2])}...")
                        
                        try:
                            for root, dirs, files in os.walk(folder):
                                if self._cancel_flag: break
                                rel_path = os.path.relpath(root, folder)
                                
                                if rel_path == ".":
                                    # 只鑽進符合任一 ISN 的子目錄
                                    dirs[:] = [d for d in dirs if any(i.lower() in d.lower() for i in isn_list)]
                                    for f in files:
                                        if any(i.lower() in f.lower() for i in isn_list) and any(f.lower().endswith(ext) for ext in extensions):
                                            results.append(os.path.join(root, f))
                                else:
                                    # 已經在 ISN 目錄下，處理 4cam 或直接收圖
                                    if sub_dir_keyword and rel_path.count(os.sep) == 0:
                                        sub_matches = [d for d in dirs if sub_dir_keyword in d.lower()]
                                        if sub_matches: dirs[:] = sub_matches
                                            
                                    for f in files:
                                        if any(f.lower().endswith(ext) for ext in extensions):
                                            results.append(os.path.join(root, f))
                        except Exception as e:
                            print(f"DEBUG: 智慧掃描失敗 {folder}: {e}")
                    
                    def _done():
                        self._close_progress()
                        if self._cancel_flag:
                            messagebox.showinfo("提示", "搜尋作業已主動終止")
                            return
                            
                        isn_str = ", ".join(isn_list)
                        if not results:
                            # 🟡 精細的未命中原因分析
                            msg = f"搜尋完成，但找不到任何符合的圖片。\n\n"
                            msg += f"🔍 搜尋條件確認：\n"
                            msg += f"• ISN 關鍵字: {isn_str}\n"
                            msg += f"• 搜尋起點: {root_dir}\n"
                            msg += f"• 目標資料夾: {target_dir_keyword}\n"
                            msg += f"• 次級過濾器 (4cam?): {sub_dir_keyword if sub_dir_keyword else '未設定'}\n\n"
                            
                            msg += "💡 常見原因：\n"
                            if sub_dir_keyword:
                                msg += f"1. [重點] 您啟用了次級過濾 '{sub_dir_keyword}'，但相關圖檔可能不在這個目錄下。\n"
                            msg += "2. ISN 輸入錯誤，或是在 STATION_RECORD 之下找不到對應目錄。\n\n"
                            msg += "是否要「擴大範圍」手動選擇一個資料夾進行全盤搜尋？"
                            
                            if messagebox.askyesno("未找到結果", msg):
                                from tkinter import filedialog
                                manual_dir = filedialog.askdirectory(title="選擇搜尋起點", initialdir=root_dir)
                                if manual_dir:
                                    self._run_image_search_logic_new(isn_str, manual_dir, target_dir_keyword, sub_dir_keyword, extensions)
                        else:
                            # 🟢 找到結果，告知數量後開啟視窗
                            messagebox.showinfo("搜尋成功", f"找到 {len(results)} 個項目！即將開啟結果視窗。")
                            from .dialogs import show_image_results
                            show_image_results(self, results, isn_str)
                    
                    self.root.after(0, _done)
                except Exception as e:
                    self.root.after(0, lambda: [self._close_progress(), messagebox.showerror("錯誤", f"搜尋失敗: {e}")])
                    
            threading.Thread(target=_search_thread, daemon=True).start()
        except Exception as e:
            messagebox.showerror("啟動錯誤", f"無法啟動搜尋程序: {e}")

    def _run_image_search_logic_new(self, isn, root_dir, target_dir_keyword, sub_dir_keyword, extensions):
        """擴大搜尋 - 強制彈窗"""
        self._cancel_flag = False
        self._show_progress("手動擴大搜尋中", f"範圍: {root_dir}\n(搜圖過程中可隨時取消)", force_popup=True)
        results = []
        
        def _thread():
            try:
                for root, dirs, files in os.walk(root_dir):
                    if self._cancel_flag or self.progress_manager.is_cancelled:
                        self._cancel_flag = True
                        break
                        
                    self._safe_update_progress_text(f"擴大搜尋中: {os.path.basename(root)}\n已找到: {len(results)}")
                    
                    # 如果當前路徑還沒包含 ISN，嘗試篩選子資料夾以加速
                    if isn.lower() not in root.lower():
                        matches = [d for d in dirs if isn.lower() in d.lower()]
                        if matches:
                            dirs[:] = matches # 優先鑽進含 ISN 的目錄
                    
                    for f in files:
                        if any(f.lower().endswith(ext) for ext in extensions):
                            full_path = os.path.join(root, f)
                            if isn.lower() in full_path.lower():
                                if not sub_dir_keyword or sub_dir_keyword in full_path.lower():
                                    results.append(full_path)
                                    
                def _done():
                    self._close_progress()
                    if self._cancel_flag:
                        messagebox.showinfo("提示", "擴大搜尋已終止")
                        return
                    if not results:
                        messagebox.showinfo("檢索結果", f"手動針對 '{root_dir}' 搜尋結果為 0。")
                    else:
                        from .dialogs import show_image_results
                        show_image_results(self, results, isn)
                self.root.after(0, _done)
            except Exception as e:
                self.root.after(0, lambda: [self._close_progress(), messagebox.showerror("錯誤", f"擴搜崩潰: {e}")])
        
        threading.Thread(target=_thread, daemon=True).start()
