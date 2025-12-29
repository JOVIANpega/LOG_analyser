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
        # 優先級偵測錯誤點 (從最下面往上找)
        dm_pattern = re.compile(r"doesn't match", re.IGNORECASE)
        is_fail_pattern = re.compile(r"is Fail", re.IGNORECASE)
        abort_pattern = re.compile(r"All Test Aborted", re.IGNORECASE)
        status_pattern = re.compile(r"Status:False", re.IGNORECASE)
        fail_pattern = re.compile(r"FAIL", re.IGNORECASE)
        error_pattern = re.compile(r"ERROR", re.IGNORECASE)
    
        # 1. 最高優先級：DOESN'T MATCH
        for i in range(len(raw_lines)-1, -1, -1):
            if dm_pattern.search(raw_lines[i]):
                error_line_idx = i
                break
        
        # 2. 次優先級：is Fail / All Test Aborted
        if error_line_idx is None:
            for i in range(len(raw_lines)-1, -1, -1):
                cur_line = raw_lines[i]
                if is_fail_pattern.search(cur_line) or abort_pattern.search(cur_line):
                    error_line_idx = i
                    break
        
        # 3. 第三優先級：Status:False
        if error_line_idx is None:
            for i in range(len(raw_lines)-1, -1, -1):
                if status_pattern.search(raw_lines[i]):
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

    # --- 步驟 A: 預先計算預覽區塊高度以利超連結定位 ---
    preview_box_height = 0
    if error_line_idx is not None and log_type == 'FAIL':
        # 標題行(1) + 內容行(len) + 跳轉按鈕(1) + 間隔行(1)
        preview_box_height = 1 + len(error_block_preview) + 1 + 1
    
    actual_log_start = start_row + preview_box_height
    curr_h_row = start_row

    # --- 步驟 B: 僅對 FAIL 日誌寫入預覽區塊 (Premium Box) ---
    if error_line_idx is not None and log_type == 'FAIL':
        # 1. 標題行
        title_font = Font(name='Microsoft JhengHei', size=12, bold=True, color='FFFFFF')
        title_fill = PatternFill('solid', fgColor='FFFF0000') # 純紅標題
        title_cell = ws.cell(row=curr_h_row, column=1, value="  [ 發現錯誤點 (預覽) ]  ")
        title_cell.font = title_font
        title_cell.fill = title_fill
        title_cell.alignment = Alignment(horizontal='center', vertical='center')
        curr_h_row += 1
        
        # 2. 錯誤內容 (每行皆可點擊跳轉)
        # 使用剛才擷取預覽塊時的 b_start 作為索引基底
        pink_fill = PatternFill('solid', fgColor='FFFFE1E1')
        red_font = Font(name='Consolas', size=11, color='FFC00000', bold=True)
        
        if error_block_preview:
            for i, line_p in enumerate(error_block_preview):
                target_log_idx = b_start + i
                target_excel_row = actual_log_start + target_log_idx
                
                cp = ws.cell(row=curr_h_row, column=1, value="  >> " + sanitize_cell_text(line_p))
                cp.font = red_font
                cp.fill = pink_fill
                
                # 建立超連結跳轉到下方對應位置
                cp.hyperlink = f"#'{ws.title}'!A{target_excel_row}"
                cp.tooltip = f"點擊跳轉到第 {target_log_idx + 1} 行"
                curr_h_row += 1
        
        # 3. 底部跳轉按鈕 (整塊 Box 的結尾)
        target_err_row = actual_log_start + error_line_idx
        jump_cell = ws.cell(row=curr_h_row, column=1, value=f" [ 🚀 直接跳轉至錯誤行 Row {target_err_row} ] ")
        jump_cell.font = Font(name='Microsoft JhengHei', size=11, bold=True, color="FF0000BB", underline="single")
        jump_cell.fill = pink_fill
        jump_cell.alignment = Alignment(horizontal='center')
        jump_cell.hyperlink = f"#'{ws.title}'!A{target_err_row}"
        
        curr_h_row += 2 # 留空行

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
