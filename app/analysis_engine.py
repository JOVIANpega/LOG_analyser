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
            
            # CPU密集型操作 (解析 LOG)
            # 在背景執行緒執行解析，主執行緒會持續跑閃爍動畫
            result = self.log_parser.parse_log_file(self.current_log_path)
            
            # 短暫讓出系統資源，確保 UI 事件迴圈有喘息空間處理閃爍
            time.sleep(0.01)
            
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
        
        # 🟢 保存分析結果用於後續參考 (如搜尋圖片時需要的時間戳)
        self.last_analysis_result = result
        
        # 🟢 新增：自動填入 ISN 圖片檢索欄位 (優先從內文找，找不到再從檔名找)
        try:
            target_isn = ""
            # 1. 嘗試從 Header 內文找
            isn_match = re.search(r'ISN=([^\n\s]+)', str(header_info))
            if isn_match:
                target_isn = isn_match.group(1)
            else:
                # 2. 嘗試從目前檔案路徑 (檔名) 找
                from .excel.excel_utils import extract_isn_from_filename
                prefix = self.settings.get('image_search_isn_prefix', 'WE')
                target_isn = extract_isn_from_filename(self.current_log_path, prefix=prefix)
            
            if hasattr(self, 'isn_image_var'):
                # 如果有找到就填入，沒找到就清空 (User Requested: 不要保留上一筆)
                self.isn_image_var.set(target_isn)
        except Exception as e: 
            print(f"DEBUG: Auto-fill ISN failed: {e}")
        
        yield

        # Step 2: 所有測項流水線 (PASS 標籤頁顯示完整流程)
        self._update_progress(f"更新測試完整流程列表...")
        if hasattr(self, 'pass_tree_enhanced'):
            # 追蹤 Phase 是否已存在，避免重複顯示大標題
            seen_phases_map = {} # phase_name -> parent_id
            
            # 🟢 使用者要求：將 PASS/FAIL 項目按時間順序交叉排列
            all_flow_items = sorted(pass_items + fail_items, key=lambda x: x.get('raw_idx', 0))
            
            # 🟢 修正：僅標註與 FAIL 摘要一致的「主錯誤 Phase」
            # 我們從 result 中取得的 last_fail 包含其所屬 phase，這才是真正的錯誤點
            final_failing_phase = last_fail.get('phase') if last_fail else None
            
            for item in all_flow_items:
                phase_name = item.get('phase', 'Unknown Phase')
                
                # 如果是新的 Phase，建立大標題
                if phase_name not in seen_phases_map:
                    # 🟢 同步邏輯：僅在此主錯誤 Phase 標註 (FAIL HERE)
                    is_phase_fail = (final_failing_phase and phase_name == final_failing_phase)
                    p_id = self.pass_tree_enhanced.insert_phase_header(phase_name, is_fail=is_phase_fail)
                    seen_phases_map[phase_name] = p_id
                
                parent_id = seen_phases_map[phase_name]
                
                # 插入此測項內的所有比對結果 (Validations)
                validations = item.get('validations', [])
                for v in validations:
                    self.pass_tree_enhanced.insert_validation_item(
                        parent_id, 
                        v.get('content', ''), 
                        v.get('status', 'PASS'),
                        line_idx=v.get('line_idx')
                    )
        yield

        # Step 3: FAIL Items
        self._update_progress(f"更新 FAIL 列表 ({len(fail_items)} 筆)...")
        if hasattr(self, 'fail_tree_enhanced'):
            # 追蹤 Phase 是否已存在
            seen_phases_map = {} # phase_name -> parent_id
            
            # 🟢 使用者要求：僅針對最後有問題導致判定FAIL的顯示出來就好
            # 我們抓取 last_fail 所屬的 phase 作為主要顯示對象
            final_phase = last_fail.get('phase') if last_fail else None
            
            for idx, item in enumerate(fail_items):
                phase_name = item.get('phase', 'Unknown Phase')
                
                # 如果有明確的最後錯誤 Phase，則過濾掉其餘 Phase (Retry Pass 的部分)
                if final_phase and phase_name != final_phase:
                    continue
                
                # 如果是新的 Phase，建立大標題 (📘 Phase X ...)
                if phase_name not in seen_phases_map:
                    p_id = self.fail_tree_enhanced.insert_phase_header(phase_name)
                    seen_phases_map[phase_name] = p_id
                
                parent_id = seen_phases_map[phase_name]
                is_main_fail = item.get('is_main_fail', False)
                full_response = item.get('full_response', '')
                
                # 🟢 使用者要求：補上 FAIL在哪一個PHASE
                error_display = item['error']
                if phase_name and phase_name != "Unknown Phase":
                    # 在錯誤訊息前加上 [FAIL在 phase XX]
                    error_display = f"[FAIL在 {phase_name}] {error_display}"

                # 插入此測項
                step_id = self.fail_tree_enhanced.insert_fail_item(
                    (item['step_name'], error_display),
                    full_response=full_response,
                    is_main_fail=is_main_fail,
                    parent=parent_id
                )
                
                # 插入比對項目資訊 (如果有)
                validations = item.get('validations', [])
                for v in validations:
                    self.fail_tree_enhanced.insert_validation_item(
                        step_id, 
                        v.get('content', ''), 
                        v.get('status', 'PASS'),
                        line_idx=v.get('line_idx')
                    )
        yield

        # Step 4: Raw Logs
        self._update_progress("更新原始 LOG 視圖...")
        if raw_lines and hasattr(self, 'log_text_enhanced'):
            log_content = '\n'.join(raw_lines)
            
            # === 新增：提取錯誤預覽段落（將錯誤區塊置頂顯示）===
            error_preview_data = [] # 改用列表結構儲存 (內容, 行號)
            if fail_items:
                if result.get('ui_annotations'):
                    for ann in result['ui_annotations']:
                        # 提取所有標記為錯誤背景的行 (COLOR_ERROR_BG = #FFE1E1)
                        if ann.get('background') == '#FFE1E1':
                            line_txt = ann.get('line_content', '')
                            # 🟢 使用者要求：僅針對真正錯誤的反白
                            # 判定是否為「真正錯誤」(critical)
                            is_critical = False
                            
                            # 🟢 A. 優先檢查數值範圍 (Criteria)
                            criteria_match = re.search(r'=\s*([^ \(\)]+)\s*\(\s*([^,]+)\s*,\s*([^ \)]+)\s*\)', line_txt)
                            is_validation = False
                            if criteria_match:
                                is_validation = True
                                try:
                                    v = float(criteria_match.group(1)); l = float(criteria_match.group(2)); r = float(criteria_match.group(3))
                                    if not (l <= v <= r):
                                        is_critical = True
                                except: pass
                            
                            # 🟢 B. 若非數值判定，才檢查關鍵字
                            if not is_validation:
                                if any(k.lower() in line_txt.lower() for k in ["doesn't match", "is Fail", "FAIL", "ERROR"]):
                                    # 額外檢查：如果這一行是我們在 LogParser 中鎖定的最後錯誤行，更要反白
                                    if result.get('fail_line_idx') == ann.get('line_idx'):
                                        is_critical = True
                                    else:
                                        # 或是有關鍵字且不是一般的 root@ 提示符
                                        if "doesn't match" in line_txt.lower():
                                            is_critical = True
                            
                            error_preview_data.append({
                                'content': line_txt,
                                'line_idx': ann.get('line_idx'),
                                'is_critical': is_critical
                            })

            # NOTE: 已延遲插入以優化性能 (yield)
            # 現在傳入 ui_annotations 以便進行精確的行高亮（包含 Criteria 的綠色/紅粉色）
            self.log_text_enhanced.insert_log_with_highlighting(log_content, {
                'fail_line_idx': fail_line_idx,
                'pass_items': pass_items,
                'fail_items': fail_items
            }, header_content=header_info, ui_annotations=result.get('ui_annotations'), error_preview_data=error_preview_data)
            
            if fail_line_idx is not None and fail_line_idx < len(raw_lines):
                self.log_text_enhanced.highlight_error_block(fail_line_idx + 1, fail_line_idx + 1)
        yield

        # Step 5: Finalize
        self._update_progress("完成！")
        
        # 根據分析結果動態顯示/隱藏標籤頁
        self._update_tabs_visibility(len(pass_items), len(fail_items), is_multiple=False)

        # 自動切換到相關Tab (依照檔名優先判定)
        filename = os.path.basename(self.current_log_path).upper()
        is_pass_file = "PASS" in filename
        
        if is_pass_file:
            # 檔名有 PASS -> 切換到 PASS 測項
            try:
                if hasattr(self, 'notebook') and hasattr(self, 'tab_pass'):
                    self.notebook.select(self.tab_pass)
            except Exception:
                pass
        else:
            # 檔名沒有 PASS -> 視為 FAIL (或未完備)，切換到 FAIL 測項
            try:
                if hasattr(self, 'notebook') and hasattr(self, 'tab_fail'):
                    self.notebook.select(self.tab_fail)
                
                # 🟢 使用者要求：切換到 FAIL 分頁後就停止，不要跳到原始 LOG
                # 原本這裡會呼叫 _switch_to_log_and_focus_error，現在已移除
            except Exception as e:
                print(f"切換到FAIL分頁失敗: {e}")
                traceback.print_exc()
                    


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
            ]
            
            for pattern, label in patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    info_lines.append(match.group(1).strip())
            
            # 專門尋找測試總時間 (通常在檔尾)
            time_content = "\n".join(raw_lines[-200:]) # 搜尋最後 200 行
            time_match = re.search(r'All phase Total Test Time[\s!:\-]+([\d\.]+)\s*Sec', time_content, re.IGNORECASE)
            if time_match:
                info_lines.append(f"All phase Total Test Time ! ----- {time_match.group(1)} Sec.")
            else:
                # 嘗試另一種格式 "Total Test Time is 727.947 Sec"
                time_match2 = re.search(r'Total Test Time is[^0-9]*?([\d\.]+)\s*sec', time_content, re.IGNORECASE)
                if time_match2:
                    info_lines.append(f"All phase Total Test Time ! ----- {time_match2.group(1)} Sec.")
            
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
        display_path = getattr(self, 'original_log_path', self.current_log_path)
        
        path_str = ""
        if isinstance(display_path, (list, tuple)) and len(display_path) > 1:
            # 檢查是否所有檔案都在同一個目錄
            dirs = set(os.path.dirname(p) for p in display_path)
            if len(dirs) == 1:
                path_str = f"資料夾: {list(dirs)[0]}"
            else:
                path_str = str(display_path)
        else:
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

                    self._ui_log(f"正在產生 Excel 至: {out_dir}", tag='summary_highlight')
                    
                    # === 新增：集中到 生成的EXCEL報表 資料夾 ===
                    report_dir = os.path.join(out_dir, "生成的EXCEL報表")
                    try:
                        if not os.path.exists(report_dir):
                            os.makedirs(report_dir, exist_ok=True)
                        out_dir = report_dir
                        self._ui_log(f"-> 報表將集中存放於: {out_dir}")
                    except Exception as e:
                        print(f"建立 EXCEL報表 資料夾失敗: {e}")
                        # 失敗則維持原目錄
                    
                    # 此時更新進度到 100% 或幾乎 100%
                    self._safe_update_progress(total_files, total_steps, "正在產生 Excel 報告...")
                    
                    if hasattr(self, 'excel_writer'):
                        from .excel.excel_utils import extract_station_from_filename
                        
                        # 1. 分組邏輯：根據站別名稱將 logs 分類
                        log_groups = {} # station_name -> {'pass': [], 'fail': []}
                        
                        # 判斷是否為單一壓縮檔來源 (通常壓縮檔就代表一個完整的測試包)
                        is_single_archive = False
                        if isinstance(self.current_log_path, str) and (self.current_log_path.lower().endswith('.zip') or self.current_log_path.lower().endswith('.7z')):
                            is_single_archive = True
                            
                        if is_single_archive:
                            # 維持原有邏輯：僅分一組，名稱以後綴決定
                            prefix_name = extract_station_from_filename(self.current_log_path)
                            log_groups[prefix_name] = {'pass': pass_logs, 'fail': fail_logs}
                        else:
                            # 多檔或資料夾：按各自 log 的 station 分組
                            for log in pass_logs:
                                s = extract_station_from_filename(log.get('file_name', ''))
                                if s not in log_groups: log_groups[s] = {'pass': [], 'fail': []}
                                log_groups[s]['pass'].append(log)
                            for log in fail_logs:
                                s = extract_station_from_filename(log.get('file_name', ''))
                                if s not in log_groups: log_groups[s] = {'pass': [], 'fail': []}
                                log_groups[s]['fail'].append(log)
                                
                        all_generated_paths = [] # 儲存格式: (station_name, pass_path, fail_path)
                        processed_groups = 0
                        
                        # 2. 逐一產生各站別的報告
                        for station, data in log_groups.items():
                            if not data['pass'] and not data['fail']: continue
                            
                            self._ui_log(f"正在產生 [{station}] 的 Excel 報告...")
                            p_path, f_path, _ = self.excel_writer.export_pass_fail_workbooks(
                                out_dir, data['pass'], data['fail'], 
                                source_path=self.current_log_path if is_single_archive else None
                            )
                            all_generated_paths.append((station, p_path, f_path))
                            processed_groups += 1
                            self._ui_log(f"-> 站別 {station} 報告產出完成")

                        # 3. 生成完成訊息與提示
                        msg_success = f"\033[92mExcel 生成成功！(共產出 {processed_groups} 組站別)\033[0m"
                        self._safe_update_progress(total_steps, total_steps, msg_success)
                        self._ui_log(f"\033[92mExcel 匯出完成！共 {processed_groups} 個測試站類別。\033[0m", tag='summary_highlight')
                        
                        # 傳入所有生成的路徑列表
                        self.root.after(100, lambda: self._show_open_folder_prompt(
                            out_dir, total_files, len(pass_logs), len(fail_logs), all_generated_paths
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
