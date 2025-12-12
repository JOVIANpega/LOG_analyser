# -*- coding: utf-8 -*-
"""
UI工具函数模块
提取错误信息、格式化等通用功能
"""

def extract_error_block(log_lines, fail_line_idx):
    """提取錯誤完整區塊"""
    if fail_line_idx is None or fail_line_idx >= len(log_lines):
        return ""
    
    # 往前找到指令開始
    start_idx = fail_line_idx
    for i in range(fail_line_idx, max(0, fail_line_idx - 50), -1):
        if '>' in log_lines[i]:  # 找到指令行
            start_idx = i
            break
    
    # 往後找到錯誤結束（或下一個指令）
    end_idx = fail_line_idx
    for i in range(fail_line_idx, min(len(log_lines), fail_line_idx + 20)):
        if i > fail_line_idx and ('>' in log_lines[i] or 'Do @STEP' in log_lines[i]):
            break
        end_idx = i
    
    # 提取區塊
    error_block = '\n'.join(log_lines[start_idx:end_idx + 1])
    return error_block
