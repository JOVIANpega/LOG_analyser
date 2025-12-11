# -*- coding: utf-8 -*-
"""
Analysis Engine Module
Handles core analysis logic orchestration (Mixin)
"""

import os
import tkinter as tk
from tkinter import messagebox
import traceback
import threading

class AnalysisEngineMixin:
    """Mixin for handling analysis orchestration in the Log Analyzer"""
    
    def _analyze_enhanced_log(self):
        """分析log檔案並更新增強版GUI顯示"""
        if not self.current_log_path:
            messagebox.showwarning("警告", "請先選擇log檔案或資料夾")
            return
            
        # 清空現有內容
        if hasattr(self, 'pass_tree_enhanced'):
            self.pass_tree_enhanced.clear()
        if hasattr(self, 'fail_tree_enhanced'):
            self.fail_tree_enhanced.clear()
        if hasattr(self, 'log_text_enhanced'):
            self.log_text_enhanced.clear()

        # 顯示分析進度
        filename = os.path.basename(self.current_log_path)
        self._show_progress("正在分析LOG檔案", f"分析檔案: {filename}")
        
        try:
            if self.current_mode == 'single':
                self._analyze_enhanced_single_file()
            else:
                self._analyze_enhanced_multiple_files()
            
            # 分析完成後關閉進度條
            self.root.after(100, self._close_progress)
                
        except Exception as e:
            self._close_progress()
            messagebox.showerror("分析錯誤", f"分析過程中發生錯誤：\n{str(e)}")
            traceback.print_exc()
    
    def _analyze_enhanced_single_file(self):
        """分析單一檔案（增強版）"""
        # 更新進度：開始解析
        self._update_progress("正在解析LOG檔案內容...")
        
        result = self.log_parser.parse_log_file(self.current_log_path)
        pass_items = result['pass_items']
        fail_items = result['fail_items']
        raw_lines = result['raw_lines']
        last_fail = result['last_fail']
        fail_line_idx = result['fail_line_idx']
        
        # 提取 Header 資訊
        header_info = self._extract_log_header_info(raw_lines)
        
        # 匯出 Markdown 報告 (包含 Header 資訊) - 用戶不需要
        # self._export_markdown_report(header_info, pass_items, fail_items, last_fail)
        
        # 更新進度：處理PASS項目
        self._update_progress(f"處理PASS項目 ({len(pass_items)} 個)...")
        
        # Tab1: PASS - 顯示所有通過的測項
        if hasattr(self, 'pass_tree_enhanced'):
            for idx, item in enumerate(pass_items, 1):
                full_response = item.get('full_response', '')
                has_retry = item.get('has_retry_but_pass', False)  # 使用 has_retry_but_pass 屬性
                self.pass_tree_enhanced.insert_pass_item(
                    (item['step_name'], item['command'], item['response'], item['result']),
                    step_number=idx,
                    full_response=full_response,
                    has_retry=has_retry
                )
        
        # 更新進度：處理FAIL項目
        self._update_progress(f"處理FAIL項目 ({len(fail_items)} 個)...")
        
        # Tab2: FAIL - 顯示所有FAIL區塊
        if hasattr(self, 'fail_tree_enhanced'):
            for idx, item in enumerate(fail_items):
                is_main_fail = item.get('is_main_fail', False)
                full_response = item.get('full_response', '')
                self.fail_tree_enhanced.insert_fail_item(
                    (item['step_name'], item['command'], item['response'], item['retry'], item['error']),
                    full_response=full_response,
                    is_main_fail=is_main_fail
                )
        
        # 更新進度：處理原始LOG
        self._update_progress("處理原始LOG內容...")
        
        # Tab3: 原始LOG，標紅錯誤行並自動跳轉
        if raw_lines and hasattr(self, 'log_text_enhanced'):
            # 將raw_lines轉換為字符串
            log_content = '\n'.join(raw_lines)
            
            # 使用新的支援 Header 的方法
            self.log_text_enhanced.insert_log_with_highlighting(log_content, {
                'fail_line_idx': fail_line_idx,
                'pass_items': pass_items,
                'fail_items': fail_items
            }, header_content=header_info)
            
            # 如果有錯誤行，跳轉到錯誤位置
            if fail_line_idx is not None and fail_line_idx < len(raw_lines):
                self.log_text_enhanced.highlight_error_block(fail_line_idx + 1, fail_line_idx + 1)
                # self.log_text_enhanced.text.see(f"{fail_line_idx + 1}.0") # highlight_error_block 已處理
        
        # 更新進度：完成分析
        self._update_progress("分析完成！")
        
        # 根據分析結果動態顯示/隱藏標籤頁
        if hasattr(self, '_update_tab_visibility'):
            self._update_tab_visibility(pass_items, fail_items)

        # 自動切換到相關Tab
        if fail_items:
            try:
                if hasattr(self, 'notebook') and hasattr(self, 'tab_fail'):
                    self.notebook.select(self.tab_fail)
                
                # 延遲切換到原始LOG標籤頁並聚焦錯誤位置
                if hasattr(self, '_switch_to_log_and_focus_error'):
                    self.root.after(2000, self._switch_to_log_and_focus_error)
                
                # 如果是FAIL Log，彈出顯示主要錯誤原因 (Priority Error)
                if last_fail:
                    error_msg = last_fail.get('error', 'Unknown Error')
                    cmd = last_fail.get('command', 'Unknown Command')
                    step = last_fail.get('step_name', 'Unknown Step')
                    
                    # 判斷是否為 "doesn't match" 的重點錯誤
                    is_match_error = "doesn't match" in str(error_msg).lower() or "doesn't match" in str(last_fail.get('full_log', '')).lower()
                    
                    priority_text = "主要錯誤 (RETEST Logic)" if is_match_error else "主要錯誤"
                    
                    details = f"Step: {step}\nCommand: {cmd}\nError: {error_msg}"
                    messagebox.showinfo(priority_text, details)
                    
            except Exception as e:
                print(f"切換到FAIL分頁或顯示錯誤失敗: {e}")
                traceback.print_exc()
        else:
            try:
                if hasattr(self, 'notebook') and hasattr(self, 'tab_pass'):
                    self.notebook.select(self.tab_pass)
            except Exception:
                pass

    def _extract_log_header_info(self, raw_lines):
        """從 Log 內容提取置頂資訊"""
        try:
            import re
            content = "\n".join(raw_lines[:500]) # 只搜尋前500行
            
            info_lines = []
            
            # 定義正則表達式
            patterns = [
                (r'(ISN=[^\n]+)', 'ISN'),
                (r'(Script File is [^\n]+)', 'Script File'),
                (r'(SFIS is [^\n]+)', 'SFIS'),
                (r'(All phase Total Test Time.+?[\d\.]+\s*Sec)', 'Test Time'), # 保留原本
                (r'All phase Total Test Time[\s!:\-]+([\d\.]+)\s*Sec', 'Test Time Regex 2') # 修正後的增強版 Regex
            ]
            
            # 用檔案名作為備選
            filename = os.path.basename(self.current_log_path)
            # info_lines.append(f"File: {filename}")
            
            for pattern, label in patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    if label == 'Test Time Regex 2':
                        # 如果是 Regex 2，match.group(1) 是秒數，我們手動組裝
                        info_lines.append(f"All phase Total Test Time ! ----- {match.group(1)} Sec.")
                    else:
                        info_lines.append(match.group(1).strip())
            
            # 如果沒有找到 ISN，嘗試從檔名提取
            # ...
            
            return "\n".join(info_lines) if info_lines else "無法提取 Header 資訊"
            
        except Exception as e:
            print(f"提取 Header 資訊失敗: {e}")
            return ""

    def _export_markdown_report(self, header_info, pass_items, fail_items, last_fail):
        """匯出 Markdown 報告到 markdown_File 資料夾"""
        try:
            # 建立目錄
            md_dir = os.path.join(os.path.dirname(self.current_log_path), "markdown_File")
            if not os.path.exists(md_dir):
                # 如果是相對路徑或沒有權限，嘗試在當前工作目錄建立
                try:
                    os.makedirs(md_dir, exist_ok=True)
                except:
                    md_dir = os.path.join(os.getcwd(), "markdown_File")
                    os.makedirs(md_dir, exist_ok=True)
            
            # 決定檔名
            base_name = os.path.basename(self.current_log_path)
            name_no_ext = os.path.splitext(base_name)[0]
            md_path = os.path.join(md_dir, f"{name_no_ext}_Report.md")
            
            # 撰寫內容
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(f"# Analysis Report: {base_name}\n\n")
                
                # Header Info
                f.write("## 1. Top Info\n")
                f.write("```text\n")
                f.write(header_info if header_info else "No header info extracted.")
                f.write("\n```\n\n")
                
                # Summary
                f.write("## 2. Summary\n")
                f.write(f"- **Total Pass**: {len(pass_items)}\n")
                f.write(f"- **Total Fail**: {len(fail_items)}\n")
                if last_fail:
                    f.write(f"- **Last Fail Step**: {last_fail.get('step_name')}\n")
                    f.write(f"- **Error**: {last_fail.get('error')}\n")
                else:
                    f.write("- **Status**: PASS\n")
                f.write("\n")
                
                # Fail Details
                if fail_items:
                    f.write("## 3. Fail Details\n")
                    for i, item in enumerate(fail_items, 1):
                        f.write(f"### Fail #{i}: {item.get('step_name')}\n")
                        f.write(f"- **Command**: `{item.get('command')}`\n")
                        f.write(f"- **Error**: {item.get('error')}\n")
                        f.write("- **Full Log Snippet**:\n")
                        f.write("```text\n")
                        f.write(item.get('full_response', '')[:1000]) # 限制長度
                        f.write("\n```\n\n")
            
            print(f"Markdown report generated: {md_path}")
            
        except Exception as e:
            print(f"匯出 Markdown 報告失敗: {e}")

    def _analyze_enhanced_multiple_files(self):
        """分析多個檔案或是資料夾（資料夾模式/壓縮檔模式）"""
        # 啟動背景執行緒進行分析，避免卡住主介面
        threading.Thread(target=self._analyze_enhanced_multiple_files_thread, daemon=True).start()

    def _analyze_enhanced_multiple_files_thread(self):
        """背景執行的多檔分析邏輯"""
        try:
            target_files = []
            
            # 1. 確定檔案清單
            if os.path.isdir(self.current_log_path):
                 for root, dirs, files in os.walk(self.current_log_path):
                    for f in files:
                        if self._cancel_flag: break
                        if f.lower().endswith('.log'):
                            target_files.append(os.path.join(root, f))
            elif isinstance(self.current_log_path, (list, tuple)):
                target_files = [f for f in self.current_log_path if f.lower().endswith('.log')]
            elif os.path.isfile(self.current_log_path):
                 target_files = [self.current_log_path]
                 
            if not target_files:
                self.root.after(0, lambda: messagebox.showwarning("警告", "找不到 .log 檔案"))
                return
    
            total_files = len(target_files)
            
            # 2. 初始化進度條 (Thread-safe)
            self._safe_update_progress_mode('determinate')
            self._safe_update_progress_max(total_files)
            
            pass_logs = []
            fail_logs = []
            
            # 3. 逐一分析
            for i, file_path in enumerate(target_files):
                if self._cancel_flag:
                    break
                    
                fname = os.path.basename(file_path)
                # 更新進度 (Thread-safe)
                self._safe_update_progress(i+1, total_files, f"正在分析 ({i+1}/{total_files}): {fname}")
                
                try:
                    # 解析 (CPU bound, safe in thread)
                    result = self.log_parser.parse_log_file(file_path)
                    
                    # 整理資料結構
                    # 提取 Header 資訊
                    header_info = self._extract_log_header_info(result['raw_lines'])
                    
                    log_entry = {
                        'file_path': file_path,
                        'file_name': fname,
                        'raw_lines': result['raw_lines'],
                        'ui_annotations': result.get('ui_annotations', []),
                        'pass_items': result['pass_items'],
                        'fail_items': result['fail_items'],
                        'last_fail': result.get('last_fail'),
                        'step_marks': None,
                        'header_info': header_info, # 加入 Header 資訊
                        'summary': {
                            'SFIS': 'Unknown', 
                            'FAIL原因': result.get('last_fail', {}).get('error', '') if result.get('last_fail') else ''
                        }
                    }
                    
                    # 分類
                    if result['log_type'] == 'PASS':
                         pass_logs.append(log_entry)
                    elif result['log_type'] == 'FAIL':
                         fail_logs.append(log_entry)
                    else:
                        if result['fail_items']:
                            fail_logs.append(log_entry)
                        else:
                            pass_logs.append(log_entry)
                         
                except Exception as e:
                    print(f"分析檔案失敗 {file_path}: {e}")
                    traceback.print_exc()
                    continue
    
            # 4. 匯出 Excel
            if not self._cancel_flag:
                self._safe_update_progress_text("正在產生 Excel 報告...")
                try:
                    # 決定輸出目錄
                    if os.path.isdir(self.current_log_path):
                        out_dir = self.current_log_path
                    else:
                        out_dir = os.path.dirname(target_files[0])
                        
                    pass_path, fail_path = self.excel_writer.export_pass_fail_workbooks(
                        out_dir, pass_logs, fail_logs
                    )
                    
                    # 5. 顯示完成視窗 (必須回到主執行緒)
                    self.root.after(0, lambda: self._show_open_folder_prompt(
                        out_dir, total_files, len(pass_logs), len(fail_logs), pass_path, fail_path
                    ))
                    
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("匯出錯誤", f"產生 Excel 報告時發生錯誤: {e}"))
                    traceback.print_exc()
                    
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("錯誤", f"多檔分析過程發生錯誤: {e}"))
            traceback.print_exc()
        finally:
            # 確保結束時關閉進度條
            self.root.after(0, self._close_progress)
