# -*- coding: utf-8 -*-
"""
Sheet Builder Module
Handles detailed log writing and annotation.
"""
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont
from .excel_utils import sanitize_cell_text

def _get_rich_text_for_line(text, keywords, base_font, highlight_color='FF0000'):
    """將特定關鍵字轉換為紅色的 CellRichText"""
    if not text:
        return ""
    
    import re
    # 建立正則表達式，忽略大小寫
    pattern = re.compile(f'({"|".join(map(re.escape, keywords))})', re.IGNORECASE)
    parts = pattern.split(text)
    
    if len(parts) <= 1:
        return text # 沒有關鍵字，回傳純文字節省資源
        
    rich_text_elements = []
    # InlineFont 使用 rFont 而非 name，sz 而非 size
    h_font = InlineFont(rFont=base_font.name, sz=base_font.size, b=True, color=highlight_color)
    d_font = InlineFont(rFont=base_font.name, sz=base_font.size, color=base_font.color.rgb if base_font.color else '000000')
    
    for part in parts:
        if not part: continue
        if pattern.fullmatch(part):
            rich_text_elements.append(TextBlock(h_font, part))
        else:
            rich_text_elements.append(part)
            
    return CellRichText(rich_text_elements)

def write_raw_log_with_annotations(ws, start_row: int, raw_lines: list, annotations: list, font, fail_items=None):
    """將原始 LOG 與顏色標籤寫入 Excel (加強：整區塊變紅)"""
    color_map = {
        'black': 'FF000000',
        'red': 'FFE74C3C',
        'green': 'FF2ECC71',
        'blue': 'FF3498DB',
        'purple': 'FF9B59B6',
    }
    
    error_line_found = False
    first_error_row = None
    
    # 關鍵字清單
    error_keywords = ['error', 'fail', 'doesn\'t', 'failed', 'timeout', 'exception']
    
    # --- 步驟 A: 預先計算「錯誤區塊」範圍 ---
    # 我們定義一個區塊是從 > (下指令) 開始到下一個指令或 @STEP 前
    fail_indices = set()
    
    # 1. 標記所有包含關鍵字的行
    raw_error_idxs = []
    for idx, line in enumerate(raw_lines):
        if any(kw in line.lower() for kw in error_keywords):
            raw_error_idxs.append(idx)
            
    # 2. 擴展到整組指令區塊
    # 如果從 parser 拿到了 fail_items 則優先使用精確範圍
    if fail_items:
        for it in fail_items:
            s, e = it.get('start_idx'), it.get('end_idx')
            if s is not None and e is not None:
                for i in range(s, e + 1):
                    fail_indices.add(i)
    else:
        # 自行偵測語境下的區塊
        for err_idx in raw_error_idxs:
            # 往上找指令開始 (>)
            block_start = err_idx
            for i in range(err_idx, max(0, err_idx - 50), -1):
                if '>' in raw_lines[i] or '@STEP' in raw_lines[i]:
                    block_start = i
                    break
            # 往下找直到結束或下一指令
            block_end = err_idx
            for i in range(err_idx, min(len(raw_lines), err_idx + 30)):
                if 'All Test Aborted' in raw_lines[i] or 'executes fail' in raw_lines[i] or 'root@' in raw_lines[i]:
                    block_end = i
                    break
                elif i > err_idx and ('>' in raw_lines[i] or '@STEP' in raw_lines[i]):
                    block_end = i - 1
                    break
                block_end = i
            
            for i in range(block_start, block_end + 1):
                fail_indices.add(i)

    # --- 步驟 B: 寫入 Excel ---
    for i, raw in enumerate(raw_lines, start=start_row):
        src_idx = i - start_row
        line = str(raw)
        
        # 標題及標註內容
        found_anno = None
        for anno in annotations:
            if anno.get('line_idx') == src_idx:
                found_anno = anno
                break
        
        # 樣式決策
        bg_color = None
        font_color = color_map['black']
        is_bold = False
        
        # 1. 區塊紅字邏輯 (使用者要求：整區塊變紅)
        is_in_fail_block = src_idx in fail_indices
        if is_in_fail_block:
            font_color = 'FFFF0000' # 紅色
            is_bold = True
            
            # 如果這行本身就是錯誤點，給點背景色
            if any(kw in line.lower() for kw in error_keywords):
                bg_color = 'FFFFFF00' # 正黃色加強
                if not error_line_found:
                    first_error_row = i
                    error_line_found = True
        
        # 2. 標籤覆蓋
        if found_anno:
            # 只有在不是失敗區塊的情況下才由標籤決定顏色，或是保留標籤顏色
            if not is_in_fail_block:
                c_name = found_anno.get('color')
                if c_name in color_map: font_color = color_map[c_name]
            
            target_bg = found_anno.get('background')
            if target_bg and target_bg.startswith('#'):
                bg_color = 'FF' + target_bg[1:]
        
        # 3. 寫入儲存格
        clean_line = sanitize_cell_text(line)
        cell = ws.cell(row=i, column=1)
        
        # --- 思考：特殊文字顯示紅色 (Rich Text) ---
        # 如果整行已經是紅色了，Rich Text 就沒意義。
        # 但如果整行是黑色，我們想讓 keyword 變紅：
        if not is_in_fail_block and any(kw in line.lower() for kw in error_keywords):
            # 針對 PASS log 中零星出現的關鍵字，只讓字變紅
            cell.value = _get_rich_text_for_line(clean_line, error_keywords, font)
        else:
            cell.value = clean_line

        # 套用儲存格樣式
        cell.font = Font(name=font.name, size=font.size, color=font_color, bold=is_bold)
        if bg_color:
            cell.fill = PatternFill('solid', fgColor=bg_color)
            
    if first_error_row:
        ws.cell(row=1, column=1).value = f"Jump to Error (A{first_error_row})"
        ws.cell(row=1, column=1).hyperlink = f"#'{ws.title}'!A{first_error_row}"
        ws.cell(row=1, column=1).font = Font(color="0000FF", underline="single")

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
