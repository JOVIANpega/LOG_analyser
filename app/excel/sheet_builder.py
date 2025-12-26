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

def write_raw_log_with_annotations(ws, start_row: int, raw_lines: list, annotations: list, font, fail_items=None):
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
    
    # 優先級偵測錯誤點：DOESN'T MATCH > FAIL/ERROR (從最下面往上找，才是真實報錯位置)
    error_line_idx = None
    dm_pattern = re.compile(r"doesn't match", re.IGNORECASE)
    fe_pattern = re.compile(r"fail|error", re.IGNORECASE)

    # 1. 先找 DOESN'T MATCH (Bottom-up)
    for i in range(len(raw_lines)-1, -1, -1):
        if dm_pattern.search(raw_lines[i]):
            error_line_idx = i
            break
    
    # 2. 如果沒找到，找 FAIL/ERROR (Bottom-up)
    if error_line_idx is None:
        for i in range(len(raw_lines)-1, -1, -1):
            if fe_pattern.search(raw_lines[i]):
                error_line_idx = i
                break
    
    # 3. 擷取錯誤區塊文字 (用於置頂顯示預覽)
    error_block_preview = []
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
    
    # 佔位：如果有的話，寫入提示與預覽
    if error_line_idx is not None:
        # A2 在 excel_writer 中已經被 [回到 Summary] 佔用了？ 
        # 不，excel_writer 呼叫時 start_row=3。
        # A1: [Back to Summary]
        # A2: 空
        # A3: Header Info start
        # 所以 start_row 會由 insert_header_info 回傳。
        pass

    # --- 步驟 B: 寫入預覽區塊 ---
    preview_rows_count = 0
    if error_line_idx is not None:
        # [ 直接前往錯誤點 ]
        jump_cell = ws.cell(row=curr_h_row, column=1, value="[ 發現錯誤點 ] (點擊跳轉至 Log 正確位置)")
        jump_cell.font = Font(name='Calibri', size=11, bold=True, color="FF0000", underline="single")
        # 暫時用佔位符列號，稍後計算 actual_log_start 後再修正 hyperlink
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
    
    # --- 步驟 C: 更新 Hyperlink ---
    if error_line_idx is not None:
        error_excel_row = actual_log_start + error_line_idx
        ws.cell(row=p_row_jump, column=1).value = f"[ 直接前往錯誤點 (Row {error_excel_row}) ]"
        ws.cell(row=p_row_jump, column=1).hyperlink = f"#'{ws.title}'!A{error_excel_row}"

    # --- 步驟 D: 寫入正式 Log ---
    current_bg_color = None
    step_bg_1 = 'FFE8F4FD' 
    step_bg_2 = 'FFF0E8FF' 

    for i, raw in enumerate(raw_lines):
        row_idx = actual_log_start + i
        line = str(raw)
        anno = anno_lookup.get(i, {})
        
        if anno.get('show_separator'):
            title = anno.get('separator_title', 'PHASE')
            sep_cell = ws.cell(row=row_idx, column=1, value=f" --   [ {title} ]")
            sep_cell.font = Font(name='Consolas', size=12, bold=True, color='FFFFFF')
            sep_cell.fill = PatternFill('solid', fgColor='FF2E7D32') 
            sep_cell.alignment = Alignment(horizontal='center')
            continue 

        cell = ws.cell(row=row_idx, column=1)
        cell.value = sanitize_cell_text(line)
        
        txt_color_name = anno.get('color', 'black')
        txt_color = color_map.get(txt_color_name, color_map['black'])
        bg_hex = anno.get('background', 'white')
        is_bold = False
        
        if bg_hex == '#FFCCCC' or txt_color_name == 'red':
            txt_color = color_map['red']
            bg_hex = 'FFFFCCCC'
            is_bold = True
        
        if bg_hex == 'white' or bg_hex is None:
            if 'Do @STEP' in line:
                current_bg_color = step_bg_1 if current_bg_color != step_bg_1 else step_bg_2
            if current_bg_color:
                cell.fill = PatternFill('solid', fgColor=current_bg_color)
        else:
            if bg_hex.startswith('#'):
                cell.fill = PatternFill('solid', fgColor='FF' + bg_hex[1:])
                
        cell.font = Font(name='Consolas', size=10, color=txt_color, bold=is_bold)

    return actual_log_start + len(raw_lines)

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
