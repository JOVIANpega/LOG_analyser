# log_parser.py
# 用途：基於檔名判斷PASS/FAIL，使用不同分析邏輯的測試log解析器
import re
import os
from pathlib import Path
from datetime import datetime, timedelta

class LogParser:
    def __init__(self):
        # 正則表達式模式
        self.step_pattern = re.compile(r'Do\s+(@STEP\d+@[^@\n]+)')
        self.test_id_pattern = re.compile(r'Run ([A-Z0-9]+-\d+):')
        # 放寬：支援 (XXX) 或 [XXX] 或無前綴的指令/回應行，例如：
        # "> :Delay,\"1000\""、"< 0"、"(PC) > :..."、"[DUT] < ..."
        self.cmd_pattern = re.compile(r'(?:\([A-Za-z0-9_ ]+\)|\[[A-Za-z0-9_ ]+\])?\s*>\s*(.+)')
        self.resp_pattern = re.compile(r'(?:\([A-Za-z0-9_ ]+\)|\[[A-Za-z0-9_ ]+\])?\s*<\s*(.+)')
        self.retry_pattern = re.compile(r'Retry:\s*(\d+)')
        self.root_pattern = re.compile(r'root@.*:/root\$')
        self.fail_keywords = [
            'FAIL', 'FAILED', 'ERROR', 'failed', 'error', 'NACK', 'timeout', 
            "doesn't match", "does not match", "Status:False"
        ]
        self.phase_pattern = re.compile(r'Execute (Phase \d+ Test)', re.IGNORECASE)

    def parse_log_file(self, file_path):
        """
        解析單一log檔案，基於檔名判斷PASS/FAIL並使用不同的分析邏輯
        保持與現有GUI模組相容的資料結構
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"讀取檔案失敗: {e}")
            return self._empty_result()
        
        raw_lines = [line.rstrip('\n') for line in lines]
        
        # 1. 依檔名判斷PASS/FAIL
        file_name = Path(file_path).name.upper()
        is_pass_log = "PASS" in file_name
        
        # 產生UI標註資訊
        ui_annotations = self._generate_ui_annotations(raw_lines, is_pass_log)
        
        # 提取時間資訊 (用於圖片比對)
        abs_times = self._extract_absolute_times(file_name, raw_lines)
        
        if is_pass_log:
            result = self._parse_pass_log(raw_lines, file_path)
        else:
            result = self._parse_fail_log(raw_lines, file_path)
        
        # 添加UI標註資訊與時間資訊
        result['ui_annotations'] = ui_annotations
        result['test_start_dt'] = abs_times['start']
        result['test_end_dt'] = abs_times['end']
        return result
    
    def _empty_result(self):
        """回傳空結果"""
        return {
            'pass_items': [],
            'fail_items': [],
            'raw_lines': [],
            'last_fail': None,
            'fail_line_idx': None,
            'log_type': 'UNKNOWN',
            'test_start_dt': None,
            'test_end_dt': None
        }

    def _extract_absolute_times(self, file_name, raw_lines):
        """
        從檔名提取日期 (YYYYMMDD) 並從 Log 內容提取開始/結束時間 (HH:MM:SS)
        """
        res = {'start': None, 'end': None}
        try:
            # 1. 從檔名提取日期與初步時間 (如果有 14 位數字如 20260105140143)
            date_str = ""
            file_dt = None
            full_ts_match = re.search(r'(\d{14})', file_name)
            if full_ts_match:
                ts = full_ts_match.group(1)
                date_str = ts[:8]
                try:
                    file_dt = datetime.strptime(ts, '%Y%m%d%H%M%S')
                except: pass
            
            if not date_str:
                date_match = re.search(r'(\d{8})', file_name)
                if date_match:
                    date_str = date_match.group(1)
            
            if not date_str:
                return res

            # 2. 從內容尋找時間戳 (HH:MM:SS)
            time_pattern = re.compile(r'(\d{2}:\d{2}:\d{2})')
            
            found_times = []
            # 掃描前 500 行找開始
            for line in raw_lines[:500]:
                m = time_pattern.search(line)
                if m:
                    found_times.append(m.group(1))
                    break
            
            # 掃描後 200 行找結束
            for line in reversed(raw_lines[-200:]):
                m = time_pattern.search(line)
                if m:
                    found_times.append(m.group(1))
                    break
            
            if len(found_times) >= 2:
                res['start'] = datetime.strptime(f"{date_str} {found_times[0]}", '%Y%m%d %H:%M:%S')
                res['end'] = datetime.strptime(f"{date_str} {found_times[-1]}", '%Y%m%d %H:%M:%S')
            elif len(found_times) == 1:
                dt = datetime.strptime(f"{date_str} {found_times[0]}", '%Y%m%d %H:%M:%S')
                res['start'] = dt
                res['end'] = dt
            elif file_dt:
                # 3. 補救措施：內容沒時間但檔名有 14 位時戳，作為保底 (預設抓檔名前 15 分鐘的圖)
                res['start'] = file_dt - timedelta(minutes=15)
                res['end'] = file_dt
        except Exception as e:
            print(f"[DEBUG] 提取絕對時間失敗: {e}")
            
        return res
    
    def _parse_pass_log(self, raw_lines, file_path):
        """
        PASS分析模式（重構版）：
        - 基於 'Test is Pass' 結束行來劃分測試項目
        - 每個項目範圍：上一個結束行下一行 -> 當前結束行
        - 這樣可以確保折疊範圍正確，即使缺少 'Do @STEP'
        """
        pass_items = []
        no_command_steps = []
        
        # 結束行匹配模式：@STEPxxx@Name Test is Pass
        # 允許結尾有 ! 或其他字符，也允許大小寫變化
        end_pattern = re.compile(r'@(STEP\d+)@(.*?)Test is Pass', re.IGNORECASE)
        # 額外支援 Run 行作為開始信號，用於拆分合併的區塊
        run_pattern = re.compile(r'Run ([A-Z0-9]+-\d+):(.*?)Mode:', re.IGNORECASE)
        
        start_idx = 0
        current_phase = "Unknown Phase"
        
        # 尋找所有測試項目的結束行
        for idx, line in enumerate(raw_lines):
            # 偵測 Phase
            p_match = self.phase_pattern.search(line)
            if p_match:
                raw_phase_title = p_match.group(1).strip()
                current_phase = self._get_enriched_phase_name(raw_lines, idx, raw_phase_title)

            match = end_pattern.search(line)
            if match:
                # 找到一個測試項目的結束
                end_step_number = match.group(1)
                end_step_name = match.group(2).strip()
                
                # 定義區塊範圍
                block_start = start_idx
                block_end = idx
                block_lines = raw_lines[block_start : block_end + 1]
                
                # 檢查區塊內是否有多個 Run 行（意味著多個步驟被合併）
                run_indices = []
                for i, l in enumerate(block_lines):
                    if run_pattern.search(l):
                        run_indices.append(i)
                        
                if len(run_indices) > 1:
                    # 進行拆分處理
                    self._process_split_blocks(
                        block_lines, block_start, run_indices, 
                        end_step_number, end_step_name,
                        pass_items, no_command_steps, 
                        current_phase
                    )
                else:
                    # 只有一個或沒有 Run 行，作為單一項目處理
                    step_info = self._analyze_block_content(block_lines, end_step_number, end_step_name)
                    step_info['start_idx'] = block_start
                    step_info['end_idx'] = block_end
                    step_info['raw_idx'] = block_start
                    step_info['full_log'] = block_lines
                    step_info['phase'] = current_phase
                    
                    for v in step_info.get('validations', []):
                        if 'line_idx' in v:
                            v['line_idx'] += block_start
                    
                    self._finalize_pass_step(step_info, pass_items, no_command_steps)
                
                # 更新下一個項目的起始位置
                start_idx = idx + 1
        
        # 處理剩餘部分
        if start_idx < len(raw_lines):
            leftover_lines = raw_lines[start_idx:]
            if any(self.step_pattern.search(l) for l in leftover_lines):
                 pass 

        # 處理"未找到指令"的集合
        self._consolidate_no_command_steps(pass_items, no_command_steps)
        
        return {
            'pass_items': pass_items,
            'fail_items': [],
            'raw_lines': raw_lines,
            'last_fail': None,
            'fail_line_idx': None,
            'log_type': 'PASS'
        }
    
    def _process_split_blocks(self, block_lines, global_start_idx, run_indices, end_step_number, end_step_name, pass_items, no_command_steps, current_phase):
        """拆分包含多個步驟的區塊"""
        run_pattern = re.compile(r'Run ([A-Z0-9]+-\d+):(.*?)Mode:', re.IGNORECASE)
        
        for i in range(len(run_indices)):
            current_run_idx = run_indices[i]
            # 下一個 Run 的索引，或是區塊結尾
            next_run_idx = run_indices[i+1] if i + 1 < len(run_indices) else len(block_lines)
            
            # 提取子區塊
            sub_lines = block_lines[current_run_idx : next_run_idx]
            
            # 確定這是不是最後一個子項目（對應結束行）
            is_last = (i == len(run_indices) - 1)
            
            # 提取 Step Name
            first_line = block_lines[current_run_idx]
            match = run_pattern.search(first_line)
            step_name = match.group(2).strip() if match else "Unknown Step"
            
            # 如果是最後一個項目，使用結束行的資訊（通常更準確）
            if is_last:
                step_name = end_step_name
                step_number = end_step_number
            else:
                block_step_num = '' 
                for l in sub_lines:
                    sm = self.step_pattern.search(l)
                    if sm:
                        sn = sm.group(1).strip()
                        if '@' in sn[1:]: block_step_num = sn.split('@')[1]
                        break
                step_number = block_step_num
            
            # 構建 Step Info
            step_info = self._analyze_block_content(sub_lines, step_number, step_name)
            step_info['phase'] = current_phase
            
            # 計算全局索引
            abs_start = global_start_idx + current_run_idx
            abs_end = global_start_idx + next_run_idx - 1
            
            step_info['start_idx'] = abs_start
            step_info['end_idx'] = abs_end
            step_info['raw_idx'] = abs_start
            step_info['full_log'] = sub_lines
            
            for v in step_info.get('validations', []):
                if 'line_idx' in v:
                    v['line_idx'] += abs_start
            
            self._finalize_pass_step(step_info, pass_items, no_command_steps)
    
    def _analyze_block_content(self, lines, step_number, step_name_raw):
        """解析一個測試區塊的內容"""
        command = ''
        response = ''
        
        # 尋找 Command 和 Response
        for line in lines:
            line_str = str(line).strip()
            if not command:
                cmd_match = self.cmd_pattern.search(line_str)
                if cmd_match:
                     command = cmd_match.group(1).strip()
            if not response:
                resp_match = self.resp_pattern.search(line_str)
                if resp_match:
                    response = resp_match.group(1).strip()
        
        # 提取比對項目
        validations = self._extract_validations(lines)
        
        return {
            'step_name': step_name_raw,
            'test_id': '',
            'command': command,
            'response': response,
            'validations': validations,
            'result': 'PASS',
            'retry': 0,
            'error': '',
            'has_retry_but_pass': False,
            'step_number': step_number
        }

    def _extract_validations(self, lines):
        """
        從 Log 行中提取比對項目資訊 (恢復為穩定模式)
        規則：必須包含 '=' 以及括號內容，如 OOO = XXX (XXX)
        """
        validations = []
        # 嚴格匹配: 名稱 = 數值 (判定標準)
        # 支持 (10,50) 或 (100,)
        pattern = re.compile(r'([\w\s_-]+)\s*=\s*([^ \(\)]+)\s*\(([^)]+)\)')
        
        noise_keywords = ['icmp_seq', 'ttl=', 'time=', 'bytes from', 'reply from', 'sfis is', 'script version', 'version is']
        exclude_names = ('ISN', 'DATE', 'VERSION', 'TIME', 'SCRIPT', 'OFFSET')
        
        for idx, line in enumerate(lines):
            line_str = str(line).strip()
            if not line_str or any(kw in line_str.lower() for kw in noise_keywords):
                continue
            
            # 排除時間戳或純日期行 (如 26 13 = 08:27)
            if re.search(r'^\d{2}[:\s]\d{2}([:\s]\d{2})?\s*[=:]', line_str):
                continue

            match = pattern.search(line_str)
            if match:
                v_name = match.group(1).strip()
                v_limits = match.group(3).strip()
                
                # 規則：名稱含字母，括號內必須包含逗號 (代表範圍或限制，如 (10,50) 或 (100,))
                # 這樣可以過濾掉單一數值的括號，如 Current message level: 0x... (51)
                has_letters = re.search(r'[A-Za-z_]', v_name)
                has_comma = ',' in v_limits
                is_date = any(m in v_limits for m in ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
                
                if has_letters and has_comma and v_name.upper() not in exclude_names and not is_date:
                    v_val = match.group(2).strip()
                    if 'The validation:' in line_str:
                        v_content = line_str.split('The validation:', 1)[1].strip()
                    else:
                        v_content = match.group(0).strip()
                    
                    v_status = 'PASS'
                    if 'is FAIL' in line_str or 'status:FAIL' in line_str.lower() or 'FAIL' in line_str.upper():
                        v_status = 'FAIL'
                    else:
                        try:
                            # 判定數值範圍
                            parts = v_limits.split(',')
                            l_lim = float(parts[0].strip())
                            r_lim = float(parts[-1].strip()) if parts[-1].strip() else l_lim
                            v_num = float(v_val)
                            if not (l_lim <= v_num <= r_lim): v_status = 'FAIL'
                        except: pass
                    
                    validations.append({'content': v_content, 'status': v_status, 'line_idx': idx})
                        
        return validations
        
        return {
            'step_name': step_name_raw,
            'test_id': '',
            'command': command,
            'response': response,
            'validations': validations, # 新增欄位
            'result': 'PASS',
            'retry': 0,
            'error': '',
            'has_retry_but_pass': False,
            'step_number': step_number
        }
    
    def _is_step_end_line(self, line, step_number):
        """檢查是否為測項結束行（@STEPxxx@ Test is Pass !）"""
        if not step_number:
            return False
        
        # 檢查是否包含 @STEPxxx@ Test is Pass ! 格式
        end_pattern = re.compile(rf'@{step_number}@.*Test is Pass !', re.IGNORECASE)
        is_end = end_pattern.search(line) is not None
        
        if is_end:
            print(f"[DEBUG] 找到結束行 STEP{step_number}: {line[:80]}")
        
        return is_end
    
    def _is_step_end_line_relaxed(self, line, step_number):
        """更寬鬆的結束行檢查"""
        if not step_number:
            return False
            
        pattern = re.compile(rf'@{step_number}@.*Pass', re.IGNORECASE)
        return pattern.search(line) is not None
    
    def _finalize_pass_step(self, step, pass_items, no_command_steps):
        """完成PASS步驟的處理"""
        # 為展開內容加上數字編碼
        numbered_content = []
        for i, line in enumerate(step['full_log'], 1):
            numbered_content.append(f"{i:4d}. {line}")
        
        # 設定完整回應為整個測項內容
        step['full_response'] = '\n'.join(numbered_content)
        
        # 設定預設值
        if not step.get('command'):
            step['command'] = f"@{step.get('step_name','')}"
        if not step.get('response'):
            step['response'] = '無收到反饋值'
        
        # 基於有效的 Retry: N 判斷
        retry_count = self._get_effective_retry_count(step['full_log'])
        
        if retry_count > 1:
            step['has_retry_but_pass'] = True
            step['retry'] = retry_count
            step['result'] = f"PASS (Retry {retry_count})"
        else:
            step['has_retry_but_pass'] = False
            step['retry'] = 0
            step['result'] = 'PASS'
        
        # 檢查是否為"未找到指令"
        if step['command'] == '未找到指令':
            no_command_steps.append(step)
        else:
            pass_items.append(step)
    
    def _finalize_step(self, step, pass_items, fail_items, no_command_steps):
        """完成步驟的處理，根據結果分類到PASS或FAIL"""
        numbered_content = []
        for i, line in enumerate(step['full_log'], 1):
            numbered_content.append(f"{i:4d}. {line}")
        
        step['full_response'] = '\n'.join(numbered_content)
        
        # 確保提取了比對項目 (如果是在 _parse_fail_log 中建立的)
        if 'validations' not in step:
            step['validations'] = self._extract_validations(step['full_log'])
            # 調整為全域索引
            start_off = step.get('start_idx', 0)
            for v in step['validations']:
                if 'line_idx' in v:
                    v['line_idx'] += start_off
        
        if not step.get('command'):
            is_pass_like = step.get('is_pass') is True or step.get('result') == 'PASS'
            step['command'] = f"@{step.get('step_name','')}" if is_pass_like else '未找到指令'
        if not step.get('response'):
            step['response'] = '無收到反饋值'
        
        retry_count = self._get_effective_retry_count(step['full_log'])
        
        if retry_count > 1:
            step['has_retry_but_pass'] = True
            step['retry'] = retry_count
            if step['result'] == 'PASS':
                step['result'] = f"PASS (Retry {retry_count})"
        else:
            step['has_retry_but_pass'] = False
            step['retry'] = 0
        
        if step.get('is_pass', True) and step['result'] != 'FAIL':
            if step['command'] == '未找到指令':
                no_command_steps.append(step)
            else:
                pass_items.append(step)
        else:
            step['is_main_fail'] = True
            fail_items.append(step)

    def _parse_fail_log(self, raw_lines, file_path):
        """FAIL分析邏輯"""
        pass_items = []
        fail_items = []
        no_command_steps = []
        current_step = None
        current_phase = "Unknown Phase"
        
        for idx, line in enumerate(raw_lines):
            # 偵測 Phase
            p_match = self.phase_pattern.search(line)
            if p_match:
                raw_phase_title = p_match.group(1).strip()
                current_phase = self._get_enriched_phase_name(raw_lines, idx, raw_phase_title)

            # 找到 Do @STEPxxx@ 或 Run 行 - 測項開始
            step_match = self.step_pattern.search(line)
            run_match = self.test_id_pattern.search(line) # Run XX-XX:
            
            # 如果是 Run 行且不是已存在的 Do 行，則作為新測項開頭
            is_new_step = step_match is not None
            if not is_new_step and run_match:
                 # 檢查是否為獨立的 Run 行 (後面通常跟著名稱)
                 if ':' in line:
                     is_new_step = True

            if is_new_step:
                if current_step:
                    current_step['end_idx'] = idx - 1
                    self._finalize_step(current_step, pass_items, fail_items, no_command_steps)
                
                step_name_clean = ""
                step_number = ""
                
                if step_match:
                    step_name_clean = step_match.group(1).strip()
                    if step_name_clean.startswith('@STEP') and '@' in step_name_clean[1:]:
                        step_parts = step_name_clean.split('@')
                        if len(step_parts) >= 2:
                            step_number = step_parts[1]
                        step_name_clean = step_name_clean.split('@', 2)[-1]
                elif run_match:
                    # Run XXX: Name
                    colon_parts = line.split(':', 1)
                    if len(colon_parts) > 1:
                        step_name_clean = colon_parts[1].strip()
                        # 過濾掉結尾的 Mode: XXX
                        if 'Mode:' in step_name_clean:
                            step_name_clean = step_name_clean.split('Mode:', 1)[0].strip()
                    else:
                        step_name_clean = f"RUN {run_match.group(1)}"
                
                current_step = {
                    'step_name': step_name_clean,
                    'test_id': run_match.group(1) if run_match else '',
                    'command': '',
                    'response': '',
                    'result': 'UNKNOWN',
                    'retry': 0,
                    'error': '',
                    'raw_idx': idx,
                    'full_log': [line],
                    'has_retry_but_pass': False,
                    'start_idx': idx,
                    'end_idx': None,
                    'step_number': step_number,
                    'is_pass': None,
                    'phase': current_phase
                }
                continue
            
            if current_step:
                current_step['full_log'].append(line)
                
                if self._is_step_end_line(line, current_step.get('step_number', '')):
                    current_step['end_idx'] = idx
                    if current_step.get('result') != 'FAIL':
                        current_step['is_pass'] = True
                        current_step['result'] = 'PASS'
                    self._finalize_step(current_step, pass_items, fail_items, no_command_steps)
                    current_step = None
                    continue
                
                if any(k.upper() in line.upper() for k in self.fail_keywords):
                    if current_step.get('result') != 'FAIL':
                        current_step['is_pass'] = False
                        current_step['result'] = 'FAIL'
                        current_step['error'] = line.strip()
                
                cmd_match = self.cmd_pattern.search(line)
                if cmd_match and not current_step['command']:
                    current_step['command'] = cmd_match.group(1).strip()
                
                if not current_step['response']:
                    resp_match = self.resp_pattern.search(line)
                    if resp_match:
                        current_step['response'] = resp_match.group(1).strip()
        
        if current_step:
            current_step['end_idx'] = len(raw_lines) - 1
            if current_step['is_pass'] is None:
                current_step['is_pass'] = False
                current_step['result'] = 'FAIL'
                if not current_step.get('error'):
                    current_step['error'] = "Step not completed (Log abruptly ended)"
            self._finalize_step(current_step, pass_items, fail_items, no_command_steps)
        
        self._consolidate_no_command_steps(pass_items, no_command_steps)
        
        last_fail = None
        
        def filter_items(items, keyword, case_sensitive=False):
            matches = []
            for item in items:
                err_str = str(item.get('error', ''))
                full_str = str(item.get('full_log', ''))
                if case_sensitive:
                    if keyword in err_str or keyword in full_str:
                        matches.append(item)
                else:
                    if keyword.lower() in err_str.lower() or keyword.lower() in full_str.lower():
                        matches.append(item)
            return matches

        matches = filter_items(fail_items, "doesn't match", case_sensitive=False)
        if matches:
            last_fail = matches[-1]
        
        if not last_fail:
            matches = filter_items(fail_items, "is Fail", case_sensitive=False)
            if matches:
                last_fail = matches[-1]

        if not last_fail:
            matches = filter_items(fail_items, "FAIL", case_sensitive=False)
            if matches:
                last_fail = matches[-1]

        if not last_fail:
            matches = filter_items(fail_items, "ERROR", case_sensitive=False)
            if matches:
                last_fail = matches[-1]
                
        if not last_fail and fail_items:
            last_fail = fail_items[-1]

        if last_fail:
            target_keywords = ["doesn't match", "is Fail", "FAIL", "ERROR"]
            for keyword in target_keywords:
                matching_lines = [
                    line for line in last_fail.get('full_log', []) 
                    if keyword.lower() in str(line).lower()
                ]
                if matching_lines:
                    last_fail['error'] = matching_lines[-1].strip()
                    break
            
        fail_line_idx = last_fail.get('raw_idx', 0) if last_fail else None
        
        return {
            'pass_items': pass_items,
            'fail_items': fail_items,
            'raw_lines': raw_lines,
            'last_fail': last_fail,
            'fail_line_idx': fail_line_idx,
            'log_type': 'FAIL'
        }
    
    def _find_fail_blocks_from_bottom(self, raw_lines):
        """從檔案尾部往上找FAIL區塊"""
        fail_blocks = []
        visited_lines = set()
        for idx in range(len(raw_lines) - 1, -1, -1):
            line = raw_lines[idx]
            if (any(keyword in line.upper() for keyword in ["FAIL", "FAILED", "ERROR"]) 
                and idx not in visited_lines):
                block_start = self._find_block_start(raw_lines, idx)
                block_end = self._find_block_end(raw_lines, idx)
                if block_start is not None and block_end is not None:
                    block_lines = raw_lines[block_start:block_end + 1]
                    fail_block = {
                        'block_lines': block_lines,
                        'start_idx': block_start,
                        'end_idx': block_end,
                        'fail_idx': idx,
                        'full_log': block_lines
                    }
                    fail_blocks.append(fail_block)
                    visited_lines.update(range(block_start, block_end + 1))
        return fail_blocks
    
    def _find_block_start(self, raw_lines, fail_idx):
        for i in range(fail_idx, max(0, fail_idx - 200), -1):
            if self.step_pattern.search(raw_lines[i]):
                return i
        for i in range(fail_idx, max(0, fail_idx - 100), -1):
            if self.cmd_pattern.search(raw_lines[i]):
                return i
        return max(0, fail_idx - 50)
    
    def _find_block_end(self, raw_lines, fail_idx):
        for i in range(fail_idx, min(len(raw_lines), fail_idx + 200)):
            if self.step_pattern.search(raw_lines[i]):
                return i - 1
            if i == len(raw_lines) - 1:
                return i
        return min(len(raw_lines) - 1, fail_idx + 200)
    
    def _find_fail_blocks(self, raw_lines):
        blocks = []
        visited_lines = set()
        for idx in range(len(raw_lines) - 1, -1, -1):
            line = raw_lines[idx]
            if any(keyword in line.upper() for keyword in self.fail_keywords) and idx not in visited_lines:
                block_info = self._extract_fail_block(raw_lines, idx)
                if block_info:
                    blocks.append(block_info)
                    start_idx = block_info.get('start_idx', idx)
                    end_idx = block_info.get('end_idx', idx)
                    visited_lines.update(range(start_idx, end_idx + 1))
        return blocks
    
    def _extract_fail_block(self, raw_lines, fail_idx):
        start_idx = fail_idx
        end_idx = fail_idx
        for i in range(fail_idx, max(0, fail_idx - 50), -1):
            if self.cmd_pattern.search(raw_lines[i]):
                start_idx = i
                break
        for i in range(fail_idx, min(len(raw_lines), fail_idx + 20)):
            if i > fail_idx and (self.root_pattern.search(raw_lines[i]) or self.cmd_pattern.search(raw_lines[i])):
                end_idx = i
                break
            end_idx = i
        block_lines = raw_lines[start_idx:end_idx + 1]
        return {
            'block_lines': block_lines,
            'start_idx': start_idx,
            'end_idx': end_idx,
            'fail_idx': fail_idx
        }
    
    def _extract_fail_step_info(self, fail_block, raw_lines):
        block_lines = fail_block['block_lines']
        fail_idx = fail_block['fail_idx']
        step_name = self._find_step_name_in_block(block_lines, raw_lines, fail_block['start_idx'])
        command = ''
        for line in block_lines:
            cmd_match = self.cmd_pattern.search(line)
            if cmd_match:
                command = cmd_match.group(1).strip()
                break
        response = ''
        for line in block_lines:
            resp_match = self.resp_pattern.search(line)
            if resp_match:
                response = resp_match.group(1).strip()
                break
        retry_count = self._get_effective_retry_count(block_lines)
        error_reason = self._find_error_reason(block_lines)
        full_log = block_lines
        if not command:
            command = '未找到指令'
        if not response:
            response = '無收到反饋值'
        return {
            'step_name': step_name,
            'test_id': '',
            'command': command,
            'response': response,
            'result': 'FAIL',
            'retry': retry_count,
            'error': error_reason,
            'full_response': '\n'.join(full_log),
            'full_log': full_log,
            'raw_idx': fail_block['start_idx'],
            'fail_idx': fail_idx,
            'start_idx': fail_block['start_idx'],
            'end_idx': fail_block['end_idx']
        }
    
    def _find_nearest_step_name(self, raw_lines, start_idx):
        for i in range(start_idx, max(0, start_idx - 100), -1):
            step_match = self.step_pattern.search(raw_lines[i])
            if step_match:
                return step_match.group(1).strip()
        return "Unknown Step"
    
    def _find_error_reason(self, block_lines):
        for line in block_lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['failed', 'error', 'nack', 'timeout', 'fail']):
                if ':' in line and ('is fail' in line_lower or 'is failed' in line_lower):
                    colon_pos = line.find(':')
                    if colon_pos != -1:
                        after_colon = line[colon_pos + 1:].strip()
                        fail_pos = -1
                        if 'is fail !' in after_colon.lower():
                            fail_pos = after_colon.lower().find('is fail !')
                            end_pos = fail_pos + 8
                        elif 'is failed !' in after_colon.lower():
                            fail_pos = after_colon.lower().find('is failed !')
                            end_pos = fail_pos + 10
                        elif 'is fail' in after_colon.lower():
                            fail_pos = after_colon.lower().find('is fail')
                            end_pos = fail_pos + 7
                        elif 'is failed' in after_colon.lower():
                            fail_pos = after_colon.lower().find('is failed')
                            end_pos = fail_pos + 9
                        if fail_pos != -1:
                            error_msg = after_colon[:end_pos].strip()
                            return error_msg
                return line.strip()
        return "Unknown Error"
    
    def _find_step_name_in_block(self, block_lines, raw_lines, start_idx):
        for line in block_lines:
            step_match = self.step_pattern.search(line)
            if step_match:
                step_name_clean = step_match.group(1).strip()
                if step_name_clean.startswith('@STEP') and '@' in step_name_clean[1:]:
                    step_name_clean = step_name_clean.split('@', 2)[-1]
                return step_name_clean
        for i in range(start_idx, max(0, start_idx - 50), -1):
            step_match = self.step_pattern.search(raw_lines[i])
            if step_match:
                step_name_clean = step_match.group(1).strip()
                if step_name_clean.startswith('@STEP') and '@' in step_name_clean[1:]:
                    step_name_clean = step_name_clean.split('@', 2)[-1]
                return step_name_clean
        return "Unknown Step"
    
    def _get_enriched_phase_name(self, raw_lines, phase_idx, phase_title):
        for i in range(phase_idx + 1, min(phase_idx + 11, len(raw_lines))):
            line = raw_lines[i]
            do_match = re.search(r'Do @STEP\d+@([^@\n]+)', line)
            run_match = re.search(r'Run [A-Z0-9\-]+:([^@\n\t]+)', line)
            step_name = None
            if do_match:
                if 'Test is Pass' not in line:
                    step_name = do_match.group(1).strip()
            elif run_match:
                step_name = run_match.group(1).strip()
            if step_name:
                return f"{phase_title} ={step_name}"
        return phase_title

    def _generate_ui_annotations(self, raw_lines, is_pass_log):
        """
        核心視覺引擎：產生統一的 UI 標註資訊 (同步 GUI & Excel)
        包含：Phase 分隔線、Step 背景交替 (Zebra Stripes)、錯誤區塊高亮
        """
        annotations = []
        
        # --- 狀態追蹤器 ---
        current_bg = 'white'
        zebra_toggle = False # True: Blue, False: Purple zebra stripes
        
        # 顏色定義 (簡化版：移除斑馬紋)
        COLOR_ERROR_BG = '#FFE1E1'  # 淺粉紅 (錯誤背景)
        COLOR_GREEN = '#28a745'
        COLOR_BLUE = '#007bff'
        COLOR_PURPLE = '#6f42c1'
        COLOR_RED = '#ff0000'
        
        # === 預先偵測 doesn't match 錯誤區塊 (整段紅色) ===
        dm_error_idx = -1
        dm_pattern = re.compile(r"doesn't match", re.IGNORECASE)
        
        for idx in range(len(raw_lines)-1, -1, -1):
            if dm_pattern.search(raw_lines[idx]):
                dm_error_idx = idx
                break
        
        # 計算 doesn't match 錯誤區塊範圍
        dm_block_start = -1
        dm_block_end = -1
        if dm_error_idx != -1:
            # 往上找指令起點
            for i in range(dm_error_idx, max(-1, dm_error_idx - 50), -1):
                if '>' in raw_lines[i] or 'Do @STEP' in raw_lines[i]:
                    dm_block_start = i
                    break
            if dm_block_start == -1:
                dm_block_start = dm_error_idx
            
            # 往下延伸到測試結束或下一個測項
            dm_block_end = dm_error_idx + 2
            for i in range(dm_error_idx + 1, min(len(raw_lines), dm_error_idx + 10)):
                if 'Test Completed' in raw_lines[i] or ('Do @STEP' in raw_lines[i] and i > dm_error_idx):
                    dm_block_end = i - 1
                    break
            dm_block_end = min(dm_block_end, len(raw_lines) - 1)

        last_separator_idx = -30
        
        for idx, line in enumerate(raw_lines):
            annotation = {
                'line_idx': idx,
                'line_content': line,
                'color': 'black',
                'background': 'white',  # 預設白色背景，移除斑馬紋
                'is_clickable': False,
                'hover_color': '#FFFF99',
                'show_separator': False,
                'separator_title': None,
                'is_bold': False
            }
            
            # === 1. doesn't match 整段紅色背景 ===
            if dm_block_start != -1 and dm_block_start <= idx <= dm_block_end:
                annotation['background'] = COLOR_ERROR_BG
                annotation['color'] = COLOR_RED
                annotation['is_bold'] = True
            
            # === 2. PHASE 章節分隔線 ===
            phase_match = self.phase_pattern.search(line)
            if phase_match:
                if (idx - last_separator_idx > 10):
                    title = self._get_enriched_phase_name(raw_lines, idx, phase_match.group(1).strip())
                    annotation['show_separator'] = True
                    annotation['separator_title'] = title.upper()
                    last_separator_idx = idx

            # === 3. 語法著色 (文字顏色) ===
            upper_line = line.upper()
            
            # 指令/回應
            if self.cmd_pattern.search(line):
                if dm_block_start == -1 or not (dm_block_start <= idx <= dm_block_end):
                    annotation['color'] = COLOR_BLUE
                annotation['is_bold'] = True
            elif self.resp_pattern.search(line):
                if dm_block_start == -1 or not (dm_block_start <= idx <= dm_block_end):
                    annotation['color'] = COLOR_PURPLE
            
            # 關鍵字與測項狀態
            if 'Do @STEP' in line:
                if dm_block_start == -1 or not (dm_block_start <= idx <= dm_block_end):
                    annotation['color'] = COLOR_BLUE if not is_pass_log else COLOR_GREEN
                annotation['is_bold'] = True
                annotation['is_clickable'] = True
            elif 'PASS' in upper_line:
                annotation['color'] = COLOR_GREEN
                annotation['is_bold'] = True
            
            # === 4. 數值判定 (Criteria) 優先於關鍵字判定 ===
            criteria_match = re.search(r'=\s*([^ \(\)]+)\s*\(\s*([^,]+)\s*,\s*([^ \)]+)\s*\)', line)
            is_validation_line = False
            if criteria_match:
                is_validation_line = True
                try:
                    v = float(criteria_match.group(1)); l = float(criteria_match.group(2)); r = float(criteria_match.group(3))
                    if l <= v <= r:
                        annotation['color'] = COLOR_GREEN
                        annotation['background'] = 'white' # 確保 Pass 不會因為名稱含 error 而帶紅底
                    else:
                        annotation['color'] = COLOR_RED
                        annotation['is_bold'] = True
                        if dm_block_start == -1 or not (dm_block_start <= idx <= dm_block_end):
                            annotation['background'] = COLOR_ERROR_BG
                except: pass

            # === 5. 單行錯誤高亮（FAIL/ERROR，但不在 doesn't match 區塊內且非數值判定行）===
            if not is_validation_line:
                if dm_block_start == -1 or not (dm_block_start <= idx <= dm_block_end):
                    if any(k.upper() in upper_line for k in ['FAIL', 'ERROR', 'NACK', 'TIMEOUT']):
                        annotation['color'] = COLOR_RED
                        annotation['is_bold'] = True
                        annotation['background'] = COLOR_ERROR_BG

            annotations.append(annotation)
        
        return annotations

    def parse_log_folder(self, folder_path):
        pass_items = []
        fail_items = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.log'):
                    file_path = os.path.join(root, file)
                    try:
                        result = self.parse_log_file(file_path)
                        file_name = os.path.basename(file_path)
                        for it in result['pass_items']:
                            it['file_name'] = file_name
                        for it in result['fail_items']:
                            it['file_name'] = file_name
                        pass_items.extend(result['pass_items'])
                        fail_items.extend(result['fail_items'])
                    except Exception as e:
                        print(f"解析檔案 {file_path} 失敗: {e}")
        return {
            'pass_items': pass_items,
            'fail_items': fail_items,
            'raw_lines': [],
            'last_fail': fail_items[-1] if fail_items else None,
            'fail_line_idx': None,
            'log_type': 'MULTI'
        }

    def _consolidate_no_command_steps(self, pass_items, no_command_steps):
        if not no_command_steps:
            return
        no_command_with_order = []
        for step in no_command_steps:
            no_command_with_order.append((step['raw_idx'], step))
        no_command_with_order.sort(key=lambda x: x[0])
        all_steps = []
        for step in pass_items:
            all_steps.append((step['raw_idx'], step, 'normal'))
        for raw_idx, step in no_command_with_order:
            all_steps.append((raw_idx, step, 'no_command'))
        all_steps.sort(key=lambda x: x[0])
        new_pass_items = []
        current_no_command_group = []
        for raw_idx, step, step_type in all_steps:
            if step_type == 'no_command':
                current_no_command_group.append(step)
            else:
                if current_no_command_group:
                    consolidated_step = self._create_consolidated_step(current_no_command_group)
                    new_pass_items.append(consolidated_step)
                    current_no_command_group = []
                new_pass_items.append(step)
        if current_no_command_group:
            consolidated_step = self._create_consolidated_step(current_no_command_group)
            new_pass_items.append(consolidated_step)
        pass_items.clear()
        pass_items.extend(new_pass_items)
    
    def _create_consolidated_step(self, no_command_group):
        consolidated_content = []
        for i, step in enumerate(no_command_group, 1):
            step_header = f"步驟 {i}: {step['step_name']}"
            consolidated_content.append(step_header)
            for j, line in enumerate(step['full_log'], 1):
                consolidated_content.append(f"  {j:4d}. {line}")
            consolidated_content.append("")
        return {
            'step_name': f"未找到指令 x{len(no_command_group)}",
            'test_id': '',
            'command': '未找到指令',
            'response': '無收到反饋值',
            'result': 'PASS',
            'retry': 0,
            'error': '',
            'full_response': '\n'.join(consolidated_content),
            'full_log': consolidated_content,
            'raw_idx': no_command_group[0]['raw_idx'],
            'start_idx': no_command_group[0]['start_idx'],
            'end_idx': no_command_group[-1]['end_idx'],
            'step_number': '',
            'has_retry_but_pass': False,
            'is_consolidated': True
        }
    
    def _get_effective_retry_count(self, lines):
        commands = []
        for line in lines:
            cmd_match = self.cmd_pattern.search(line)
            if cmd_match:
                command = cmd_match.group(1).strip()
                commands.append(command)
        if not commands:
            return 0
        main_command = commands[0]
        command_count = commands.count(main_command)
        return command_count if command_count > 1 else 0