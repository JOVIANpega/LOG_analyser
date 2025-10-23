#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOG格式管理系統
支援多種LOG格式的自動檢測和轉換
"""

import re
import os
import json
from typing import Dict, List, Tuple, Optional
import logging

class LogFormatManager:
    """LOG格式管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 預設格式配置
        self.available_formats = {
            'pega_standard': {
                'name': 'PEGA標準格式',
                'description': 'Do @STEP@ 格式，Test is Pass/Fail',
                'file_patterns': ['pega', 'test'],
                'patterns': {
                    'step': r'Do @STEP\d+@([^@]+)',
                    'test_id': r'Run ([A-Z0-9]+-\d+):',
                    'command': r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2} \[\d+\]\s*>\s*(.+)',
                    'response': r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2} \[\d+\]\s*<\s*(.+)',
                    'pass_result': r'Test is Pass !',
                    'fail_result': r'Test is Fail',
                    'execution_time': r'----- ([\d.]+) Sec\.',
                    'retry_count': r'Retry:\s*(\d+)',
                    'phase': r'Execute Phase (\d+) Test\.'
                }
            },
            'iqgprf_format': {
                'name': 'IQGPRF格式',
                'description': 'IQGPRF測試LOG格式',
                'file_patterns': ['iqgprf', 'gprf'],
                'patterns': {
                    'step': r'\[STEP\s*(\d+)\]\s*(.+)',
                    'test_id': r'Test ID:\s*([A-Z0-9_-]+)',
                    'command': r'Command:\s*(.+)',
                    'response': r'Response:\s*(.+)',
                    'pass_result': r'Result:\s*PASS',
                    'fail_result': r'Result:\s*FAIL',
                    'execution_time': r'Time:\s*([\d.]+)s',
                    'retry_count': r'Retry:\s*(\d+)',
                    'phase': r'Phase:\s*(\d+)'
                }
            },
            'generic_test': {
                'name': '通用測試格式',
                'description': '標準的PASS/FAIL測試格式',
                'file_patterns': ['test', 'log'],
                'patterns': {
                    'step': r'(?:Test|Step|Case)\s*[#:]?\s*(\d+)',
                    'test_id': r'(?:ID|TestID):\s*([A-Za-z0-9_-]+)',
                    'command': r'(?:Command|CMD|Input):\s*(.+)',
                    'response': r'(?:Response|RESP|Output):\s*(.+)',
                    'pass_result': r'(?:Result|Status):\s*(?:PASS|SUCCESS|OK)',
                    'fail_result': r'(?:Result|Status):\s*(?:FAIL|ERROR|TIMEOUT)',
                    'execution_time': r'(?:Time|Duration):\s*([\d.]+)',
                    'retry_count': r'(?:Retry|Attempt):\s*(\d+)',
                    'phase': r'(?:Phase|Stage):\s*(\d+)'
                }
            }
        }
        
        # 格式記憶系統
        self.format_history = {}
        self.file_patterns = {}
        
        # 載入格式記憶
        self._load_format_memory()
    
    def auto_detect_format(self, log_content: str, file_path: str = "") -> str:
        """自動檢測LOG格式"""
        
        # 首先嘗試根據檔案名稱預測
        if file_path:
            predicted_format = self._predict_by_filename(file_path)
            if predicted_format:
                self.logger.info(f"根據檔案名稱預測格式: {predicted_format}")
                return predicted_format
        
        # 然後進行內容檢測
        scores = {}
        
        for format_key, format_info in self.available_formats.items():
            score = 0
            total_patterns = len(format_info['patterns'])
            
            for pattern_name, pattern in format_info['patterns'].items():
                if re.search(pattern, log_content, re.MULTILINE | re.IGNORECASE):
                    score += 1
            
            # 計算匹配率
            match_rate = score / total_patterns
            scores[format_key] = {
                'name': format_info['name'],
                'score': score,
                'match_rate': match_rate,
                'key': format_key
            }
        
        # 返回最佳匹配的格式
        if scores:
            best_match = max(scores.values(), key=lambda x: x['match_rate'])
            detected_format = best_match['key']
            
            # 記憶檢測結果
            if file_path:
                self._remember_format(file_path, detected_format)
            
            self.logger.info(f"自動檢測到格式: {best_match['name']} (匹配率: {best_match['match_rate']:.2f})")
            return detected_format
        
        return "unknown"
    
    def _predict_by_filename(self, file_path: str) -> Optional[str]:
        """根據檔案名稱預測格式"""
        filename = os.path.basename(file_path).lower()
        
        # 檢查檔案名稱模式
        for format_key, format_info in self.available_formats.items():
            for pattern in format_info['file_patterns']:
                if pattern in filename:
                    return format_key
        
        # 檢查記憶的模式
        for pattern, format_type in self.file_patterns.items():
            if pattern in filename:
                return format_type
        
        return None
    
    def _remember_format(self, file_path: str, detected_format: str):
        """記住某個檔案的格式"""
        self.format_history[file_path] = detected_format
        
        # 學習檔案名稱模式
        filename = os.path.basename(file_path)
        for format_key, format_info in self.available_formats.items():
            if detected_format == format_key:
                for pattern in format_info['file_patterns']:
                    if pattern in filename.lower():
                        self.file_patterns[pattern] = detected_format
                        break
                break
        
        # 儲存格式記憶
        self._save_format_memory()
    
    def get_format_config(self, format_key: str) -> Optional[Dict]:
        """獲取格式配置"""
        return self.available_formats.get(format_key)
    
    def get_format_names(self) -> List[str]:
        """獲取所有格式名稱"""
        return [format_info['name'] for format_info in self.available_formats.values()]
    
    def get_format_by_name(self, format_name: str) -> Optional[Dict]:
        """根據名稱獲取格式配置"""
        for format_key, format_info in self.available_formats.items():
            if format_info['name'] == format_name:
                return format_info
        return None
    
    def _load_format_memory(self):
        """載入格式記憶"""
        try:
            if os.path.exists('format_memory.json'):
                with open('format_memory.json', 'r', encoding='utf-8') as f:
                    memory_data = json.load(f)
                    self.format_history = memory_data.get('history', {})
                    self.file_patterns = memory_data.get('patterns', {})
        except Exception as e:
            self.logger.warning(f"載入格式記憶失敗: {e}")
    
    def _save_format_memory(self):
        """儲存格式記憶"""
        try:
            memory_data = {
                'history': self.format_history,
                'patterns': self.file_patterns
            }
            with open('format_memory.json', 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.warning(f"儲存格式記憶失敗: {e}")

class FormatConverter:
    """格式轉換器 - 將不同格式轉換為統一格式"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def convert_to_unified_format(self, parsed_data: dict, source_format: str) -> dict:
        """轉換為統一的PASS/FAIL格式"""
        
        if source_format == "pega_standard":
            return self._convert_pega_format(parsed_data)
        elif source_format == "iqgprf_format":
            return self._convert_iqgprf_format(parsed_data)
        elif source_format == "generic_test":
            return self._convert_generic_format(parsed_data)
        else:
            return parsed_data
    
    def _convert_iqgprf_format(self, iqgprf_data: dict) -> dict:
        """轉換IQGPRF格式為統一格式"""
        unified_data = {
            'pass_tests': [],
            'fail_tests': []
        }
        
        # 轉換每個測試項目
        for test in iqgprf_data.get('tests', []):
            unified_test = {
                'step_name': test.get('step_name', ''),
                'test_id': test.get('test_id', ''),
                'phase': test.get('phase', 0),
                'commands': test.get('commands', []),
                'responses': test.get('responses', []),
                'retry_count': test.get('retry_count', 0),
                'execution_time': test.get('execution_time', 0.0),
                'error_message': test.get('error_message', ''),
                'status': test.get('status', 'Unknown')
            }
            
            # 根據狀態分類到PASS或FAIL
            if unified_test['status'] == 'PASS':
                unified_data['pass_tests'].append(unified_test)
            elif unified_test['status'] == 'FAIL':
                unified_data['fail_tests'].append(unified_test)
        
        return unified_data
    
    def _convert_pega_format(self, pega_data: dict) -> dict:
        """轉換PEGA格式為統一格式（保持原有結構）"""
        # PEGA格式已經是統一格式，直接返回
        return pega_data
    
    def _convert_generic_format(self, generic_data: dict) -> dict:
        """轉換通用格式為統一格式"""
        unified_data = {
            'pass_tests': [],
            'fail_tests': []
        }
        
        # 轉換邏輯類似IQGPRF
        for test in generic_data.get('tests', []):
            unified_test = {
                'step_name': test.get('step_name', ''),
                'test_id': test.get('test_id', ''),
                'phase': test.get('phase', 0),
                'commands': test.get('commands', []),
                'responses': test.get('responses', []),
                'retry_count': test.get('retry_count', 0),
                'execution_time': test.get('execution_time', 0.0),
                'error_message': test.get('error_message', ''),
                'status': test.get('status', 'Unknown')
            }
            
            if unified_test['status'] == 'PASS':
                unified_data['pass_tests'].append(unified_test)
            elif unified_test['status'] == 'FAIL':
                unified_data['fail_tests'].append(unified_test)
        
        return unified_data 