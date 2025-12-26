# -*- coding: utf-8 -*-
"""
Sheet Builder Module
Handles detailed log writing and annotation.
"""
import re
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont
from .excel_utils import sanitize_cell_text

def write_raw_log_with_annotations(ws, start_row: int, raw_lines: list, annotations: list, font, fail_items=None, log_type='UNKNOWN'):
    """將原始 LOG 與顏色標籤寫入 Excel (同步 GUI 的 Premium 外觀)"""
    color_map = {
        'black': 'FF000000',
        'red': 'FFFF0000',
        'green': 'FF28a745',
        'blue': 'FF007bff',
        'purple': 'FF6f42c1',
        'pink': 'FFe83e8c'
    }
    
    # 建立一個索引查表
    anno_lookup = {a['line_idx']: a for a in annotations}
    
    # ⚠️ 僅對 FAIL 日誌執行錯誤檢測與預覽生成
    error_line_idx = None
    error_block_preview = []
    
    if log_type == 'FAIL':
        # 優先級偵測錯誤點：DOESN'T MATCH > is Fail > FAIL > ERROR (從最下面往上找)
        dm_pattern = re.compile(r"doesn't match", re.IGNORECASE)
        is_fail_pattern = re.compile(r"is Fail", re.IGNORECASE)
        fail_pattern = re.compile(r"FAIL", re.IGNORECASE)
        error_pattern = re.compile(r"ERROR", re.IGNORECASE)
    
        # 1. 最高優先級：DOESN'T MATCH (Bottom-up)
        for i in range(len(raw_lines)-1, -1, -1):
            if dm_pattern.search(raw_lines[i]):
                error_line_idx = i
                break
        
        # 2. 次優先級：is Fail
        if error_line_idx is None:
            for i in range(len(raw_lines)-1, -1, -1):
                if is_fail_pattern.search(raw_lines[i]):
                    error_line_idx = i
                    break
        
        # 3. 第三優先級：FAIL
        if error_line_idx is None:
            for i in range(len(raw_lines)-1, -1, -1):
                if fail_pattern.search(raw_lines[i]):
                    error_line_idx = i
                    break
        
        # 4. 最後備選：ERROR
        if error_line_idx is None:
            for i in range(len(raw_lines)-1, -1, -1):
                if error_pattern.search(raw_lines[i]):
                    error_line_idx = i
                    break
        
        # 擷取錯誤區塊文字 (用於置頂顯示預覽)
        if error_line_idx is not None:
            b_start = error_line_idx
            for j in range(error_line_idx, max(-1, error_line_idx - 20), -1):
                if '>' in raw_lines[j] or 'Do @STEP' in raw_lines[j]:
                    b_start = j
                    break
            b_end = error_line_idx
            for j in range(error_line_idx, min(len(raw_lines), error_line_idx + 10)):
                b_end = j
                if j > error_line_idx and ('>' in raw_lines[j] or 'Do @STEP' in raw_lines[j]):
                    b_end = j - 1
                    break
                if 'Test Completed' in raw_lines[j] or 'executes fail' in raw_lines[j]:
                    break
            error_block_preview = raw_lines[b_start : b_end + 1]

    # --- 步驟 A: 預先計算置頂區塊高度 ---
    curr_h_row = start_row # 通常是 3 或更高

    # --- 步驟 B: 僅對 FAIL 日誌寫入預覽區塊 ---
    preview_rows_count = 0
    if error_line_idx is not None and log_type == 'FAIL':
        # [ 直接前往錯誤點 ]
        jump_cell = ws.cell(row=curr_h_row, column=1, value="[ 發現錯誤點 ] (點擊跳轉至 Log 正確位置)")
        jump_cell.font = Font(name='Calibri', size=11, bold=True, color="FF0000", underline="single")
        p_row_jump = curr_h_row
        curr_h_row += 1
        
        if error_block_preview:
            pink_fill = PatternFill('solid', fgColor='FFFFE1E1')
            for line_p in error_block_preview:
                cp = ws.cell(row=curr_h_row, column=1, value="  >> " + sanitize_cell_text(line_p))
                cp.font = Font(name='Consolas', size=10, color='FFC00000', bold=True)
                cp.fill = pink_fill
                curr_h_row += 1
            curr_h_row += 1 # 留空行
    
    actual_log_start = curr_h_row
    
    # --- 步驟 C: 更新 Hyperlink (僅 FAIL) ---
    if error_line_idx is not None and log_type == 'FAIL':
        error_excel_row = actual_log_start + error_line_idx
        ws.cell(row=p_row_jump, column=1).value = f"[ 直接前往錯誤點 (Row {error_excel_row}) ]"
        ws.cell(row=p_row_jump, column=1).hyperlink = f"#'{ws.title}'!A{error_excel_row}"

    # --- 步驟 D: 寫入正式 Log ---
    for i, raw in enumerate(raw_lines):
        row_idx = actual_log_start + i
        line = str(raw)
        anno = anno_lookup.get(i, {})
        
        # 章節標頭 (綠底白字)
        if anno.get('show_separator'):
            title = anno.get('separator_title', 'PHASE')
            sep_cell = ws.cell(row=row_idx, column=1, value=f" --   [ {title} ]")
            sep_cell.font = Font(name='Consolas', size=12, bold=True, color='FFFFFF')
            sep_cell.fill = PatternFill('solid', fgColor='FF2E7D32') 
            sep_cell.alignment = Alignment(horizontal='center')
            continue 

        # 一般日誌行
        cell = ws.cell(row=row_idx, column=1)
        cell.value = sanitize_cell_text(line)
        
        # 取得標註樣式
        txt_color_name = anno.get('color', 'black')
        txt_color = color_map.get(txt_color_name, color_map['black'])
        bg_hex = anno.get('background', 'white')
        is_bold = anno.get('is_bold', False)
        
        # 應用背景 (Excel 需要 'FFxxxxxx' 格式)
        if bg_hex and bg_hex.startswith('#'):
            cell.fill = PatternFill('solid', fgColor='FF' + bg_hex[1:])
        elif bg_hex == 'white':
            pass # 預設白色底
        
        # 應用字體
        cell.font = Font(name='Consolas', size=10, color=txt_color, bold=is_bold)

    # 返回最後一行和錯誤行位置 (供 FAIL_LIST 超鏈接使用)
    last_row = actual_log_start + len(raw_lines)
    return (last_row, error_excel_row if log_type == 'FAIL' else None)

def insert_header_info(ws, header_info, start_row=4):
    """插入置頂 Header 資訊"""
    if not header_info:
        return start_row
        
    lines = header_info.split('\n')
    header_font = Font(name='Consolas', size=14, bold=True, color='000000')
    header_fill = PatternFill('solid', fgColor='90EE90') # 淺綠
    
    for i, line in enumerate(lines):
        cell = ws.cell(row=start_row + i, column=1, value=line)
        cell.font = header_font
        cell.fill = header_fill
        
    return start_row + len(lines) + 1
