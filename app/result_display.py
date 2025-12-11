# -*- coding: utf-8 -*-
"""
Result Display Module
Handles displaying analysis results in the UI (Mixin)
"""

import os
import tkinter as tk
from tkinter import messagebox

class ResultDisplayMixin:
    """Mixin for handling result display operations in the Log Analyzer"""
    
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
                from .settings_loader import save_settings
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
                # 從存儲中獲取完整內容
                full_content = self.fail_tree_enhanced.full_content_storage.get(item_id, '')
                
                # 提取主要的FAIL原因作為大字體標題
                main_error = self._extract_main_fail_reason(full_content)
                
                # 顯示大字體紅色文字白底
                if hasattr(self, 'fail_error_title'):
                    self.fail_error_title.config(text=main_error, 
                                                font=('Arial', 20, 'bold'), fg='red', bg='white')
                
                # 提取FAIL原因部分顯示在下方
                fail_reason_content = self._extract_fail_reason(full_content)
                
                # 更新錯誤內容
                if hasattr(self, 'fail_error_text'):
                    self.fail_error_text.config(state=tk.NORMAL)
                    self.fail_error_text.delete('1.0', tk.END)
                    self._insert_formatted_fail_content(fail_reason_content)
                    self.fail_error_text.config(state=tk.NORMAL)
            else:
                if hasattr(self, 'fail_error_title'):
                    self.fail_error_title.config(text="無詳細錯誤資訊")
                if hasattr(self, 'fail_error_text'):
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
                    # 從存儲中獲取完整內容，優先找到包含 "is Fail" 的行作為標題
                    full_content = self.fail_tree_enhanced.full_content_storage.get(item_id, '')
                    
                    # 優先從完整內容中找到包含 "is Fail" 的行作為大字體標題
                    main_error = self._extract_main_fail_reason(full_content)
                    
                    # 顯示大字體紅色文字白底
                    if hasattr(self, 'fail_error_title'):
                        self.fail_error_title.config(text=main_error, 
                                                    font=('Arial', 20, 'bold'), fg='red', bg='white')
                    
                    # 提取FAIL原因部分顯示在下方
                    fail_reason_content = self._extract_fail_reason(full_content)
                    
                    # 更新錯誤內容
                    if hasattr(self, 'fail_error_text'):
                        self.fail_error_text.config(state=tk.NORMAL)
                        self.fail_error_text.delete('1.0', tk.END)
                        self._insert_formatted_fail_content(fail_reason_content)
                        self.fail_error_text.config(state=tk.NORMAL)
                else:
                    if hasattr(self, 'fail_error_title'):
                        self.fail_error_title.config(text="無詳細錯誤資訊")
                    if hasattr(self, 'fail_error_text'):
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
        if hasattr(self, 'fail_error_text'):
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
            
    def _clear_enhanced_results(self):
        """清除增強版分析結果（供左側按鈕呼叫）"""
        try:
            # 清理壓縮檔解壓縮的暫存檔案
            if hasattr(self, '_cleanup_temp_files'):
                self._cleanup_temp_files()
            
            # 清除當前選擇的路徑
            self.current_log_path = ''
            self.current_mode = 'single'
            
            # 清除 UI 顯示
            if hasattr(self, 'file_info_label'):
                self.file_info_label.config(text="尚未選擇檔案", fg='gray')
            
            # 清除分頁內容
            if hasattr(self, 'pass_tree_enhanced'):
                self.pass_tree_enhanced.clear()
            
            if hasattr(self, 'fail_tree_enhanced'):
                self.fail_tree_enhanced.clear()
                
            if hasattr(self, 'log_text_enhanced'):
                self.log_text_enhanced.clear()
            
            if hasattr(self, 'pass_summary_tree'):
                self.pass_summary_tree.delete(*self.pass_summary_tree.get_children())
            if hasattr(self, 'fail_summary_tree'):
                self.fail_summary_tree.delete(*self.fail_summary_tree.get_children())
            
            if hasattr(self, 'pass_tree'):
                for item in self.pass_tree.get_children():
                    self.pass_tree.delete(item)
            
            if hasattr(self, 'fail_tree'):
                for item in self.fail_tree.get_children():
                    self.fail_tree.delete(item)
            
            if hasattr(self, 'raw_text'):
                self.raw_text.delete(1.0, tk.END)
                
            # 清除FAIL錯誤顯示區域
            if hasattr(self, 'fail_error_title'):
                self.fail_error_title.config(text="選擇FAIL項目查看詳細錯誤")
            if hasattr(self, 'fail_error_text'):
                self.fail_error_text.config(state=tk.NORMAL)
                self.fail_error_text.delete('1.0', tk.END)
                self.fail_error_text.config(state=tk.NORMAL)
            
            print("已清除所有結果")
        except Exception as e:
            print(f"清除結果時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
