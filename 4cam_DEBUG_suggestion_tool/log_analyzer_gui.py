import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import re
from pathlib import Path
from collections import defaultdict
import json
import os
import pandas as pd

class LogAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LOG 錯誤分析工具 - 操作員版")
        self.root.geometry("1200x800")
        
        self.log_files = []
        self.log_data_cache = {}  # 儲存LOG數據以便查看完整內容
        self.font_size = 11  # 預設字體大小
        self.config_file = Path(__file__).parent / "user_config.json"
        self.solutions_file = Path(__file__).parent / "solutions.xlsx"
        self.error_solutions = [] # 儲存從Excel讀取的對策
        
        # 載入用戶設定
        self.load_user_config()
        
        # 載入對策資料庫
        self.load_solutions()
        
        self.create_widgets()
        
        # 視窗關閉時保存設定
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_widgets(self):
        # 頂部：文件選擇區域
        top_frame = tk.Frame(self.root, bg="#2c3e50", padx=15, pady=15)
        top_frame.pack(fill=tk.X)
        
        tk.Label(top_frame, text="選擇LOG檔案:", font=("微軟正黑體", 12, "bold"), 
                bg="#2c3e50", fg="white").pack(side=tk.LEFT, padx=5)
        
        self.file_count_var = tk.StringVar(value="尚未選擇檔案")
        tk.Label(top_frame, textvariable=self.file_count_var, font=("微軟正黑體", 11), 
                bg="#2c3e50", fg="#ecf0f1").pack(side=tk.LEFT, padx=10)
        
        browse_btn = tk.Button(top_frame, text="📁 批次選擇LOG", command=self.browse_files, 
                              bg="#27ae60", fg="white", font=("微軟正黑體", 12, "bold"), 
                              padx=20, pady=8, cursor="hand2")
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        # 雖然會自動分析，但保留按鈕以便手動重整
        analyze_btn = tk.Button(top_frame, text="🔍 重新分析", command=self.analyze_logs,
                               bg="#e74c3c", fg="white", font=("微軟正黑體", 12, "bold"), 
                               padx=20, pady=8, cursor="hand2")
        analyze_btn.pack(side=tk.LEFT, padx=5)
        
        # 編輯對策資料庫按鈕 (移至上方)
        edit_db_btn = tk.Button(top_frame, text="📝 編輯對策資料庫", command=self.open_solutions_file,
                               bg="#f39c12", fg="white", font=("微軟正黑體", 12, "bold"), 
                               padx=20, pady=8, cursor="hand2")
        edit_db_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(top_frame, text="🗑️ 清空", command=self.clear_results,
                             bg="#95a5a6", fg="white", font=("微軟正黑體", 12, "bold"), 
                             padx=15, pady=8, cursor="hand2")
        clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # 字體大小調整
        tk.Label(top_frame, text="字體:", font=("微軟正黑體", 12), 
                bg="#2c3e50", fg="white").pack(side=tk.RIGHT, padx=5)
        
        font_plus_btn = tk.Button(top_frame, text="A+", command=self.increase_font,
                                 bg="#34495e", fg="white", font=("微軟正黑體", 12, "bold"), 
                                 padx=10, pady=8, cursor="hand2")
        font_plus_btn.pack(side=tk.RIGHT, padx=2)
        
        font_minus_btn = tk.Button(top_frame, text="A-", command=self.decrease_font,
                                  bg="#34495e", fg="white", font=("微軟正黑體", 12, "bold"), 
                                  padx=10, pady=8, cursor="hand2")
        font_minus_btn.pack(side=tk.RIGHT, padx=2)
        
        # 中間：結果顯示區域
        result_frame = tk.Frame(self.root, padx=15, pady=10)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        # 搜尋框（頂部）
        search_frame = tk.Frame(result_frame, bg="#ecf0f1", pady=5)
        search_frame.pack(fill=tk.X)
        
        tk.Label(search_frame, text="🔍 搜尋:", font=("微軟正黑體", 12, "bold"), 
                bg="#ecf0f1").pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                               font=("微軟正黑體", 12), width=40)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(search_frame, text="搜尋", command=self.search_in_results,
                 bg="#3498db", fg="white", font=("微軟正黑體", 12, "bold"), 
                 padx=15, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=2)
        
        tk.Button(search_frame, text="清除高亮", command=self.clear_search,
                 bg="#95a5a6", fg="white", font=("微軟正黑體", 12, "bold"), 
                 padx=10, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=2)
        
        tk.Label(search_frame, text="(提示: Ctrl+F 快速搜尋)", 
                font=("微軟正黑體", 10), bg="#ecf0f1", fg="#7f8c8d").pack(side=tk.LEFT, padx=10)
        
        # 使用ScrolledText顯示結果
        self.result_text = scrolledtext.ScrolledText(result_frame, font=("微軟正黑體", 11), 
                                                     wrap=tk.WORD, bg="#ecf0f1", 
                                                     relief=tk.FLAT, padx=10, pady=10)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # 綁定Ctrl+F快捷鍵
        self.root.bind('<Control-f>', lambda e: search_entry.focus_set())
        search_entry.bind('<Return>', lambda e: self.search_in_results())
        
        # 配置文字顏色標籤
        self.update_font_size() # 初始化字體設定
        self.result_text.tag_config("search_highlight", background="yellow")
        
    def browse_files(self):
        """批次選擇LOG檔案"""
        filenames = filedialog.askopenfilenames(
            title="選擇LOG檔案（可多選）",
            initialdir=r"d:\((Python TOOL\4cam_DEBUG_suggestion_tool\LOG",
            filetypes=[("Log files", "*.log"), ("All files", "*.*")]
        )
        
        if filenames:
            self.log_files = list(filenames)
            self.file_count_var.set(f"已選擇 {len(self.log_files)} 個檔案")
            # 自動開始分析
            self.analyze_logs()
            
    def analyze_logs(self):
        """分析LOG檔案"""
        if not self.log_files:
            messagebox.showerror("錯誤", "請先選擇LOG檔案！")
            return
            
        self.clear_results()
        
        try:
            # 按ISN分組LOG檔案
            isn_groups = defaultdict(list)
            
            for log_file in self.log_files:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 提取ISN
                sn_match = re.search(r'ISN=(\w+)', content)
                isn = sn_match.group(1) if sn_match else "未知"
                
                isn_groups[isn].append({
                    'path': log_file,
                    'name': Path(log_file).name,
                    'content': content
                })
            
            # 檢查是否只有一個ISN
            if len(isn_groups) > 1:
                isn_list = "\n".join([f"• {isn} ({len(files)}個檔案)" 
                                     for isn, files in isn_groups.items()])
                messagebox.showerror("錯誤", 
                    f"選擇的LOG檔案包含多個不同的ISN！\n\n{isn_list}\n\n請只選擇同一個ISN的LOG檔案。")
                return
            
            # 獲取唯一的ISN和其LOG檔案
            isn = list(isn_groups.keys())[0]
            log_data_list = isn_groups[isn]
            
            # 顯示ISN資訊
            self.result_text.insert(tk.END, f" 設備序號: {isn} ", "big_title")
            self.result_text.insert(tk.END, f"\n共分析 {len(log_data_list)} 個LOG檔案\n\n", "info_header")
            
            # 1. 先分析所有LOG，收集結果
            analyzed_results = []
            total_errors = 0
            
            for idx, log_info in enumerate(log_data_list, 1):
                errors, is_pass, priority_score, phase_data = self.get_log_errors(log_info)
                analyzed_results.append({
                    'log_info': log_info,
                    'file_idx': idx,
                    'errors': errors,
                    'is_pass': is_pass,
                    'priority_score': priority_score,
                    'phases': phase_data['phases'],
                    'failed_phase_idx': phase_data['failed_idx']
                })
                total_errors += len(errors)
            
            # 2. 排序結果：優先級分數越小越前面 (0: doesn't match, 1: error, 2: pass)
            analyzed_results.sort(key=lambda x: x['priority_score'])
            
            # 3. 收集所有錯誤並去重（同一個 ISN 的相同錯誤只顯示一次）
            unique_errors = {}  # key: 錯誤訊息, value: 錯誤詳情
            
            for result in analyzed_results:
                for error in result['errors']:
                    # 使用錯誤訊息作為唯一鍵
                    error_key = error['message']
                    if error_key not in unique_errors:
                        unique_errors[error_key] = error
            
            # 4. 顯示每個 LOG 的標題和狀態（不顯示錯誤詳情）
            for result in analyzed_results:
                self.display_log_result(result, show_errors=False)
            
            # 5. 在所有 LOG 顯示完後，統一顯示去重後的錯誤
            if unique_errors:
                self.result_text.insert(tk.END, "\n" + "═" * 80 + "\n", "separator")
                self.result_text.insert(tk.END, "\n 🔍 錯誤分析總結 \n\n", "big_title")
                self.result_text.insert(tk.END, f"此批 LOG 共發現 {len(unique_errors)} 種錯誤類型：\n\n", "info_header")
                
                # 將錯誤轉為列表並排序（doesn't match 優先）
                unique_error_list = list(unique_errors.values())
                unique_error_list.sort(key=lambda x: x['priority'])
                
                # 最多顯示 3 種錯誤
                display_limit = 3
                for idx, error in enumerate(unique_error_list[:display_limit], 1):
                    solution = self.find_solution(error['message'])
                    self.display_error_simple(error, idx, solution)
                
                if len(unique_error_list) > display_limit:
                    self.result_text.insert(tk.END, f"... 還有 {len(unique_error_list) - display_limit} 種錯誤（請查看完整LOG）\n\n", "normal")
            
            # 顯示總結
            self.result_text.insert(tk.END, "\n" + "═" * 80 + "\n", "separator")
            if total_errors == 0:
                self.result_text.insert(tk.END, "\n ✅ 所有測試通過 - 無錯誤 \n", "pass_title")
                self.result_text.insert(tk.END, "\n此批LOG沒有發現問題，設備測試正常通過。\n", "normal")
            else:
                self.result_text.insert(tk.END, f"\n ❌ 總計發現 {total_errors} 個錯誤 \n", "big_title")
                
        except Exception as e:
            messagebox.showerror("錯誤", f"分析LOG檔案時出錯:\n{str(e)}")
            import traceback
            traceback.print_exc()

    def get_log_errors(self, log_info):
        """分析單一LOG內容，返回錯誤列表和狀態"""
        content = log_info['content']
        log_name = log_info['name']
        
        # 【關鍵】檔案名沒有PASS就是FAIL
        filename_has_pass = "PASS" in log_name.upper()
        
        # 檢查是否通過測試（檔案名 + 內容）
        content_has_pass = "All Test Pass" in content
        content_has_abort = "All Test Aborted" in content or "Test is Fail" in content
        
        # 真正的PASS條件：檔案名有PASS 且 內容有All Test Pass 且 沒有Aborted
        is_pass = filename_has_pass and content_has_pass and not content_has_abort
        
        errors_found = []
        
        # 優先級1: doesn't match (最高優先級)
        for match in re.finditer(r"doesn't match", content, re.IGNORECASE):
            error_pos = match.start()
            
            # 1. 往上找最近的時間戳
            timestamp = "未知時間"
            search_start = max(0, error_pos - 5000)
            before_text = content[search_start:error_pos]
            time_matches = list(re.finditer(r'(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})', before_text))
            if time_matches:
                timestamp = time_matches[-1].group(1)
            
            # 2. 往上找最近的指令
            command_context = self.extract_command_context(content, error_pos)
            
            # 3. 提取錯誤訊息
            line_start = content.rfind('\n', 0, error_pos) + 1
            line_end = content.find('\n', error_pos)
            if line_end == -1: line_end = len(content)
            error_msg = content[line_start:line_end].strip()
            line_num = content[:error_pos].count('\n') + 1
            
            errors_found.append({
                'priority': 1,
                'type': "doesn't match",
                'line': line_num,
                'time': timestamp,
                'message': error_msg,
                'command_context': command_context
            })
        
        # 優先級2: ERROR/FAIL
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            if any(e['line'] == line_num for e in errors_found):
                continue
            
            if ('ERROR' in line.upper() or 'FAIL' in line.upper()) and \
               'Test is Pass' not in line and 'PASS' not in line:
                time_match = re.search(r'(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})', line)
                timestamp = time_match.group(1) if time_match else "未知"
                command_context = self.find_command_in_lines(lines, line_num - 1)
                
                errors_found.append({
                    'priority': 2,
                    'type': 'ERROR/FAIL',
                    'line': line_num,
                    'time': timestamp,
                    'message': line.strip(),
                    'command_context': command_context
                })
        
        errors_found.sort(key=lambda x: x['priority'])
        
        # 過濾邏輯
        has_doesnt_match = any(e['type'] == "doesn't match" for e in errors_found)
        if has_doesnt_match:
            errors_found = [e for e in errors_found if e['type'] == "doesn't match"]
            priority_score = 0 # 最高優先級
        elif errors_found:
            priority_score = 1 # 次高優先級
        else:
            priority_score = 2 # 無錯誤
            
        # 提取測試階段 (Phases)
        phases = []
        phase_matches = list(re.finditer(r"Execute Phase (\d+).*", content, re.IGNORECASE))
        
        failed_phase_idx = -1
        last_valid_phase_idx = -1
        
        # 1. 構建 Phase 列表
        for i, match in enumerate(phase_matches):
            phase_num = int(match.group(1))
            start_pos = match.start()
            # 下一個 phase 的開始位置，或是檔案結尾
            end_pos = phase_matches[i+1].start() if i < len(phase_matches) - 1 else len(content)
            
            phase_info = {
                'name': match.group(0).strip(),
                'number': phase_num,
                'start_pos': start_pos,
                'end_pos': end_pos,
                'last_command': None
            }
            phases.append(phase_info)
            
            # 記錄最後一個有效 Phase (< 90)
            if phase_num < 90:
                last_valid_phase_idx = i

        # 2. 如果有錯誤或未通過，找出需要標紅的 Phase 並提取指令
        if (not is_pass or errors_found) and last_valid_phase_idx != -1:
            failed_phase_idx = last_valid_phase_idx
            target_phase = phases[failed_phase_idx]
            
            # 在該 Phase 範圍內尋找最後一個指令
            phase_content = content[target_phase['start_pos']:target_phase['end_pos']]
            
            # 使用與 extract_command_context 類似的邏輯
            cmd_patterns = [
                r'\((LAN|UART|CmdConsole|ADB|[^\)]+)\)\s*>\s*([^\r\n]+)',
                r'(LAN|UART|CmdConsole|ADB|[^@\s]+)@([^\r\n]+)'
            ]
            
            # 收集所有指令候選者
            candidates = []
            for pattern in cmd_patterns:
                for match in re.finditer(pattern, phase_content):
                    candidates.append({
                        'pos': match.start(),
                        'type': match.group(1),
                        'content': match.group(2).strip()
                    })
            
            # 按位置排序
            candidates.sort(key=lambda x: x['pos'])
            
            # 過濾邏輯：從後往前找，忽略包含特定關鍵字的指令
            ignore_keywords = ["Skipped", "run mode is", "echo"]
            selected_cmd = None
            
            if candidates:
                # 預設選最後一個
                selected_cmd = candidates[-1]
                
                # 嘗試往前找更好的
                for cmd in reversed(candidates):
                    cmd_text = cmd['content']
                    is_noise = any(kw.lower() in cmd_text.lower() for kw in ignore_keywords)
                    if not is_noise:
                        selected_cmd = cmd
                        break
            
            if selected_cmd:
                target_phase['last_command'] = f"{selected_cmd['type']}@{selected_cmd['content']}"

        return errors_found, is_pass, priority_score, {'phases': phases, 'failed_idx': failed_phase_idx}

    def display_log_result(self, result, show_errors=True):
        """顯示單一LOG的分析結果"""
        log_info = result['log_info']
        file_idx = result['file_idx']
        errors_found = result['errors']
        is_pass = result['is_pass']
        
        content = log_info['content']
        log_name = log_info['name']
        log_path = log_info['path']
        
        # 儲存數據到cache
        log_key = f"log_{file_idx}"
        self.log_data_cache[log_key] = {
            'content': content,
            'name': log_name,
            'path': log_path,
            'errors': errors_found
        }
        
        # 顯示LOG檔案標題
        self.result_text.insert(tk.END, f"\n【檔案 {file_idx}】{log_name}  ", "info_header")
        
        # 添加「查看完整LOG」按鈕
        view_tag = f"view_log_{file_idx}"
        self.result_text.insert(tk.END, "📄 查看完整LOG", view_tag)
        self.result_text.tag_config(view_tag, foreground="#3498db", underline=True, font=("微軟正黑體", 10, "bold"))
        self.result_text.tag_bind(view_tag, "<Button-1>", lambda e, key=log_key: self.show_full_log(key))
        self.result_text.tag_bind(view_tag, "<Enter>", lambda e, tag=view_tag: self.result_text.config(cursor="hand2"))
        self.result_text.tag_bind(view_tag, "<Leave>", lambda e: self.result_text.config(cursor=""))
        self.result_text.insert(tk.END, "\n", "normal")
        
        # 顯示測試進度
        phases = result.get('phases', [])
        failed_idx = result.get('failed_phase_idx', -1)
        
        if phases:
            self.result_text.insert(tk.END, " 📋 測試進度: \n", "info_header")
            for i, phase in enumerate(phases):
                phase_name = phase['name']
                
                # 如果是判定為失敗的階段，顯示紅色
                if i == failed_idx:
                    self.result_text.insert(tk.END, f"   -> {phase_name}\n", "phase_error_red")
                    
                    # 顯示該階段最後執行的指令
                    if phase.get('last_command'):
                        cmd = phase['last_command']
                        # 去除類型前綴，只顯示指令內容
                        if "@" in cmd:
                            cmd = cmd.split("@", 1)[1]
                        self.result_text.insert(tk.END, f"      └── 最後指令: {cmd}\n", "cmd_error_red")
                else:
                    self.result_text.insert(tk.END, f"   -> {phase_name}\n", "reason_text")
            self.result_text.insert(tk.END, "\n", "normal")
        
        if is_pass and not errors_found:
            self.result_text.insert(tk.END, " ✅ PASS ", "pass_title")
            self.result_text.insert(tk.END, "\n", "normal")
            return
        
        # 如果不顯示錯誤詳情，只顯示錯誤數量
        if not show_errors:
            if errors_found:
                self.result_text.insert(tk.END, f" ⚠️ 發現 {len(errors_found)} 個錯誤 \n", "warning_box")
            return
        
        # 顯示錯誤詳情
        display_limit = 3  # 最多顯示 3 筆錯誤
        if errors_found:
            self.result_text.insert(tk.END, f" ⚠️ 發現 {len(errors_found)} 個錯誤 \n\n", "warning_box")
            
            shown_suggestion = False
            
            for idx, error in enumerate(errors_found[:display_limit], 1):
                solution = self.find_solution(error['message'])
                self.display_error_simple(error, idx, solution)
                if solution:
                    shown_suggestion = True
                
            if len(errors_found) > display_limit:
                self.result_text.insert(tk.END, f"... 還有 {len(errors_found) - display_limit} 個錯誤（請查看完整LOG）\n\n", "normal")
            
            if not shown_suggestion:
                self.result_text.insert(tk.END, "🔧 建議處理：\n", "info_header")
                self.result_text.insert(tk.END, "   1. 記錄上方錯誤訊息與執行指令\n", "action_text")
                self.result_text.insert(tk.END, "   2. 聯繫工程師進行診斷\n", "action_text")
                
                edit_tag = f"edit_db_{file_idx}"
                self.result_text.insert(tk.END, "   (點擊此處可打開Excel新增此錯誤的解決方案)\n", edit_tag)
                self.result_text.tag_config(edit_tag, foreground="#f39c12", underline=True, font=("微軟正黑體", 10))
                self.result_text.tag_bind(edit_tag, "<Button-1>", lambda e: self.open_solutions_file())
                self.result_text.tag_bind(edit_tag, "<Enter>", lambda e, tag=edit_tag: self.result_text.config(cursor="hand2"))
                self.result_text.tag_bind(edit_tag, "<Leave>", lambda e: self.result_text.config(cursor=""))
                self.result_text.insert(tk.END, "\n", "normal")
    
    def extract_command_context(self, content, error_pos):
        """提取錯誤附近的命令 (LAN/UART/CmdConsole/ADB)"""
        # 優化：擴大搜尋範圍至 10000 個字元，避免因輸出過長而找不到指令
        start_pos = max(0, error_pos - 10000)
        before_text = content[start_pos:error_pos]
        
        # 支援兩種格式：
        # 1. (LAN) > command
        # 2. LAN@command
        
        patterns = [
            r'\((LAN|UART|CmdConsole|ADB|[^\)]+)\)\s*>\s*([^\r\n]+)',  # (TYPE) > CMD
            r'(LAN|UART|CmdConsole|ADB|[^@\s]+)@([^\r\n]+)'            # TYPE@CMD
        ]
        
        last_match = None
        last_match_pos = -1
        
        for pattern in patterns:
            matches = list(re.finditer(pattern, before_text))
            if matches:
                current_last = matches[-1]
                if current_last.start() > last_match_pos:
                    last_match = current_last
                    last_match_pos = current_last.start()
        
        if last_match:
            cmd_type = last_match.group(1)
            cmd_content = last_match.group(2).strip()
            return f"{cmd_type}@{cmd_content}" # 統一顯示格式
            
        return None

    def find_command_in_lines(self, lines, current_idx):
        """在行列表中往前尋找命令"""
        # 往前最多找 100 行 (增加範圍)
        start_idx = max(0, current_idx - 100)
        for i in range(current_idx, start_idx - 1, -1):
            line = lines[i]
            
            # 檢查是否有命令特徵
            # 1. (LAN) > command
            match1 = re.search(r'\((LAN|UART|CmdConsole|ADB|[^\)]+)\)\s*>\s*([^\r\n]+)', line)
            if match1:
                return f"{match1.group(1)}@{match1.group(2).strip()}"
                
            # 2. LAN@command
            match2 = re.search(r'(LAN|UART|CmdConsole|ADB|[^@\s]+)@([^\r\n]+)', line)
            if match2:
                return f"{match2.group(1)}@{match2.group(2).strip()}"
                
        return None
        
    def display_error_simple(self, error, idx, solution=None):
        """簡化的錯誤顯示"""
        self.result_text.insert(tk.END, f"┌{'─' * 78}┐\n", "separator")
        
        # 大標題錯誤編號
        self.result_text.insert(tk.END, f" 錯誤 {idx} ", "error_box")
        self.result_text.insert(tk.END, f"  [第{error['line']}行 @ {error['time']}]\n\n", "info_header")
        
        # 顯示導致錯誤的命令（如果有）
        if error.get('command_context'):
            cmd_full = error['command_context']
            # 嘗試只提取指令部分，去除 LAN@ 等前綴
            if "@" in cmd_full:
                cmd_clean = cmd_full.split("@", 1)[1]
            else:
                cmd_clean = cmd_full
                
            self.result_text.insert(tk.END, "🔸 執行的命令（可能原因）：", "info_header")
            self.result_text.insert(tk.END, f"{cmd_clean} 引起錯誤\n", "cmd_error_red")
            self.result_text.insert(tk.END, "   (此指令執行後出現錯誤，可能是此功能異常)\n\n", "reason_text")
        
        # 錯誤內容
        self.result_text.insert(tk.END, "🔴 錯誤訊息：\n", "info_header")
        short_msg = self.simplify_error_message(error['message'])
        self.result_text.insert(tk.END, f"   {short_msg}\n\n", "error_content")
        
        # 對策（如果有特定對策才顯示）
        if solution:
            self.result_text.insert(tk.END, "💡 可能原因：\n", "info_header")
            self.result_text.insert(tk.END, f"   {solution['可能原因']}\n\n", "reason_text")
            
            self.result_text.insert(tk.END, "🔧 維修步驟：\n", "info_header")
            # 處理換行符號
            steps = str(solution['維修步驟']).split('\n')
            for step in steps:
                self.result_text.insert(tk.END, f"   {step}\n", "action_text")
            
        self.result_text.insert(tk.END, f"\n└{'─' * 78}┘\n\n", "separator")

    def simplify_error_message(self, msg):
        """簡化錯誤訊息，只保留關鍵部分"""
        # 移除時間戳記
        msg = re.sub(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2} \[\d+\]\s*', '', msg)
        
        # 如果太長，截斷
        if len(msg) > 150:
            msg = msg[:150] + "..."
            
        return msg.strip()
        
    def find_solution(self, error_message):
        """根據錯誤訊息查找對策 (Excel)"""
        if not self.error_solutions:
            return None
            
        for solution in self.error_solutions:
            keyword = str(solution.get('錯誤關鍵字', ''))
            if keyword and keyword.lower() in error_message.lower():
                return solution
        return None
            
    def load_solutions(self):
        """載入對策資料庫 (Excel)"""
        try:
            if self.solutions_file.exists():
                df = pd.read_excel(self.solutions_file)
                # 轉換為字典列表，方便查詢
                self.error_solutions = df.to_dict('records')
            else:
                # 如果檔案不存在，創建一個空的（或帶有預設值的）
                # 這裡我們依賴外部已經創建好的檔案，或者可以在這裡創建
                pass
        except Exception as e:
            print(f"載入對策資料庫失敗: {e}")
            self.error_solutions = []
            
    def open_solutions_file(self):
        """打開對策資料庫文件進行編輯"""
        try:
            os.startfile(self.solutions_file)
        except Exception as e:
            messagebox.showerror("錯誤", f"無法打開文件: {e}")
            
    def clear_results(self):
        """清空結果顯示"""
        self.result_text.delete(1.0, tk.END)
    
    def increase_font(self):
        """增加字體大小"""
        if self.font_size < 20:
            self.font_size += 1
            self.update_font_size()
            self.save_user_config() # 立即儲存
    
    def decrease_font(self):
        """減少字體大小"""
        if self.font_size > 8:
            self.font_size -= 1
            self.update_font_size()
            self.save_user_config() # 立即儲存
    
    def update_font_size(self):
        """更新主界面字體大小"""
        self.result_text.config(font=("微軟正黑體", self.font_size))
        # 更新所有tag的字體大小
        self.result_text.tag_config("big_title", font=("微軟正黑體", self.font_size + 9, "bold"))
        self.result_text.tag_config("pass_title", font=("微軟正黑體", self.font_size + 7, "bold"))
        self.result_text.tag_config("error_box", font=("微軟正黑體", self.font_size + 3, "bold"))
        self.result_text.tag_config("warning_box", font=("微軟正黑體", self.font_size + 2, "bold"))
        self.result_text.tag_config("info_header", font=("微軟正黑體", self.font_size + 1, "bold"))
        self.result_text.tag_config("error_content", font=("Consolas", self.font_size + 1, "bold"))
        self.result_text.tag_config("reason_text", font=("微軟正黑體", self.font_size))
        self.result_text.tag_config("action_text", font=("微軟正黑體", self.font_size, "bold"))
        self.result_text.tag_config("normal", font=("微軟正黑體", self.font_size - 1))
        # 新增紅色指令錯誤樣式
        self.result_text.tag_config("cmd_error_red", font=("微軟正黑體", self.font_size + 1, "bold"), foreground="red")
        self.result_text.tag_config("phase_error_red", font=("微軟正黑體", self.font_size, "bold"), foreground="red")
    
    def search_in_results(self):
        """在結果中搜尋"""
        query = self.search_var.get()
        if not query:
            return
        
        # 清除之前的高亮
        self.result_text.tag_remove("search_highlight", "1.0", tk.END)
        
        # 搜尋並高亮
        idx = "1.0"
        count = 0
        while True:
            idx = self.result_text.search(query, idx, nocase=True, stopindex=tk.END)
            if not idx:
                break
            lastidx = f"{idx}+{len(query)}c"
            self.result_text.tag_add("search_highlight", idx, lastidx)
            idx = lastidx
            count += 1
        
        # 跳到第一個匹配
        if count > 0:
            first_idx = self.result_text.search(query, "1.0", nocase=True, stopindex=tk.END)
            if first_idx:
                self.result_text.see(first_idx)
            messagebox.showinfo("搜尋結果", f"找到 {count} 個匹配項")
        else:
            messagebox.showinfo("搜尋結果", "未找到匹配項")
    
    def clear_search(self):
        """清除搜尋高亮"""
        self.result_text.tag_remove("search_highlight", "1.0", tk.END)
    
    def load_user_config(self):
        """載入用戶設定"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.font_size = config.get('font_size', 11)
                    
                    # 設定視窗大小和位置
                    window_geometry = config.get('window_geometry', None)
                    if window_geometry:
                        self.root.geometry(window_geometry)
        except Exception as e:
            print(f"載入設定失敗: {e}")
    
    def save_user_config(self):
        """保存用戶設定"""
        try:
            config = {
                'font_size': self.font_size,
                'window_geometry': self.root.geometry()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存設定失敗: {e}")
    
    def on_closing(self):
        """視窗關閉時保存設定"""
        self.save_user_config()
        self.root.destroy()
    
    def show_full_log(self, log_key):
        """顯示完整LOG內容（新視窗）"""
        if log_key not in self.log_data_cache:
            messagebox.showerror("錯誤", "無法找到LOG數據！")
            return
        
        log_data = self.log_data_cache[log_key]
        content = log_data['content']
        log_name = log_data['name']
        raw_errors = log_data['errors']
        
        # 錯誤過濾邏輯
        # 1. 優先顯示 doesn't match
        doesnt_match_errors = [e for e in raw_errors if e['type'] == "doesn't match"]
        
        if doesnt_match_errors:
            errors = doesnt_match_errors
        elif raw_errors:
            # 2. 如果沒有 doesn't match，只顯示最後一個錯誤
            errors = [raw_errors[-1]]
        else:
            errors = []
        
        # 創建新視窗
        log_window = tk.Toplevel(self.root)
        log_window.title(f"完整LOG - {log_name}")
        log_window.geometry("1400x900")
        
        # 頂部框架 - 錯誤總覽
        top_frame = tk.Frame(log_window, bg="#c0392b", padx=15, pady=10)
        top_frame.pack(fill=tk.X)
        
        tk.Label(top_frame, text=f"📋 {log_name}", 
                font=("微軟正黑體", 14, "bold"), bg="#c0392b", fg="white").pack(anchor=tk.W)
        
        # 錯誤總覽區域
        if errors:
            error_summary_frame = tk.Frame(log_window, bg="#ffe6e6", padx=15, pady=10)
            error_summary_frame.pack(fill=tk.X)
            
            tk.Label(error_summary_frame, text=f"❌ 錯誤總覽（共 {len(errors)} 個）- 點擊可跳轉", 
                    font=("微軟正黑體", 12, "bold"), bg="#ffe6e6", fg="#c0392b").pack(anchor=tk.W)
            
            # 錯誤列表（可點擊）
            summary_text = tk.Text(error_summary_frame, height=8, font=("微軟正黑體", 10), 
                                 bg="#ffe6e6", relief=tk.FLAT)
            summary_text.pack(fill=tk.X)
            
            for i, error in enumerate(errors, 1):
                line_num = error['line']
                msg = error['message'][:80] + "..." if len(error['message']) > 80 else error['message']
                # 確保 cmd 有值，如果是 None 則顯示未知
                cmd = error.get('command_context')
                if not cmd:
                    cmd = "未知指令"
                
                tag = f"error_{i}"
                
                # 顯示格式：[指令] -> 錯誤訊息
                summary_text.insert(tk.END, f"{i}. ", "bold")
                summary_text.insert(tk.END, f"[{cmd}] ", "cmd_summary")
                summary_text.insert(tk.END, f"第{line_num}行: {msg}\n", tag)
                
                # 點擊跳轉
                summary_text.tag_bind(tag, "<Button-1>", 
                                    lambda e, ln=line_num: self.scroll_to_line(log_text, ln))
                summary_text.tag_config(tag, foreground="blue", underline=True)
                summary_text.tag_bind(tag, "<Enter>", lambda e: summary_text.config(cursor="hand2"))
                summary_text.tag_bind(tag, "<Leave>", lambda e: summary_text.config(cursor=""))
            
            summary_text.tag_config("cmd_summary", foreground="#d35400", font=("微軟正黑體", 10, "bold"))
            summary_text.tag_config("bold", font=("微軟正黑體", 10, "bold"))

        # 搜尋框
        search_frame = tk.Frame(log_window, bg="#ecf0f1", pady=5)
        search_frame.pack(fill=tk.X)
        
        tk.Label(search_frame, text="🔍 搜尋內容:", font=("微軟正黑體", 11), bg="#ecf0f1").pack(side=tk.LEFT, padx=5)
        
        # 設定預設搜尋文字為 "doesn't match"
        search_var = tk.StringVar(value="doesn't match")
        search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        def search_log(event=None): # 支援事件綁定
            query = search_var.get()
            if not query: return
            log_text.tag_remove("search", "1.0", tk.END)
            idx = "1.0"
            while True:
                idx = log_text.search(query, idx, nocase=True, stopindex=tk.END)
                if not idx: break
                lastidx = f"{idx}+{len(query)}c"
                log_text.tag_add("search", idx, lastidx)
                idx = lastidx
            
            first = log_text.search(query, "1.0", nocase=True, stopindex=tk.END)
            if first: log_text.see(first)

        tk.Button(search_frame, text="搜尋", command=search_log, bg="#3498db", fg="white").pack(side=tk.LEFT)
        
        # 綁定 Enter 鍵
        search_entry.bind('<Return>', search_log)
        
        # 字體大小控制
        font_size = tk.IntVar(value=11)
        def update_log_font():
            log_text.config(font=("Consolas", font_size.get()))
            
        tk.Button(search_frame, text="A+", command=lambda: [font_size.set(min(20, font_size.get()+1)), update_log_font()],
                 width=3).pack(side=tk.RIGHT, padx=2)
        tk.Button(search_frame, text="A-", command=lambda: [font_size.set(max(8, font_size.get()-1)), update_log_font()],
                 width=3).pack(side=tk.RIGHT, padx=2)

        # LOG內容顯示
        log_text = scrolledtext.ScrolledText(log_window, font=("Consolas", 11), wrap=tk.NONE)
        log_text.pack(fill=tk.BOTH, expand=True)
        
        log_text.insert(tk.END, content)
        
        # 高亮顯示
        # 1. 錯誤行 (紅底白字，反白顯示)
        for error in errors:
            line_num = error['line']
            log_text.tag_add("error_line", f"{line_num}.0", f"{line_num}.end")
            
        log_text.tag_config("error_line", background="#e74c3c", foreground="white", font=("Consolas", 11, "bold"))
        log_text.tag_config("search", background="#e74c3c", foreground="white", font=("Consolas", 11, "bold"))
        
        # 2. PASS/FAIL 關鍵字
        self.highlight_pattern(log_text, r"PASS", "pass_tag", "#d4edda", "#155724")
        self.highlight_pattern(log_text, r"FAIL", "fail_tag", "#f8d7da", "#721c24")
        self.highlight_pattern(log_text, r"ERROR", "fail_tag", "#f8d7da", "#721c24")
        
        # 3. 時間戳
        self.highlight_pattern(log_text, r"\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}", "time_tag", None, "#666666")
        
        # 4. 命令
        self.highlight_pattern(log_text, r"\((LAN|UART|CmdConsole|[^\)]+)\)\s*>\s*[^\r\n]+", "cmd_tag", "#e8f6f3", "#000000")
        self.highlight_pattern(log_text, r"(LAN|UART|CmdConsole|[^@\s]+)@([^\r\n]+)", "cmd_tag", "#e8f6f3", "#000000")

        # 5. 測試階段 (Phase) - 深綠色
        self.highlight_pattern(log_text, r"Execute Phase \d+.*", "phase_tag", None, "#006400")
        log_text.tag_config("phase_tag", foreground="#006400", font=("Consolas", 11, "bold"))

    def highlight_pattern(self, text_widget, pattern, tag, bg, fg):
        """高亮特定模式"""
        idx = "1.0"
        while True:
            idx = text_widget.search(pattern, idx, regexp=True, stopindex=tk.END)
            if not idx: break
            
            # 計算匹配長度
            match_len = 0
            # 這裡簡單處理，實際上應該用match object，但tkinter search只返回位置
            # 我們假設匹配到行尾或空格，這裡簡化處理
            # 為了準確，我們重新在該行匹配
            line_idx = idx.split('.')[0]
            line_text = text_widget.get(f"{line_idx}.0", f"{line_idx}.end")
            col_idx = int(idx.split('.')[1])
            
            match = re.search(pattern, line_text[col_idx:])
            if match:
                match_len = match.end() - match.start()
                lastidx = f"{idx}+{match_len}c"
                text_widget.tag_add(tag, idx, lastidx)
                idx = lastidx
            else:
                idx = f"{idx}+1c"

        if bg: text_widget.tag_config(tag, background=bg)
        if fg: text_widget.tag_config(tag, foreground=fg)

    def scroll_to_line(self, text_widget, line_num):
        """捲動到指定行"""
        text_widget.see(f"{line_num}.0")
        # 閃爍效果
        text_widget.tag_add("flash", f"{line_num}.0", f"{line_num}.end")
        text_widget.tag_config("flash", background="#e74c3c", foreground="white", font=("Consolas", 11, "bold"))
        self.root.after(1000, lambda: text_widget.tag_remove("flash", f"{line_num}.0", f"{line_num}.end"))
