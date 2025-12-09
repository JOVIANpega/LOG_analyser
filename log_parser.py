# log_parser.py
# 用途：基於檔名判斷PASS/FAIL，使用不同分析邏輯的測試log解析器
import re
import os
from pathlib import Path

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
        self.fail_keywords = ['FAIL', 'FAILED', 'ERROR', 'failed', 'error', 'NACK', 'timeout']

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
        
        if is_pass_log:
            result = self._parse_pass_log(raw_lines, file_path)
        else:
            result = self._parse_fail_log(raw_lines, file_path)
        
        # 添加UI標註資訊
        result['ui_annotations'] = ui_annotations
        return result
    
    def _empty_result(self):
        """回傳空結果"""
        return {
            'pass_items': [],
            'fail_items': [],
            'raw_lines': [],
            'last_fail': None,
            'fail_line_idx': None,
            'log_type': 'UNKNOWN'
        }
    
    def _parse_pass_log(self, raw_lines, file_path):
        """
        PASS分析模式：
        - 從頭到尾逐行讀取
        - Do @STEPxxx@ 行視為測項開始
        - @STEPxxx@ Test is Pass ! 行視為測項結束
        - 結果一律標記 "PASS"
        - 檢查是否有 "Retry: N" 關鍵字，若有且N>1 不需要紅字註記了，用黑色文字
        - 將"未找到指令"的項目集合成一大塊，顯示為"未找到指令xN"
        """
        pass_items = []
        current_step = None
        no_command_steps = []  # 收集"未找到指令"的步驟
        
        for idx, line in enumerate(raw_lines):
            # 找到 Do @STEPxxx@ 行 - 測項開始
            step_match = self.step_pattern.search(line)
            if step_match:
                # 完成前一個測項
                if current_step:
                    current_step['end_idx'] = idx - 1
                    self._finalize_pass_step(current_step, pass_items, no_command_steps)
                
                # 開始新測項
                step_name_clean = step_match.group(1).strip()
                # 提取STEP號碼
                step_number = ''
                if step_name_clean.startswith('@STEP') and '@' in step_name_clean[1:]:
                    # 提取STEP號碼，例如 @STEP048@CHECK SD 提取 048
                    step_parts = step_name_clean.split('@')
                    if len(step_parts) >= 2:
                        step_number = step_parts[1]
                    step_name_clean = step_name_clean.split('@', 2)[-1]
                
                current_step = {
                    'step_name': step_name_clean,
                    'test_id': '',
                    'command': '',
                    'response': '',
                    'result': 'PASS',
                    'retry': 0,
                    'error': '',
                    'raw_idx': idx,
                    'full_log': [line],  # 完整測試過程
                    'has_retry_but_pass': False,
                    'start_idx': idx,
                    'end_idx': None,
                    'step_number': step_number
                }
                continue
            
            if current_step:
                current_step['full_log'].append(line)
                
                # 檢查是否為測項結束行（@STEPxxx@ Test is Pass !）
                if self._is_step_end_line(line, current_step.get('step_number', '')):
                    current_step['end_idx'] = idx
                    self._finalize_pass_step(current_step, pass_items, no_command_steps)
                    current_step = None
                    continue
                
                # 檢查是否為指令行
                cmd_match = self.cmd_pattern.search(line)
                if cmd_match:
                    # 第一條指令
                    if not current_step['command']:
                        current_step['command'] = cmd_match.group(1).strip()
                
                # 第一個回應 - 測項開始後第一個 < 行
                if not current_step['response']:
                    resp_match = self.resp_pattern.search(line)
                    if resp_match:
                        current_step['response'] = resp_match.group(1).strip()
        
        # 處理最後一個測項
        if current_step:
            current_step['end_idx'] = len(raw_lines) - 1
            self._finalize_pass_step(current_step, pass_items, no_command_steps)
        
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
    
    def _is_step_end_line(self, line, step_number):
        """檢查是否為測項結束行（@STEPxxx@ Test is Pass !）"""
        if not step_number:
            return False
        
        # 檢查是否包含 @STEPxxx@ Test is Pass ! 格式
        # 支援多種可能的格式：
        # @STEP048@CHECK SD  Inserted Test is Pass !
        # @STEP048@ Test is Pass !
        end_pattern = re.compile(rf'@{step_number}@.*Test is Pass !', re.IGNORECASE)
        return end_pattern.search(line) is not None
    
    def _finalize_pass_step(self, step, pass_items, no_command_steps):
        """完成PASS步驟的處理"""
        # 為展開內容加上數字編碼
        numbered_content = []
        for i, line in enumerate(step['full_log'], 1):
            numbered_content.append(f"{i:4d}. {line}")
        
        # 設定完整回應為整個測項內容（供+按鈕展開使用）
        step['full_response'] = '\n'.join(numbered_content)
        
        # 設定預設值
        if not step.get('command'):
            # 若沒有找到指令，預設顯示為 @步驟名稱（例如 @CheckRoute）
            step['command'] = f"@{step.get('step_name','')}"
        if not step.get('response'):
            step['response'] = '無收到反饋值'
        
        # 基於有效的 Retry: N 判斷（忽略出現在 Run 行上的 Retry 參數）
        retry_count = self._get_effective_retry_count(step['full_log'])
        
        # 只有當真正有"Retry: N"關鍵字且N>1時才標記為RETRY，但用黑色文字
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
        # 為展開內容加上數字編碼
        numbered_content = []
        for i, line in enumerate(step['full_log'], 1):
            numbered_content.append(f"{i:4d}. {line}")
        
        # 設定完整回應為整個測項內容
        step['full_response'] = '\n'.join(numbered_content)
        
        # 設定預設值
        if not step.get('command'):
            # 對 PASS 步驟：若沒有找到指令，顯示為 @步驟名稱；FAIL 步驟仍顯示未找到指令
            is_pass_like = step.get('is_pass') is True or step.get('result') == 'PASS'
            step['command'] = f"@{step.get('step_name','')}" if is_pass_like else '未找到指令'
        if not step.get('response'):
            step['response'] = '無收到反饋值'
        
        # 檢查RETRY（忽略 Run 行上的 Retry 欄位）
        retry_count = self._get_effective_retry_count(step['full_log'])
        
        if retry_count > 1:
            step['has_retry_but_pass'] = True
            step['retry'] = retry_count
            if step['result'] == 'PASS':
                step['result'] = f"PASS (Retry {retry_count})"
        else:
            step['has_retry_but_pass'] = False
            step['retry'] = 0
        
        # 根據結果分類
        if step.get('is_pass', True) and step['result'] != 'FAIL':
            # PASS項目
            if step['command'] == '未找到指令':
                no_command_steps.append(step)
            else:
                pass_items.append(step)
        else:
            # FAIL項目
            step['is_main_fail'] = True
            fail_items.append(step)

    def _annotate_attempts(self, lines):
        """在完整內容中為每次指令嘗試加入 Attempt 1/2/3 標註（已棄用）"""
        # 這個方法已經不再使用，真正的RETRY判斷基於"Retry: N"關鍵字
        return '\n'.join(lines)

    def _parse_fail_log(self, raw_lines, file_path):
        """
        FAIL分析邏輯：
        - 按照PASS邏輯解析所有測項
        - PASS的項目放到PASS區塊
        - FAIL的項目放到FAIL區塊
        - 支援"未找到指令"集合功能
        """
        pass_items = []
        fail_items = []
        no_command_steps = []
        current_step = None
        
        for idx, line in enumerate(raw_lines):
            # 找到 Do @STEPxxx@ 行 - 測項開始
            step_match = self.step_pattern.search(line)
            if step_match:
                # 完成前一個測項
                if current_step:
                    current_step['end_idx'] = idx - 1
                    self._finalize_step(current_step, pass_items, fail_items, no_command_steps)
                
                # 開始新測項
                step_name_clean = step_match.group(1).strip()
                # 提取STEP號碼
                step_number = ''
                if step_name_clean.startswith('@STEP') and '@' in step_name_clean[1:]:
                    step_parts = step_name_clean.split('@')
                    if len(step_parts) >= 2:
                        step_number = step_parts[1]
                    step_name_clean = step_name_clean.split('@', 2)[-1]
                
                current_step = {
                    'step_name': step_name_clean,
                    'test_id': '',
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
                    'is_pass': None  # 待確定
                }
                continue
            
            if current_step:
                current_step['full_log'].append(line)
                
                # 檢查是否為PASS結束行
                if self._is_step_end_line(line, current_step.get('step_number', '')):
                    current_step['end_idx'] = idx
                    current_step['is_pass'] = True
                    current_step['result'] = 'PASS'
                    self._finalize_step(current_step, pass_items, fail_items, no_command_steps)
                    current_step = None
                    continue
                
                # 檢查是否為FAIL行
                if any(keyword in line.upper() for keyword in ['FAIL', 'FAILED', 'ERROR']):
                    current_step['is_pass'] = False
                    current_step['result'] = 'FAIL'
                    current_step['error'] = line.strip()
                
                # 檢查指令行
                cmd_match = self.cmd_pattern.search(line)
                if cmd_match and not current_step['command']:
                    current_step['command'] = cmd_match.group(1).strip()
                
                # 檢查回應行
                if not current_step['response']:
                    resp_match = self.resp_pattern.search(line)
                    if resp_match:
                        current_step['response'] = resp_match.group(1).strip()
        
        # 處理最後一個測項
        if current_step:
            current_step['end_idx'] = len(raw_lines) - 1
            # 如果沒有明確的PASS/FAIL標記，根據是否有錯誤判斷
            if current_step['is_pass'] is None:
                current_step['is_pass'] = not bool(current_step['error'])
                current_step['result'] = 'PASS' if current_step['is_pass'] else 'FAIL'
            self._finalize_step(current_step, pass_items, fail_items, no_command_steps)
        
        # 處理"未找到指令"的集合
        self._consolidate_no_command_steps(pass_items, no_command_steps)
        
        # 找到主要FAIL (Logic: Improved 4-Level Priority)
        # Priority 1: Last "doesn't match"
        # Priority 2: Last "is Fail"
        # Priority 3: Last "FAIL"
        # Priority 4: Last "ERROR"
        # Fallback: Last item
        
        last_fail = None
        
        # Helper to filter items containing a keyword (case-insensitive checks where appropriate)
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

        # 1. doesn't match
        matches = filter_items(fail_items, "doesn't match", case_sensitive=False)
        if matches:
            last_fail = matches[-1]
        
        # 2. is Fail (case sensitive "is Fail" based on user example, but safe to ignore case if consistent)
        # User example: "Imtest is Fail !"
        if not last_fail:
            matches = filter_items(fail_items, "is Fail", case_sensitive=False)
            if matches:
                last_fail = matches[-1]

        # 3. FAIL (Generic)
        if not last_fail:
            matches = filter_items(fail_items, "FAIL", case_sensitive=False) # 'FAIL' is usually upper case in logs, but let's be broad
            if matches:
                last_fail = matches[-1]

        # 4. ERROR (Generic)
        if not last_fail:
            matches = filter_items(fail_items, "ERROR", case_sensitive=False)
            if matches:
                last_fail = matches[-1]
                
        # 5. Fallback
        if not last_fail and fail_items:
            last_fail = fail_items[-1]

        # === CRITICAL FIX: Extract Precise Error Text ===
        # Ensure the 'error' field contains the specific line that triggered the priority match,
        # not just the last error line in the step (which might be "All Test Aborted").
        if last_fail:
            target_keywords = ["doesn't match", "is Fail", "FAIL", "ERROR"]
            # Check full_log for the highest priority keyword that is present
            for keyword in target_keywords:
                # Find all lines in this step containing the keyword
                matching_lines = [
                    line for line in last_fail.get('full_log', []) 
                    if keyword.lower() in str(line).lower()
                ]
                
                if matching_lines:
                    # Update 'error' to the LAST matching line (RETEST logic)
                    last_fail['error'] = matching_lines[-1].strip()
                    break # Stop after finding the highest priority keyword match
            
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
        
        # 從最後一行往上掃描，找符合關鍵字的行
        for idx in range(len(raw_lines) - 1, -1, -1):
            line = raw_lines[idx]
            
            # 檢查是否包含FAIL關鍵字且未被處理過
            if (any(keyword in line.upper() for keyword in ["FAIL", "FAILED", "ERROR"]) 
                and idx not in visited_lines):
                
                # 往上回溯到該測項的 Do @STEPxxx@ 行（或指令行 >）
                block_start = self._find_block_start(raw_lines, idx)
                
                # 往下延伸到 root@ 行
                block_end = self._find_block_end(raw_lines, idx)
                
                if block_start is not None and block_end is not None:
                    # 提取完整錯誤區塊
                    block_lines = raw_lines[block_start:block_end + 1]
                    
                    fail_block = {
                        'block_lines': block_lines,
                        'start_idx': block_start,
                        'end_idx': block_end,
                        'fail_idx': idx,
                        'full_log': block_lines  # 錯誤區塊完整內容（顯示紅字）
                    }
                    
                    fail_blocks.append(fail_block)
                    
                    # 標記已處理的行
                    visited_lines.update(range(block_start, block_end + 1))
        
        return fail_blocks
    
    def _find_block_start(self, raw_lines, fail_idx):
        """往上回溯到該測項的 Do @STEPxxx@ 行（或指令行 >）"""
        # 先找 Do @STEPxxx@ 行
        for i in range(fail_idx, max(0, fail_idx - 200), -1):
            if self.step_pattern.search(raw_lines[i]):
                return i
        
        # 如果沒找到 Do @STEPxxx@，找指令行 >
        for i in range(fail_idx, max(0, fail_idx - 100), -1):
            if self.cmd_pattern.search(raw_lines[i]):
                return i
        
        # 都沒找到，使用fail_idx往前50行
        return max(0, fail_idx - 50)
    
    def _find_block_end(self, raw_lines, fail_idx):
        """往下延伸到下一個 Do @STEPxxx@ 行或檔案結束"""
        for i in range(fail_idx, min(len(raw_lines), fail_idx + 200)):
            # 找到下一個 Do @STEPxxx@ 行
            if self.step_pattern.search(raw_lines[i]):
                return i - 1
            
            # 如果到達檔案結尾
            if i == len(raw_lines) - 1:
                return i
        
        # 如果沒找到下一個測項，使用fail_idx往後200行
        return min(len(raw_lines) - 1, fail_idx + 200)
    
    def _find_fail_blocks(self, raw_lines):
        """從底部往上找 FAIL/ERROR 區塊"""
        blocks = []
        visited_lines = set()
        
        # 從底部往上掃描
        for idx in range(len(raw_lines) - 1, -1, -1):
            line = raw_lines[idx]
            
            # 檢查是否包含FAIL關鍵字且未被處理過
            if any(keyword in line.upper() for keyword in self.fail_keywords) and idx not in visited_lines:
                block_info = self._extract_fail_block(raw_lines, idx)
                if block_info:
                    blocks.append(block_info)
                    # 標記已處理的行
                    start_idx = block_info.get('start_idx', idx)
                    end_idx = block_info.get('end_idx', idx)
                    visited_lines.update(range(start_idx, end_idx + 1))
        
        return blocks
    
    def _extract_fail_block(self, raw_lines, fail_idx):
        """提取FAIL區塊：從指令開始到結束"""
        start_idx = fail_idx
        end_idx = fail_idx
        
        # 往上找到指令起點
        for i in range(fail_idx, max(0, fail_idx - 50), -1):
            if self.cmd_pattern.search(raw_lines[i]):
                start_idx = i
                break
        
        # 往下找到結束點（root@行或下一個指令）
        for i in range(fail_idx, min(len(raw_lines), fail_idx + 20)):
            if i > fail_idx and (self.root_pattern.search(raw_lines[i]) or self.cmd_pattern.search(raw_lines[i])):
                end_idx = i
                break
            end_idx = i
        
        # 提取區塊
        block_lines = raw_lines[start_idx:end_idx + 1]
        
        return {
            'block_lines': block_lines,
            'start_idx': start_idx,
            'end_idx': end_idx,
            'fail_idx': fail_idx
        }
    
    def _extract_fail_step_info(self, fail_block, raw_lines):
        """從FAIL區塊中提取步驟資訊"""
        block_lines = fail_block['block_lines']
        fail_idx = fail_block['fail_idx']
        
        # Step Name - 從區塊中找 Do @STEPxxx@ 或從附近找
        step_name = self._find_step_name_in_block(block_lines, raw_lines, fail_block['start_idx'])
        
        # 錯誤指令 - 該錯誤區塊的第一個 > 行
        command = ''
        for line in block_lines:
            cmd_match = self.cmd_pattern.search(line)
            if cmd_match:
                command = cmd_match.group(1).strip()
                break
        
        # 錯誤回應 - 該錯誤區塊的第一個 < 行
        response = ''
        for line in block_lines:
            resp_match = self.resp_pattern.search(line)
            if resp_match:
                response = resp_match.group(1).strip()
                break
        
        # Retry 次數（忽略 Run 行上的 Retry 欄位）
        retry_count = self._get_effective_retry_count(block_lines)
        
        # FAIL原因 - 從錯誤訊息行擷取
        error_reason = self._find_error_reason(block_lines)
        
        # full_log - 錯誤區塊完整內容（顯示紅字），加入Attempt標註
        full_log = block_lines
        
        # 設定預設值
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
        """從起始行往上找最近的 Step 名稱"""
        for i in range(start_idx, max(0, start_idx - 100), -1):
            step_match = self.step_pattern.search(raw_lines[i])
            if step_match:
                return step_match.group(1).strip()
        return "Unknown Step"
    
    def _find_error_reason(self, block_lines):
        """尋找FAIL原因"""
        for line in block_lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['failed', 'error', 'nack', 'timeout', 'fail']):
                # 處理類似 "VSCH026-043:Chec Frimware version is Fail ! <ErrorCode: BSFR18>" 的格式
                # 提取冒號後到 "is Fail" 或 "is Failed" 的部分
                if ':' in line and ('is fail' in line_lower or 'is failed' in line_lower):
                    # 找到冒號的位置
                    colon_pos = line.find(':')
                    if colon_pos != -1:
                        # 提取冒號後的部分
                        after_colon = line[colon_pos + 1:].strip()
                        # 尋找 "is Fail" 或 "is Failed" 的位置
                        fail_pos = -1
                        if 'is fail !' in after_colon.lower():
                            fail_pos = after_colon.lower().find('is fail !')
                            end_pos = fail_pos + 8  # "is Fail !" 的長度
                        elif 'is failed !' in after_colon.lower():
                            fail_pos = after_colon.lower().find('is failed !')
                            end_pos = fail_pos + 10  # "is Failed !" 的長度
                        elif 'is fail' in after_colon.lower():
                            fail_pos = after_colon.lower().find('is fail')
                            end_pos = fail_pos + 7  # "is Fail" 的長度
                        elif 'is failed' in after_colon.lower():
                            fail_pos = after_colon.lower().find('is failed')
                            end_pos = fail_pos + 9  # "is Failed" 的長度
                        
                        if fail_pos != -1:
                            # 提取錯誤訊息部分
                            error_msg = after_colon[:end_pos].strip()
                            return error_msg
                
                # 如果沒有找到特定格式，返回整行
                return line.strip()
        return "Unknown Error"
    
    def _find_step_name_in_block(self, block_lines, raw_lines, start_idx):
        """從區塊中或附近找Step名稱"""
        # 先在區塊中找
        for line in block_lines:
            step_match = self.step_pattern.search(line)
            if step_match:
                step_name_clean = step_match.group(1).strip()
                # 移除 @STEPxxx@ 前綴，只保留後面的名稱
                if step_name_clean.startswith('@STEP') and '@' in step_name_clean[1:]:
                    step_name_clean = step_name_clean.split('@', 2)[-1]
                return step_name_clean
        
        # 在區塊外往上找
        for i in range(start_idx, max(0, start_idx - 50), -1):
            step_match = self.step_pattern.search(raw_lines[i])
            if step_match:
                step_name_clean = step_match.group(1).strip()
                # 移除 @STEPxxx@ 前綴，只保留後面的名稱
                if step_name_clean.startswith('@STEP') and '@' in step_name_clean[1:]:
                    step_name_clean = step_name_clean.split('@', 2)[-1]
                return step_name_clean
        
        return "Unknown Step"
    
    def _generate_ui_annotations(self, raw_lines, is_pass_log):
        """產生UI標註資訊"""
        annotations = []
        
        for idx, line in enumerate(raw_lines):
            annotation = {
                'line_idx': idx,
                'line_content': line,
                'color': 'black',
                'background': 'white',
                'is_clickable': False,
                'hover_color': None
            }
            
            # Step 區塊標註
            if self.step_pattern.search(line):
                annotation['color'] = 'green' if is_pass_log else 'blue'
                annotation['background'] = '#E8F4FD' if idx % 2 == 0 else '#F0E8FF'
                annotation['is_clickable'] = True
                annotation['hover_color'] = '#FFFF99'
            
            # PASS/FAIL 標註
            elif 'PASS' in line.upper():
                annotation['color'] = 'green'
            elif any(keyword in line.upper() for keyword in ['FAIL', 'ERROR']):
                annotation['color'] = 'red'
            
            # 指令/回應標註
            elif self.cmd_pattern.search(line):
                annotation['color'] = 'blue'
            elif self.resp_pattern.search(line):
                annotation['color'] = 'purple'
            
            annotations.append(annotation)
        
        return annotations
    
    def parse_log_folder(self, folder_path):
        """
        解析資料夾內所有log檔案，回傳彙總結果
        """
        pass_items = []
        fail_items = []
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.log'):
                    file_path = os.path.join(root, file)
                    try:
                        result = self.parse_log_file(file_path)
                        file_name = os.path.basename(file_path)
                        # 為每筆結果加上來源檔名，便於彙整與匯出
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
        """將連續的"未找到指令"步驟集合成多個分組，不一次收集全部"""
        if not no_command_steps:
            return
        
        # 按照在 pass_items 中的順序重新排序 no_command_steps
        # 找出每個 no_command_step 在原始順序中的位置
        no_command_with_order = []
        for step in no_command_steps:
            no_command_with_order.append((step['raw_idx'], step))
        
        # 按原始順序排序
        no_command_with_order.sort(key=lambda x: x[0])
        
        # 將 pass_items 和 no_command_steps 合併並按順序排序
        all_steps = []
        for step in pass_items:
            all_steps.append((step['raw_idx'], step, 'normal'))
        
        for raw_idx, step in no_command_with_order:
            all_steps.append((raw_idx, step, 'no_command'))
        
        # 按原始順序排序
        all_steps.sort(key=lambda x: x[0])
        
        # 重新構建 pass_items，將連續的"未找到指令"集合起來
        new_pass_items = []
        current_no_command_group = []
        
        for raw_idx, step, step_type in all_steps:
            if step_type == 'no_command':
                # 收集連續的"未找到指令"
                current_no_command_group.append(step)
            else:
                # 遇到正常步驟，先處理之前收集的"未找到指令"組
                if current_no_command_group:
                    consolidated_step = self._create_consolidated_step(current_no_command_group)
                    new_pass_items.append(consolidated_step)
                    current_no_command_group = []
                
                # 添加正常步驟
                new_pass_items.append(step)
        
        # 處理最後一組"未找到指令"
        if current_no_command_group:
            consolidated_step = self._create_consolidated_step(current_no_command_group)
            new_pass_items.append(consolidated_step)
        
        # 更新 pass_items
        pass_items.clear()
        pass_items.extend(new_pass_items)
    
    def _create_consolidated_step(self, no_command_group):
        """創建一個"未找到指令"集合項目"""
        consolidated_content = []
        for i, step in enumerate(no_command_group, 1):
            # 添加步驟名稱和內容
            step_header = f"步驟 {i}: {step['step_name']}"
            consolidated_content.append(step_header)
            
            # 添加該步驟的完整日誌內容
            for j, line in enumerate(step['full_log'], 1):
                consolidated_content.append(f"  {j:4d}. {line}")
            consolidated_content.append("")  # 空行分隔
        
        # 創建集合項目
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
            'is_consolidated': True  # 標記為集合項目
        }
    
    def _get_effective_retry_count(self, lines):
        """基於指令出現次數判斷RETRY，而不是基於Retry: N關鍵字"""
        # 提取所有指令
        commands = []
        for line in lines:
            cmd_match = self.cmd_pattern.search(line)
            if cmd_match:
                command = cmd_match.group(1).strip()
                commands.append(command)
        
        if not commands:
            return 0
        
        # 計算主要指令的出現次數
        main_command = commands[0]  # 第一個指令作為主要指令
        command_count = commands.count(main_command)
        
        # 如果指令出現次數大於1，表示有RETRY
        return command_count if command_count > 1 else 0