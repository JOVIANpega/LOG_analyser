#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試Log分析器
主要功能：分析測試log檔，提取測項資訊並分類為PASS/FAIL
"""

import re
import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import logging
from log_format_manager import LogFormatManager, FormatConverter

class LogAnalyzer:
    """
    測試Log分析器類別
    負責解析log檔案，提取測項資訊並分類結果
    """
    
    def __init__(self):
        """初始化分析器"""
        self.pass_tests = []  # 儲存通過的測試項目
        self.fail_tests = []  # 儲存失敗的測試項目
        self.script_tests = []  # 儲存腳本中的測試項目
        self.log_content = ""  # 原始log內容
        self.current_format = "pega_standard"  # 當前使用的格式
        
        # 初始化格式管理器
        self.format_manager = LogFormatManager()
        self.format_converter = FormatConverter()
        
        # 設定正則表達式模式（預設PEGA格式）
        self.patterns = {
            'step': r'Do @STEP\d+@([^@]+)',
            'test_id': r'Run ([A-Z0-9]+-\d+):',
            'command': r'^\s*>\s*(.+)',
            'response': r'^\s*<\s*(.+)',
            'pass_result': r'Test is Pass !',
            'fail_result': r'Test is Fail',
            'execution_time': r'----- ([\d.]+) Sec\.',
            'retry_count': r'Retry:\s*(\d+)',
            'error_message': r'Error:|Exception:|Failed:|Timeout:',
            'phase': r'Execute Phase (\d+) Test\.'
        }
        
        # 設定logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def load_log_file(self, file_path: str) -> bool:
        """
        載入單一log檔案
        
        Args:
            file_path: log檔案路徑
            
        Returns:
            bool: 是否成功載入
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                self.log_content = f.read()
            self.logger.info(f"成功載入log檔案: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"載入log檔案失敗: {e}")
            return False
        
        # 自動檢測LOG格式
        if self.log_content:
            self._auto_detect_format(file_path)
        
        return True
    
    def load_log_directory(self, directory_path: str) -> bool:
        """
        載入整個資料夾的log檔案
        
        Args:
            directory_path: 資料夾路徑
            
        Returns:
            bool: 是否成功載入
        """
        try:
            all_content = []
            log_files = []
            
            # 尋找所有.log檔案
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    if file.endswith('.log'):
                        log_files.append(os.path.join(root, file))
            
            if not log_files:
                self.logger.warning(f"在目錄 {directory_path} 中未找到.log檔案")
                return False
            
            # 載入所有log檔案
            for log_file in log_files:
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        all_content.append(f"=== {log_file} ===\n{content}\n")
                except Exception as e:
                    self.logger.warning(f"無法讀取檔案 {log_file}: {e}")
            
            self.log_content = "\n".join(all_content)
            self.logger.info(f"成功載入 {len(log_files)} 個log檔案")
            return True
            
        except Exception as e:
            self.logger.error(f"載入log目錄失敗: {e}")
            return False
    
    def parse_test_steps(self) -> Tuple[List[Dict], List[Dict]]:
        """
        解析log中的測試步驟
        
        Returns:
            Tuple[List[Dict], List[Dict]]: (通過的測試, 失敗的測試)
        """
        if not self.log_content:
            return [], []
        
        lines = self.log_content.split('\n')
        pass_tests = []
        fail_tests = []
        
        current_test = None
        current_phase = 0
        
        for i, line in enumerate(lines):
            # 檢查是否為新的Phase
            phase_match = re.search(self.patterns['phase'], line)
            if phase_match:
                current_phase = int(phase_match.group(1))
                continue
            
            # 檢查是否為新的測試步驟
            step_match = re.search(self.patterns['step'], line)
            if step_match:
                step_name = step_match.group(1).strip()
                
                # 尋找對應的測試ID
                test_id = self._find_test_id(lines, i)
                
                current_test = {
                    'step_name': step_name,
                    'test_id': test_id,
                    'phase': current_phase,
                    'commands': [],
                    'responses': [],
                    'retry_count': 0,
                    'execution_time': 0.0,
                    'error_message': '',
                    'status': 'Unknown'
                }
                continue
            
            # 如果當前有測試項目，繼續收集資訊
            if current_test:
                # 收集指令 - 修正為處理時間戳記格式
                cmd_match = re.search(r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2} \[\d+\]\s*>\s*(.+)', line)
                if cmd_match:
                    current_test['commands'].append(cmd_match.group(1).strip())
                
                # 收集回應 - 修正為處理時間戳記格式
                resp_match = re.search(r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2} \[\d+\]\s*<\s*(.+)', line)
                if resp_match:
                    current_test['responses'].append(resp_match.group(1).strip())
                
                # 檢查重試次數
                retry_match = re.search(self.patterns['retry_count'], line)
                if retry_match:
                    current_test['retry_count'] = int(retry_match.group(1))
                
                # 檢查結果 - 修正為更精確的匹配
                if re.search(self.patterns['pass_result'], line):
                    current_test['status'] = 'PASS'
                    # 提取執行時間
                    time_match = re.search(self.patterns['execution_time'], line)
                    if time_match:
                        current_test['execution_time'] = float(time_match.group(1))
                    
                    # 完成當前測試，加入通過列表
                    if current_test['test_id']:  # 確保有測試ID
                        pass_tests.append(current_test.copy())
                    current_test = None
                
                elif re.search(self.patterns['fail_result'], line):
                    current_test['status'] = 'FAIL'
                    # 提取執行時間
                    time_match = re.search(self.patterns['execution_time'], line)
                    if time_match:
                        current_test['execution_time'] = float(time_match.group(1))
                    
                    # 尋找錯誤訊息
                    error_msg = self._find_error_message(lines, i)
                    current_test['error_message'] = error_msg
                    
                    # 完成當前測試，加入失敗列表
                    if current_test['test_id']:  # 確保有測試ID
                        fail_tests.append(current_test.copy())
                    current_test = None
        
        self.pass_tests = pass_tests
        self.fail_tests = fail_tests
        
        return pass_tests, fail_tests
    
    def _find_test_id(self, lines: List[str], start_index: int) -> str:
        """
        在指定行附近尋找測試ID
        
        Args:
            lines: 所有行
            start_index: 開始搜尋的索引
            
        Returns:
            str: 測試ID
        """
        # 向前搜尋最多10行
        for i in range(max(0, start_index - 10), start_index + 1):
            if i < len(lines):
                match = re.search(self.patterns['test_id'], lines[i])
                if match:
                    return match.group(1)
        return ""
    
    def _find_error_message(self, lines: List[str], start_index: int) -> str:
        """
        在指定行附近尋找錯誤訊息
        
        Args:
            lines: 所有行
            start_index: 開始搜尋的索引
            
        Returns:
            str: 錯誤訊息
        """
        error_msg = ""
        # 向後搜尋最多5行
        for i in range(start_index, min(len(lines), start_index + 5)):
            if re.search(self.patterns['error_message'], lines[i], re.IGNORECASE):
                error_msg = lines[i].strip()
                break
        return error_msg
    
    def load_script_excel(self, excel_path: str) -> bool:
        """
        載入測試腳本Excel檔案
        
        Args:
            excel_path: Excel檔案路徑
            
        Returns:
            bool: 是否成功載入
        """
        try:
            # 嘗試讀取Excel檔案
            df = pd.read_excel(excel_path)
            
            # 根據常見的欄位名稱尋找測試項目
            script_tests = []
            
            # 尋找可能的欄位名稱
            possible_id_columns = ['Test ID', 'TestID', 'ID', 'Test_ID']
            possible_name_columns = ['Step Name', 'StepName', 'Name', 'Description', 'Test Name']
            
            id_column = None
            name_column = None
            
            for col in possible_id_columns:
                if col in df.columns:
                    id_column = col
                    break
            
            for col in possible_name_columns:
                if col in df.columns:
                    name_column = col
                    break
            
            # 如果找不到標準欄位，使用前兩欄
            if id_column is None and len(df.columns) > 0:
                id_column = df.columns[0]
            if name_column is None and len(df.columns) > 1:
                name_column = df.columns[1]
            
            # 提取測試項目
            for index, row in df.iterrows():
                test_id = str(row[id_column]) if id_column else f"Test_{index+1}"
                step_name = str(row[name_column]) if name_column else f"Step_{index+1}"
                
                script_tests.append({
                    'test_id': test_id,
                    'step_name': step_name,
                    'status': 'Not Executed'  # 預設狀態
                })
            
            self.script_tests = script_tests
            self.logger.info(f"成功載入腳本Excel檔案: {excel_path}, 共 {len(script_tests)} 個測試項目")
            return True
            
        except Exception as e:
            self.logger.error(f"載入Excel檔案失敗: {e}")
            return False
    
    def compare_with_script(self) -> Dict:
        """
        比對實際執行結果與腳本
        
        Returns:
            Dict: 比對結果
        """
        if not self.script_tests:
            return {}
        
        # 建立實際執行的測試ID集合
        executed_pass = {test['test_id'] for test in self.pass_tests}
        executed_fail = {test['test_id'] for test in self.fail_tests}
        all_executed = executed_pass | executed_fail
        
        # 建立腳本中的測試ID集合
        script_test_ids = {test['test_id'] for test in self.script_tests}
        
        # 比對結果
        comparison = {
            'executed_pass': list(executed_pass),
            'executed_fail': list(executed_fail),
            'not_executed': list(script_test_ids - all_executed),
            'extra_executed': list(all_executed - script_test_ids),
            'total_script': len(self.script_tests),
            'total_executed': len(all_executed),
            'total_pass': len(self.pass_tests),
            'total_fail': len(self.fail_tests)
        }
        
        return comparison
    
    def export_to_excel(self, output_path: str) -> bool:
        """
        匯出分析結果到Excel檔案
        
        Args:
            output_path: 輸出檔案路徑
            
        Returns:
            bool: 是否成功匯出
        """
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # 匯出PASS測試
                if self.pass_tests:
                    pass_df = pd.DataFrame(self.pass_tests)
                    pass_df = pass_df[['step_name', 'test_id', 'commands', 'responses', 'status', 'execution_time']]
                    pass_df.columns = ['Step Name', 'Test ID', '指令', '回應', '結果', '執行時間(秒)']
                    pass_df.to_excel(writer, sheet_name='PASS測試', index=False)
                
                # 匯出FAIL測試
                if self.fail_tests:
                    fail_df = pd.DataFrame(self.fail_tests)
                    fail_df = fail_df[['step_name', 'test_id', 'commands', 'responses', 'retry_count', 'error_message', 'execution_time']]
                    fail_df.columns = ['Step Name', 'Test ID', '指令', '錯誤回應', 'Retry次數', 'FAIL原因', '執行時間(秒)']
                    fail_df.to_excel(writer, sheet_name='FAIL測試', index=False)
                
                # 匯出腳本比對報告
                comparison = self.compare_with_script()
                if comparison:
                    comparison_data = []
                    
                    # 已執行且通過的測試
                    for test_id in comparison['executed_pass']:
                        comparison_data.append({
                            'Test ID': test_id,
                            'Status': '✅ PASS',
                            'Note': '已執行且通過'
                        })
                    
                    # 已執行但失敗的測試
                    for test_id in comparison['executed_fail']:
                        comparison_data.append({
                            'Test ID': test_id,
                            'Status': '❌ FAIL',
                            'Note': '已執行但失敗'
                        })
                    
                    # 未執行的測試
                    for test_id in comparison['not_executed']:
                        comparison_data.append({
                            'Test ID': test_id,
                            'Status': '⚠️ NOT EXECUTED',
                            'Note': '腳本中有但未執行'
                        })
                    
                    # 額外執行的測試
                    for test_id in comparison['extra_executed']:
                        comparison_data.append({
                            'Test ID': test_id,
                            'Status': '➕ EXTRA',
                            'Note': '執行但腳本中沒有'
                        })
                    
                    if comparison_data:
                        comp_df = pd.DataFrame(comparison_data)
                        comp_df.to_excel(writer, sheet_name='腳本比對報告', index=False)
                
                # 匯出統計摘要
                summary_data = {
                    '項目': ['總測試數', '通過數', '失敗數', '成功率'],
                    '數值': [
                        len(self.pass_tests) + len(self.fail_tests),
                        len(self.pass_tests),
                        len(self.fail_tests),
                        f"{len(self.pass_tests) / (len(self.pass_tests) + len(self.fail_tests)) * 100:.1f}%" if (len(self.pass_tests) + len(self.fail_tests)) > 0 else "0%"
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='統計摘要', index=False)
            
            self.logger.info(f"成功匯出Excel檔案: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"匯出Excel檔案失敗: {e}")
            return False
    
    def clear_results(self):
        """清除分析結果"""
        self.pass_tests = []
        self.fail_tests = []
        self.script_tests = []
        self.log_content = ""
        self.logger.info("已清除所有分析結果")
    
    def _auto_detect_format(self, file_path: str = ""):
        """自動檢測LOG格式"""
        if not self.log_content:
            return
        
        detected_format = self.format_manager.auto_detect_format(self.log_content, file_path)
        if detected_format != "unknown":
            self.set_format_patterns(detected_format)
            self.logger.info(f"自動檢測到LOG格式: {detected_format}")
        else:
            self.logger.warning("無法自動檢測LOG格式，使用預設PEGA格式")
    
    def set_format_patterns(self, format_key: str):
        """設定解析模式"""
        format_config = self.format_manager.get_format_config(format_key)
        if format_config:
            self.patterns = format_config['patterns']
            self.current_format = format_key
            self.logger.info(f"已切換到格式: {format_config['name']}")
        else:
            self.logger.warning(f"未找到格式配置: {format_key}")
    
    def get_current_format_name(self) -> str:
        """獲取當前格式名稱"""
        format_config = self.format_manager.get_format_config(self.current_format)
        return format_config['name'] if format_config else "未知格式"
    
    def get_available_formats(self) -> List[str]:
        """獲取所有可用格式名稱"""
        return self.format_manager.get_format_names()
    
    def parse_test_steps(self) -> Tuple[List[Dict], List[Dict]]:
        """解析log中的測試步驟（支援多格式）"""
        if not self.log_content:
            return [], []
        
        # 根據當前格式選擇解析方法
        if self.current_format == "pega_standard":
            return self._parse_pega_format()
        elif self.current_format == "iqgprf_format":
            return self._parse_iqgprf_format()
        elif self.current_format == "generic_test":
            return self._parse_generic_format()
        else:
            # 預設使用PEGA格式解析
            return self._parse_pega_format()
    
    def _parse_pega_format(self) -> Tuple[List[Dict], List[Dict]]:
        """解析PEGA格式（原有邏輯）"""
        # 這裡保持原有的解析邏輯
        lines = self.log_content.split('\n')
        pass_tests = []
        fail_tests = []
        
        current_test = None
        current_phase = 0
        
        for i, line in enumerate(lines):
            # 檢查是否為新的Phase
            phase_match = re.search(self.patterns['phase'], line)
            if phase_match:
                current_phase = int(phase_match.group(1))
                continue
            
            # 檢查是否為新的測試步驟
            step_match = re.search(self.patterns['step'], line)
            if step_match:
                step_name = step_match.group(1).strip()
                
                # 尋找對應的測試ID
                test_id = self._find_test_id(lines, i)
                
                current_test = {
                    'step_name': step_name,
                    'test_id': test_id,
                    'phase': current_phase,
                    'commands': [],
                    'responses': [],
                    'retry_count': 0,
                    'execution_time': 0.0,
                    'error_message': '',
                    'status': 'Unknown'
                }
                continue
            
            # 如果當前有測試項目，繼續收集資訊
            if current_test:
                # 收集指令
                cmd_match = re.search(self.patterns['command'], line)
                if cmd_match:
                    current_test['commands'].append(cmd_match.group(1).strip())
                
                # 收集回應
                resp_match = re.search(self.patterns['response'], line)
                if resp_match:
                    current_test['responses'].append(resp_match.group(1).strip())
                
                # 檢查重試次數
                retry_match = re.search(self.patterns['retry_count'], line)
                if retry_match:
                    current_test['retry_count'] = int(retry_match.group(1))
                
                # 檢查結果
                if re.search(self.patterns['pass_result'], line):
                    current_test['status'] = 'PASS'
                    # 提取執行時間
                    time_match = re.search(self.patterns['execution_time'], line)
                    if time_match:
                        current_test['execution_time'] = float(time_match.group(1))
                    
                    # 完成當前測試，加入通過列表
                    if current_test['test_id']:
                        pass_tests.append(current_test.copy())
                    current_test = None
                
                elif re.search(self.patterns['fail_result'], line):
                    current_test['status'] = 'FAIL'
                    # 提取執行時間
                    time_match = re.search(self.patterns['execution_time'], line)
                    if time_match:
                        current_test['execution_time'] = float(time_match.group(1))
                    
                    # 尋找錯誤訊息
                    error_msg = self._find_error_message(lines, i)
                    current_test['error_message'] = error_msg
                    
                    # 完成當前測試，加入失敗列表
                    if current_test['test_id']:
                        fail_tests.append(current_test.copy())
                    current_test = None
        
        self.pass_tests = pass_tests
        self.fail_tests = fail_tests
        
        return pass_tests, fail_tests
    
    def _parse_iqgprf_format(self) -> Tuple[List[Dict], List[Dict]]:
        """解析IQGPRF格式"""
        lines = self.log_content.split('\n')
        pass_tests = []
        fail_tests = []
        
        current_test = None
        current_phase = 0
        
        for i, line in enumerate(lines):
            # 檢查是否為新的Phase
            if 'phase' in self.patterns:
                phase_match = re.search(self.patterns['phase'], line)
                if phase_match:
                    current_phase = int(phase_match.group(1))
                    continue
            
            # 檢查是否為新的測試步驟
            if 'step' in self.patterns:
                step_match = re.search(self.patterns['step'], line)
                if step_match:
                    step_name = step_match.group(1).strip()
                    
                    # 尋找對應的測試ID
                    test_id = self._find_test_id(lines, i)
                    
                    current_test = {
                        'step_name': step_name,
                        'test_id': test_id,
                        'phase': current_phase,
                        'commands': [],
                        'responses': [],
                        'retry_count': 0,
                        'execution_time': 0.0,
                        'error_message': '',
                        'status': 'Unknown'
                    }
                    continue
            
            # 如果當前有測試項目，繼續收集資訊
            if current_test:
                # 收集指令
                if 'command' in self.patterns:
                    cmd_match = re.search(self.patterns['command'], line)
                    if cmd_match:
                        current_test['commands'].append(cmd_match.group(1).strip())
                
                # 收集回應
                if 'response' in self.patterns:
                    resp_match = re.search(self.patterns['response'], line)
                    if resp_match:
                        current_test['responses'].append(resp_match.group(1).strip())
                
                # 檢查重試次數
                if 'retry_count' in self.patterns:
                    retry_match = re.search(self.patterns['retry_count'], line)
                    if retry_match:
                        current_test['retry_count'] = int(retry_match.group(1))
                
                # 檢查結果
                if 'pass_result' in self.patterns and re.search(self.patterns['pass_result'], line):
                    current_test['status'] = 'PASS'
                    # 提取執行時間
                    if 'execution_time' in self.patterns:
                        time_match = re.search(self.patterns['execution_time'], line)
                        if time_match:
                            current_test['execution_time'] = float(time_match.group(1))
                    
                    # 完成當前測試，加入通過列表
                    if current_test['test_id']:
                        pass_tests.append(current_test.copy())
                    current_test = None
                
                elif 'fail_result' in self.patterns and re.search(self.patterns['fail_result'], line):
                    current_test['status'] = 'FAIL'
                    # 提取執行時間
                    if 'execution_time' in self.patterns:
                        time_match = re.search(self.patterns['execution_time'], line)
                        if time_match:
                            current_test['execution_time'] = float(time_match.group(1))
                    
                    # 尋找錯誤訊息
                    error_msg = self._find_error_message(lines, i)
                    current_test['error_message'] = error_msg
                    
                    # 完成當前測試，加入失敗列表
                    if current_test['test_id']:
                        fail_tests.append(current_test.copy())
                    current_test = None
        
        self.pass_tests = pass_tests
        self.fail_tests = fail_tests
        
        return pass_tests, fail_tests
    
    def _parse_generic_format(self) -> Tuple[List[Dict], List[Dict]]:
        """解析通用格式（類似IQGPRF的邏輯）"""
        return self._parse_iqgprf_format() 