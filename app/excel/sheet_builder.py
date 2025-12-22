# -*- coding: utf-8 -*-
"""
Sheet Builder Module
Handles detailed log writing and annotation.
"""
from openpyxl.styles import Font, PatternFill, Alignment
from .excel_utils import sanitize_cell_text

def write_raw_log_with_annotations(ws, start_row: int, raw_lines: list, annotations: list, font):
    """將原始 LOG 與顏色標籤寫入 Excel"""
    color_map = {
        'black': 'FF000000',
        'red': 'FFE74C3C',
        'green': 'FF2ECC71',
        'blue': 'FF3498DB',
        'purple': 'FF9B59B6',
    }
    
    error_line_found = False
    first_error_row = None
    
    for i, raw in enumerate(raw_lines, start=start_row):
        src_idx = i - start_row
        line = str(raw)
        
        # 錯誤識別
        is_error_line = False
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in [
            'is fail', 'segmentation fault', 'core dumped', 'executes fail', 
            "doesn't match", 'timeout', 'exception', 'error', 'fail'
        ]):
            is_error_line = True
            if not error_line_found:
                first_error_row = i
                error_line_found = True
        
        # 清理並寫入
        clean_line = sanitize_cell_text(line)
        cell = ws.cell(row=i, column=1, value=clean_line)
        cell.font = font
        
        # 錯誤行樣式
        if is_error_line:
            cell.font = Font(name=font.name, size=font.size, color='FF0000', bold=True)
            cell.fill = PatternFill('solid', fgColor='FFFFFF99') 
            
        # 標籤對應顏色
        for anno in annotations:
            if anno.get('line_idx') == src_idx:
                color_name = anno.get('color')
                if color_name in color_map:
                    cell.font = Font(name=font.name, size=font.size, color=color_map[color_name])
                break
                
    if first_error_row:
        # A1 連結到第一個錯誤
        ws.cell(row=1, column=1).hyperlink = f"#{ws.title}!A{first_error_row}"

def insert_header_info(ws, header_info, start_row=4):
    """插入置頂 Header 資訊"""
    if not header_info:
        return
        
    lines = header_info.split('\n')
    header_font = Font(name='Consolas', size=14, bold=True, color='000000')
    header_fill = PatternFill('solid', fgColor='90EE90') # 淺綠
    
    for i, line in enumerate(lines):
        cell = ws.cell(row=start_row + i, column=1, value=line)
        cell.font = header_font
        cell.fill = header_fill
        
    return start_row + len(lines) + 1
