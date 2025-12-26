# -*- coding: utf-8 -*-
"""
Excel工具函數模組
提供Excel文件處理的通用工具函數
"""
import re
import os
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from datetime import datetime

def sanitize_cell_text(value: object) -> str:
    """
    清理欲寫入儲存格的文字：
    - 轉為字串並處理 Excel 公式偵測問題 (避免 = 開頭導致損毀)
    - 移除非法控制字元
    - 截斷過長文字
    """
    if value is None:
        return ""
    
    text = str(value)
    
    # --- 關鍵修正：防止 Excel 將 Log 誤認為公式 ---
    # 如果內容以 '=' 開頭，Excel 會嘗試當作公式解析，這在 Log 中極易導致檔案損毀。
    # 加入前綴單引號 (') 是 Excel 官方推薦的轉義純文字方法。
    if text.startswith('='):
        text = "'" + text

    # 移除 ANSI/ESC 序列
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    text = ansi_escape.sub('', text)
    
    # 移除非法字元
    text = ILLEGAL_CHARACTERS_RE.sub('', text)
    
    # 截斷過長文字
    max_len = 30000
    if len(text) > max_len:
        text = text[:max_len] + "...(截斷)"
    
    return text


def extract_isn_from_filename(filename: str) -> str:
    """從檔名嘗試提取 ISN (WE開頭 或 純數字10碼以上)"""
    base_name = os.path.splitext(os.path.basename(filename))[0]
    
    # 嘗試匹配 WE 開頭的序號
    match = re.search(r'(WE\d{9,})', base_name, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    
    # 嘗試匹配純數字 (10碼以上)
    match = re.search(r'(\d{10,})', base_name)
    if match:
        return match.group(1)
    
    return ""


def extract_station_from_filename(filename: str) -> str:
    """
    從檔名提取 Station 名稱
    規則範例: 1+4cam stitching1 test-1110... -> 4cam stitching1
    去除前面的數字和+號，去除 test- 及其後面所有內容
    """
    base_name = os.path.splitext(os.path.basename(filename))[0]
    
    # 去除時間戳 (14位數字)
    base_name = re.sub(r'\d{14}', '', base_name)
    
    # 去除 test- 及其後所有內容
    if 'test-' in base_name.lower():
        base_name = re.split(r'test-', base_name, flags=re.IGNORECASE)[0]
    
    # 去除前面的數字+加號 (例如 "1+")
    base_name = re.sub(r'^\d+\+', '', base_name)
    
    # 清理空白
    station = base_name.strip(' _-')
    
    return station if station else "Unknown"


def sanitize_sheet_title(title: str) -> str:
    """
    移除Excel工作表名稱不允許的字元並修剪長度。
    禁用字元: : \\ / ? * [ ] '，且長度<=31，不可為空。
    """
    if not title:
        return "Sheet"
    
    # 移除禁用字元 (包含單引號，避免連結出錯)
    forbidden_chars = [':', '\\', '/', '?', '*', '[', ']', "'"]
    for char in forbidden_chars:
        title = title.replace(char, '_')
    
    # 限制長度
    if len(title) > 31:
        title = title[:30]
    
    # 截斷後確保不以點號或底線結尾，並移除點號 (避免 Excel 解析超連結出錯)
    title = title.replace(".", "_")
    title = title.strip("_ ")
    
    return title.strip() if title.strip() else "Sheet"


def unique_sheet_name(wb, base_name: str) -> str:
    """確保工作表名稱不重複"""
    base = sanitize_sheet_title(base_name)
    name = base
    counter = 1
    existing = {s.title.lower() for s in wb.worksheets}
    while name.lower() in existing:
        suffix = f"({counter})"
        if len(base) + len(suffix) > 31:
            name = base[:(31-len(suffix))] + suffix
        else:
            name = base + suffix
        counter += 1
    return name


def format_filename_with_timestamp(base_name: str) -> str:
    """將檔名中的連續14位時間戳 YYYYMMDDHHMMSS 轉為 YYYY-MMDD-HHMMSS 格式。"""
    match = re.search(r'(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})', base_name)
    if match:
        ts_old = match.group(0)
        ts_new = f"{match.group(1)}-{match.group(2)}{match.group(3)}-{match.group(4)}{match.group(5)}{match.group(6)}"
        return base_name.replace(ts_old, ts_new)
    return base_name


def auto_fit_columns(ws, min_widths: dict | None = None):
    """
    自動調整欄寬
    min_widths: {column_index_or_letter: width}
    """
    from openpyxl.utils import get_column_letter
    
    for col in ws.columns:
        curr_max_length = 0
        column_letter = get_column_letter(col[0].column)
        
        # 檢查是否有預設最小寬度
        min_w = 10
        if min_widths:
            # 支援數字索引或字母作為 key
            if col[0].column in min_widths:
                min_w = min_widths[col[0].column]
            elif column_letter in min_widths:
                min_w = min_widths[column_letter]
        
        for cell in col:
            try:
                if cell.value:
                    lines = str(cell.value).split('\n')
                    line_max = max(len(l) for l in lines)
                    if line_max > curr_max_length:
                        curr_max_length = line_max
            except:
                pass
        
        # 計算寬度 (字元數 * 系數，並限制最大寬度)
        adjusted_width = (curr_max_length + 2) * 1.2
        if adjusted_width < min_w:
            adjusted_width = min_w
        if adjusted_width > 100: # 最大寬度限制
            adjusted_width = 100
            
        ws.column_dimensions[column_letter].width = adjusted_width

def extract_system_info(raw_lines: list) -> dict:
    """從 raw_lines 擷取系統資訊"""
    system_info = {}
    try:
        content_limit = raw_lines[:300] if len(raw_lines) > 300 else raw_lines
        for i, line in enumerate(content_limit):
            line_str = str(line).strip()
            if not line_str: continue
            
            # 常見欄位匹配
            if 'ISN=' in line_str:
                system_info['ISN'] = line_str.split('ISN=')[-1].split()[0]
            elif 'Script File is' in line_str:
                system_info['Script'] = line_str.split('is')[-1].strip()
            elif 'SFIS is' in line_str:
                system_info['SFIS'] = line_str.split('is')[-1].strip()
            elif 'System Version is' in line_str:
                system_info['Version'] = line_str.split('is')[-1].strip()
            elif 'IP is' in line_str:
                system_info['IP'] = line_str.split('is')[-1].strip()
            # Retest 相關
            elif '- Retest' in line_str:
                system_info['Mode'] = 'Retest'
            
            # 特殊處理：Active IPs 可能在下一行
            if 'Active IPs:' in line_str:
                val = line_str.split('Active IPs:')[-1].strip()
                if val:
                    system_info['Active IPs'] = val
                elif i + 1 < len(content_limit):
                    next_line = str(content_limit[i+1]).strip()
                    if next_line and not next_line.endswith('.'):
                        system_info['Active IPs'] = next_line
        
        return system_info
    except Exception:
        return {}

def extract_total_secs(raw_lines: list) -> tuple[float | None, list[str]]:
    """從 raw_lines 嘗試提取測試總時間 (帶顏色日誌)"""
    logs = []
    try:
        search_lines = raw_lines[-100:] if len(raw_lines) > 100 else raw_lines
        for line in reversed(search_lines):
            line_str = str(line).strip()
            line_lower = line_str.lower()
            
            if 'total test time is' in line_lower:
                time_match = re.search(r'total test time is[^0-9]*?([\d\.]+)\s*sec', line_str, re.IGNORECASE)
                if time_match:
                    val = float(time_match.group(1))
                    if val > 0:
                        msg = f"[DEBUG] 找到測試總時間: {val} 秒 (來源: Total Test Time is)"
                        logs.append(msg)
                        return val, logs
            
            elif 'all phase total test time' in line_lower:
                time_match = re.search(r'-+\s*([\d\.]+)\s*sec', line_str, re.IGNORECASE)
                if time_match:
                    val = float(time_match.group(1))
                    if val > 0:
                        msg = f"[DEBUG] 找到測試總時間: {val} 秒 (來源: All phase Total Test Time)"
                        logs.append(msg)
                        return val, logs
        
        logs.append("[WARNING] 未找到測試總時間")
        return None, logs
    except Exception as e:
        logs.append(f"[ERROR] 提取測試總時間失敗: {e}")
        return None, logs

def extract_main_error_type(error_text: str) -> str:
    """從錯誤文字中提取主要錯誤類型"""
    if not error_text:
        return "Unknown"
    
    error_text_lower = error_text.lower()
    
    # 加入常見關鍵字
    categories = {
        "Segmentation Fault": "System Crash",
        "core dumped": "System Crash",
        "doesn't match": "Value Mismatch",
        "timeout": "Timeout",
        "executes fail": "Execution Fail",
        "Wrong": "Parameter Error",
        "exception": "Exception"
    }
    
    for key, result in categories.items():
        if key.lower() in error_text_lower:
            return result
            
    # 如果沒匹配到，嘗試提取第一行
    first_line = error_text.split('\n')[0].strip()
    if len(first_line) > 50:
        first_line = first_line[:47] + "..."
    return first_line if first_line else "General Fail"

def normalize_error_group(error_text: str) -> str:
    """將錯誤字串標準化為群組鍵"""
    if not error_text: return "Unknown"
    
    # 1. 提取主要錯誤類型
    main_type = extract_main_error_type(error_text)
    
    # 2. 特殊邏輯：如果有 "doesn't match"，過濾掉數值部分
    if "match" in main_type.lower():
        # "Value 123 doesn't match 456" -> "Value mismatch"
        return "Value Mismatch"
        
    # 3. 如果包含 "is Fail"，裁切到那裡
    if "is fail" in error_text.lower():
        parts = re.split(r'is fail', error_text, flags=re.IGNORECASE)
        # 去除前面的測試編號如 B7PL011-202:
        clean_prefix = re.split(r'[:\-]', parts[0])[-1].strip()
        return f"{clean_prefix} is Fail"
        
    return main_type
