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
import time
import re

class AnalysisEngineMixin:
    """Mixin for handling analysis orchestration in the Log Analyzer"""
    
    def _analyze_enhanced_log(self):
        """分析log檔案並更新增強版GUI顯示"""
        print(f"[DEBUG] _analyze_enhanced_log 被調用")
        print(f"[DEBUG] - current_mode: {self.current_mode}")
        print(f"[DEBUG] - current_log_path 類型: {type(self.current_log_path)}")
        
        if not self.current_log_path:
            print(f"[ERROR] current_log_path 為空！")
            messagebox.showwarning("警告", "請先選擇log檔案或資料夾")
            return
        
        # 如果是列表，顯示檔案數量
        if isinstance(self.current_log_path, (list, tuple)):
            print(f"[DEBUG] - current_log_path 包含 {len(self.current_log_path)} 個檔案")
        else:
            print(f"[DEBUG] - current_log_path: {self.current_log_path}")
            
        # 清空現有內容
        if hasattr(self, 'pass_tree_enhanced'):
            self.pass_tree_enhanced.clear()
        if hasattr(self, 'fail_tree_enhanced'):
            self.fail_tree_enhanced.clear()
        if hasattr(self, 'log_text_enhanced'):
            self.log_text_enhanced.clear()

        # 顯示分析進度
        if isinstance(self.current_log_path, (list, tuple)):
            filename = f"{len(self.current_log_path)} 個檔案"
        else:
            filename = os.path.basename(self.current_log_path)
        
        print(f"[DEBUG] - 顯示進度: {filename}")
        self._show_progress("正在分析LOG檔案", f"分析檔案: {filename}")
        
        try:
            if self.current_mode == 'single':
                print(f"[DEBUG] - 調用 _analyze_enhanced_single_file()")
                self._analyze_enhanced_single_file()
            else:
                print(f"[DEBUG] - 調用 _analyze_enhanced_multiple_files()")
                self._analyze_enhanced_multiple_files()
            

                
        except Exception as e:
            print(f"[ERROR] 分析過程中發生錯誤: {e}")
            import traceback
            traceback.print_exc()
            self._close_progress()
            messagebox.showerror("分析錯誤", f"分析過程中發生錯誤：\n{str(e)}")
    
    def _analyze_enhanced_single_file(self):
        """分析單一檔案（增強版）- 啟動背景執行緒"""
        # 更新進度：開始解析
        self._update_progress("正在啟動背景解析...")
        threading.Thread(target=self._single_file_worker, daemon=True).start()

    def _ui_log(self, message, clear=False, tag=None):
        """在 UI 的原始 LOG 視窗顯示訊息 (Thread-safe)"""
        # ANSI 顏色代碼映射 (簡單處理常用的幾核色)
        ANSI_CLEAN = re.compile(r'\033\[[0-9;]*m')
        
        def _append():
            if hasattr(self, 'log_text_enhanced'):
                if clear:
                    self.log_text_enhanced.clear()
                
                # 若沒提供 tag 但訊息中有 ANSI 色碼，嘗試自動對應
                final_tag = tag
                if not final_tag:
                    if "\033[92m" in str(message): final_tag = 'summary_success'
                    elif "\033[93m" in str(message): final_tag = 'summary_path'
                    elif "\033[94m" in str(message) or "\033[96m" in str(message): final_tag = 'summary_info'
                
                # 對於 Text Widget，需要過濾掉 ANSI 代碼
                clean_msg = ANSI_CLEAN.sub('', str(message))
                self.log_text_enhanced.append(clean_msg, tag=final_tag)
                try:
                    self.log_text_enhanced.text.see(tk.END)
                except:
                    pass
        
        if hasattr(self, 'root'):
            self.root.after(0, _append)
        
        # 終端機輸出 (保留顏色)
        print(f"[UI_LOG] {message}")

    def _single_file_worker(self):
        """背景執行緒：執行解析邏輯"""
        try:
            self._ui_log(f"=== 開始單檔分析: {os.path.basename(self.current_log_path)} ===", clear=True)
            self._safe_update_progress_text("正在解析LOG檔案內容...")
            
            # CPU密集應操作
            result = self.log_parser.parse_log_file(self.current_log_path)
            
            # 即時顯示測試時間日誌
            try:
                if hasattr(self, 'excel_writer'):
                    secs, time_logs = self.excel_writer._extract_total_secs(result['raw_lines'])
                    for tlog in time_logs:
                        self._ui_log(tlog)
            except:
                pass
                
            # 提取 Header 資訊
            header_info = self._extract_log_header_info(result['raw_lines'])
            
            # 準備數據傳回主執行緒更新UI
            data = {
                'result': result,
                'header_info': header_info
            }
            
            # 調度 UI 更新
            self.root.after(0, lambda: self._single_file_ui_update(data))
            
        except Exception as e:
            self._ui_log(f"[錯誤] 分析失敗: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("分析錯誤", f"解析過程中發生錯誤：\n{str(e)}"))
            self.root.after(0, self._close_progress)
            traceback.print_exc()

    def _single_file_ui_update(self, data):
        """主執行緒：啟動 UI 更新流程 (分步執行以保持介面響應)"""
        # 啟動分步更新生成器
        step_generator = self._single_file_ui_steps(data)
        self._run_ui_update_step(step_generator)

    def _run_ui_update_step(self, generator):
        """執行下一個 UI 更新步驟"""
        try:
            # 執行下一步
            next(generator)
            # 排程下一步 (保留 50ms 給事件迴圈處理閃爍動畫)
            self.root.after(50, lambda: self._run_ui_update_step(generator))
        except StopIteration:
            # 全部完成
            self._close_progress()
        except Exception as e:
            messagebox.showerror("UI更新錯誤", f"更新顯示時發生錯誤：\n{str(e)}")
            traceback.print_exc()
            self._close_progress()

    def _single_file_ui_steps(self, data):
        """UI 更新步驟生成器"""
        result = data['result']
        header_info = data['header_info']
        
        pass_items = result['pass_items']
        fail_items = result['fail_items']
        raw_lines = result['raw_lines']
        last_fail = result['last_fail']
        fail_line_idx = result['fail_line_idx']
        
        # Step 1: Update Progress Text
        self._update_progress(f"準備顯示結果...")
        yield

        # Step 2: PASS Items
        self._update_progress(f"更新 PASS 列表 ({len(pass_items)} 筆)...")
        if hasattr(self, 'pass_tree_enhanced'):
            # Clear existing items if needed? Assuming tree is cleared before analysis or we append.
            # Usually we clear old results before analysis start. But let's assume cleanliness is handled elsewhere.
            # Batch insertion: Insert 100 items at a time
            batch_size = 100
            for i in range(0, len(pass_items), batch_size):
                batch = pass_items[i:i+batch_size]
                for idx, item in enumerate(batch, 1 + i):
                    full_response = item.get('full_response', '')
                    has_retry = item.get('has_retry_but_pass', False)
                    self.pass_tree_enhanced.insert_pass_item(
                        (item['step_name'], item['command'], item['response'], item['result']),
                        step_number=idx,
                        full_response=full_response,
                        has_retry=has_retry
                    )
                if len(pass_items) > 500: # Only yield inside loop if many items
                     yield 
        yield

        # Step 3: FAIL Items
        self._update_progress(f"更新 FAIL 列表 ({len(fail_items)} 筆)...")
        if hasattr(self, 'fail_tree_enhanced'):
            for idx, item in enumerate(fail_items):
                is_main_fail = item.get('is_main_fail', False)
                full_response = item.get('full_response', '')
                self.fail_tree_enhanced.insert_fail_item(
                    (item['step_name'], item['command'], item['response'], item['retry'], item['error']),
                    full_response=full_response,
                    is_main_fail=is_main_fail
                )
        yield

        # Step 4: Raw Logs
        self._update_progress("更新原始 LOG 視圖...")
        if raw_lines and hasattr(self, 'log_text_enhanced'):
            log_content = '\n'.join(raw_lines)
            
            # This is heavy. Assume insert_log_with_highlighting handles it or it blocks for a bit.
            # We can't easily chunk text widget insertion without changing EnhancedText.
            # But the yield before this gives a breath.
            self.log_text_enhanced.insert_log_with_highlighting(log_content, {
                'fail_line_idx': fail_line_idx,
                'pass_items': pass_items,
                'fail_items': fail_items
            }, header_content=header_info)
            
            if fail_line_idx is not None and fail_line_idx < len(raw_lines):
                self.log_text_enhanced.highlight_error_block(fail_line_idx + 1, fail_line_idx + 1)
        yield

        # Step 5: Finalize
        self._update_progress("完成！")
        
        # 根據分析結果動態顯示/隱藏標籤頁
        self._update_tabs_visibility(len(pass_items), len(fail_items), is_multiple=False)

        # 自動切換到相關Tab
        if fail_items:
            try:
                if hasattr(self, 'notebook') and hasattr(self, 'tab_fail'):
                    self.notebook.select(self.tab_fail)
                
                # 延遲切換到原始LOG標籤頁並聚焦錯誤位置
                if hasattr(self, '_switch_to_log_and_focus_error'):
                    self.root.after(500, self._switch_to_log_and_focus_error)
                
                # 如果是FAIL Log，彈出顯示主要錯誤原因 (Priority Error)
                if last_fail:
                    error_msg = last_fail.get('error', 'Unknown Error')
                    cmd = last_fail.get('command', 'Unknown Command')
                    step = last_fail.get('step_name', 'Unknown Step')
                    
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
            
            # 用檔案名作為備選（但在多檔模式下不使用）
            # filename = os.path.basename(self.current_log_path)
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
            # 檢查 current_log_path 是否為列表（多檔模式不支援 Markdown 匯出）
            if isinstance(self.current_log_path, (list, tuple)):
                print(f"[INFO] 多檔模式不支援 Markdown 報告匯出")
                return
            
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
        """分析多個檔案（增強版）- 啟動背景執行緒"""
        # 清除並切換到原始LOG標籤，用來顯示處理日誌
        self._ui_log("\033[96m=== 開始多檔分析流程 ===\033[0m", clear=True)
        
        # 顯示路徑並反白 (凸顯位置)
        # 優先使用原路徑 (避免顯示 Temp 路徑)
        display_path = getattr(self, 'original_log_path', self.current_log_path)
        path_str = str(display_path)
        self._ui_log(f"\033[93m路徑: {path_str}\033[0m", tag='summary_path')
        
        if hasattr(self, 'notebook'):
            try:
                # 假設「原始LOG」是第三個標籤 (索引 2)
                self.notebook.select(2)
            except:
                pass
                
        self._update_progress("正在啟動背景多檔解析...")
        threading.Thread(target=self._analyze_enhanced_multiple_files_thread, daemon=True).start()

    def _analyze_enhanced_multiple_files_thread(self):
        """背景執行的多檔分析邏輯"""
        try:
            target_files = []
            
            print(f"[DEBUG] _analyze_enhanced_multiple_files_thread 開始")
            print(f"[DEBUG] - current_log_path 類型: {type(self.current_log_path)}")
            
            # 1. 確定檔案清單（先檢查類型，避免將列表傳給 os.path 函數）
            if isinstance(self.current_log_path, (list, tuple)):
                # 多個檔案（列表）
                print(f"[DEBUG] - 處理檔案列表，共 {len(self.current_log_path)} 個")
                target_files = [f for f in self.current_log_path if f.lower().endswith('.log')]
            elif isinstance(self.current_log_path, str):
                # 單一路徑（字串）
                if os.path.isdir(self.current_log_path):
                    # 資料夾：遞迴搜尋
                    print(f"[DEBUG] - 掃描資料夾: {self.current_log_path}")
                    for root, dirs, files in os.walk(self.current_log_path):
                        for f in files:
                            if self._cancel_flag: break
                            if f.lower().endswith('.log'):
                                target_files.append(os.path.join(root, f))
                elif os.path.isfile(self.current_log_path):
                    # 單一檔案
                    print(f"[DEBUG] - 處理單一檔案: {self.current_log_path}")
                    target_files = [self.current_log_path]
                else:
                    print(f"[ERROR] 路徑不存在: {self.current_log_path}")
            else:
                print(f"[ERROR] current_log_path 類型不正確: {type(self.current_log_path)}")
                  
            if not target_files:
                print(f"[ERROR] 找不到 .log 檔案")
                self.root.after(0, lambda: messagebox.showwarning("警告", "找不到 .log 檔案"))
                return
    
            total_files = len(target_files)
            total_steps = total_files + 1  # 總步數包含 Excel 生成
            self._ui_log(f"找到 {total_files} 個檔案開始分析...")
            
            # 2. 初始化進度條 (Thread-safe)
            self._safe_update_progress_mode('determinate')
            self._safe_update_progress_max(total_steps)
            
            pass_logs = []
            fail_logs = []
            skip_count = 0
            
            # 3. 逐一分析
            for i, file_path in enumerate(target_files):
                if self._cancel_flag:
                    self._ui_log("分析被使用者取消")
                    break
                    
                fname = os.path.basename(file_path)
                # 更新進度 (Thread-safe)
                self._safe_update_progress(i+1, total_steps, f"正在分析 ({i+1}/{total_files}): {fname}")
                
                try:
                    # 解析 (CPU bound, safe in thread)
                    result = self.log_parser.parse_log_file(file_path)
                    
                    # 提取測試時間日誌
                    test_time = "未知"
                    should_skip = False
                    try:
                        secs, time_logs = self.excel_writer._extract_total_secs(result['raw_lines'])
                        # 將詳細日誌輸出到 UI
                        for tlog in time_logs:
                            self._ui_log(tlog)
                            
                        if secs: 
                            test_time = f"{secs:.2f} 秒"
                        elif self.settings.get('skip_no_test_time', True):
                            self._ui_log(f"[\033[93mSKIP\033[0m] {fname}: 未找到測試總時間，已忽略", tag='summary_warning')
                            should_skip = True
                            skip_count += 1
                    except: 
                        pass
                    
                    if should_skip:
                        continue
                    
                    # 分析完成 (改為一般黑色，不使用綠色凸顯)
                    self._ui_log(f"[{i+1}/{total_files}] 分析完成: {fname} (時間: {test_time})")
                    
                    # 整理資料結構
                    header_info = self._extract_log_header_info(result['raw_lines'])
                    
                    log_entry = {
                        'file_path': file_path,
                        'file_name': fname,
                        'raw_lines': result['raw_lines'],
                        'ui_annotations': result.get('ui_annotations', []),
                        'pass_items': result['pass_items'],
                        'fail_items': result['fail_items'],
                        'last_fail': result.get('last_fail'),
                        'header_info': header_info,
                        'summary': {
                            'SFIS': 'Unknown', 
                            'FAIL原因': result.get('last_fail', {}).get('error', '') if result.get('last_fail') else ''
                        }
                    }
                    
                    if result['log_type'] == 'PASS': pass_logs.append(log_entry)
                    else: fail_logs.append(log_entry)
                           
                except Exception as e:
                    self._ui_log(f"[錯誤] 分析失敗 {fname}: {str(e)}")
                    continue
    
            # 4. 匯出 Excel
            if not self._cancel_flag:
                # 分析完畢，但進度條不應到達 100%，而是保留一步給 Excel
                self._safe_update_progress(total_files, total_steps, "分析完成，正在準備產生 Excel 報告...")
                final_summary = f"分析結束。pass logs : {len(pass_logs)}, fail logs: {len(fail_logs)}"
                if skip_count > 0:
                    final_summary += f", 忽略: {skip_count} log"
                self._ui_log(final_summary, tag='summary_info')
                
                # 根據成果動態顯示標籤頁
                self.root.after(0, lambda: self._update_tabs_visibility(len(pass_logs), len(fail_logs), is_multiple=True))
                try:
                    # 決定輸出目錄
                    out_dir = ""
                    current_path = self.current_log_path
                    
                    # 智慧判斷：如果是在暫存資料夾中，優先找原始壓縮檔所在處
                    is_temp = False
                    if isinstance(current_path, str):
                        if "AppData\\Local\\Temp" in current_path or "log_archives_" in current_path:
                            is_temp = True
                    
                    if is_temp:
                         # 嘗試從上次記錄的路徑取得目錄 (優先檢查壓縮檔資料夾，再檢查單一 Log 路徑)
                         if self.settings.get('last_compressed_folder') and os.path.exists(self.settings.get('last_compressed_folder')):
                             out_dir = self.settings.get('last_compressed_folder')
                         elif self.settings.get('last_folder_path') and os.path.exists(self.settings.get('last_folder_path')):
                             out_dir = self.settings.get('last_folder_path')
                         elif self.settings.get('last_log_path') and os.path.exists(self.settings.get('last_log_path')):
                             # 如果 last_log_path 是檔案，取其目錄；如果是目錄，直接使用
                             if os.path.isdir(self.settings.get('last_log_path')):
                                 out_dir = self.settings.get('last_log_path')
                             else:
                                 out_dir = os.path.dirname(self.settings.get('last_log_path'))
                         else:
                             # 最終 fallback：桌面 (比工作目錄更友善) 或 使用者目錄
                             out_dir = os.path.join(os.path.expanduser("~"), "Desktop")
                             if not os.path.exists(out_dir):
                                 out_dir = os.getcwd()
                                 
                         self._ui_log(f"偵測到暫存目錄，改為輸出至: {out_dir}")
                    elif isinstance(current_path, str) and os.path.exists(current_path):
                        if os.path.isdir(current_path):
                            out_dir = current_path
                        else:
                            out_dir = os.path.dirname(current_path)
                    elif isinstance(current_path, (list, tuple)):
                        if current_path and os.path.exists(current_path[0]):
                            out_dir = os.path.dirname(current_path[0])
                        else:
                            out_dir = os.getcwd()
                    else:
                        out_dir = os.getcwd()

                    self._ui_log(f"正在產生 Excel 至: {out_dir}")
                    # 此時更新進度到 100% 或幾乎 100%
                    self._safe_update_progress(total_files, total_steps, "正在產生 Excel 報告...")
                    
                    if hasattr(self, 'excel_writer'):
                        pass_path, fail_path, _ = self.excel_writer.export_pass_fail_workbooks(
                            out_dir, pass_logs, fail_logs
                        )
                        # 生成完成
                        msg_success = f"\033[92mExcel 生成成功！\033[0m 耗時 {int(time.time() - self.progress_manager._start_time)}s"
                        self._safe_update_progress(total_steps, total_steps, msg_success)
                        self._ui_log(f"\033[92mExcel 生成成功！\033[0m\n\033[96mPASS: {os.path.basename(pass_path)}\nFAIL: {os.path.basename(fail_path)}\033[0m", tag='summary_success')
                        # 使用 root.after 確保在主執行緒彈出
                        # 參數: out_dir, total_files, pass_count, fail_count, pass_path, fail_path
                        self.root.after(100, lambda: self._show_open_folder_prompt(
                            out_dir, total_files, len(pass_logs), len(fail_logs), pass_path, fail_path
                        ))
                except Exception as e:
                    self._ui_log(f"[錯誤] 匯出 Excel 失敗: {str(e)}")
                    traceback.print_exc()
                    self.root.after(0, lambda: messagebox.showerror("匯出錯誤", str(e)))
            else:
                self._ui_log(f"Excel 生成被取消")
                    
        except Exception as e:
            error_msg = f"多檔分析過程發生錯誤: {e}"
            print(f"[ERROR] {error_msg}")
            traceback.print_exc()
            self.root.after(0, lambda: messagebox.showerror("錯誤", error_msg))
        finally:
            # 確保結束時關閉進度條
            print(f"[DEBUG] 分析完成，關閉進度條")
            self.root.after(0, self._close_progress)
