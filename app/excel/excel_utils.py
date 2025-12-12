# -*- coding: utf-8 -*-
"""
Excel工具函数模块
提供Excel文件处理的通用工具函数
"""
import re
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE

def sanitize_cell_text(value: object) -> str:
    """
    清理欲写入储存格的文字：
    - 转为字串
    - 移除非法控制字元 (openpyxl 限制)
    - 去除 ANSI/ESC 序列
    - 截断过长文字 (3 万字元)
    """
    if value is None:
        return ""
    
    text = str(value)
    
    # 移除 ANSI/ESC 序列
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    text = ansi_escape.sub('', text)
    
    # 移除非法字元
    text = ILLEGAL_CHARACTERS_RE.sub('', text)
    
    # 截断过长文字
    max_len = 30000
    if len(text) > max_len:
        text = text[:max_len] + "...(截断)"
    
    return text


def extract_isn_from_filename(filename: str) -> str:
    """从档名尝试提取 ISN (WE开头 或 纯数字10码以上)"""
    import os
    base_name = os.path.splitext(os.path.basename(filename))[0]
    
    # 尝试匹配 WE 开头的序号
    match = re.search(r'(WE\d{9,})', base_name, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    
    # 尝试匹配纯数字 (10码以上)
    match = re.search(r'(\d{10,})', base_name)
    if match:
        return match.group(1)
    
    return ""


def extract_station_from_filename(filename: str) -> str:
    """
    从档名提取 Station 名称
    规则范例: 1+4cam stitching1 test-1110... -> 4cam stitching1
    去除前面的数字和+号，去除 test- 及其后面所有内容
    """
    import os
    base_name = os.path.splitext(os.path.basename(filename))[0]
    
    # 去除时间戳 (14位数字)
    base_name = re.sub(r'\d{14}', '', base_name)
    
    # 去除 test- 及其后所有内容
    if 'test-' in base_name.lower():
        base_name = re.split(r'test-', base_name, flags=re.IGNORECASE)[0]
    
    # 去除前面的数字+加号 (例如 "1+")
    base_name = re.sub(r'^\d+\+', '', base_name)
    
    # 清理空白
    station = base_name.strip(' _-')
    
    return station if station else "Unknown"


def sanitize_sheet_title(title: str) -> str:
    """
    移除Excel工作表名称不允许的字元并修剪长度。
    禁用字元: : \\ / ? * [ ]，且长度<=31，不可为空。
    """
    if not title:
        return "Sheet"
    
    # 移除禁用字元
    forbidden_chars = [':', '\\', '/', '?', '*', '[', ']']
    for char in forbidden_chars:
        title = title.replace(char, '_')
    
    # 限制长度
    if len(title) > 31:
        title = title[:28] + "..."
    
    return title if title else "Sheet"


def unique_sheet_name(wb, base_name: str) -> str:
    """确保工作表名称不重复"""
    sheet_name = sanitize_sheet_title(base_name)
    existing_names = [sheet.title for sheet in wb.worksheets]
    
    if sheet_name not in existing_names:
        return sheet_name
    
    # 添加数字后缀
    counter = 1
    while True:
        new_name = f"{sheet_name[:27]}_{counter}"
        if new_name not in existing_names:
            return new_name
        counter += 1


def auto_fit_columns(ws, min_widths: dict = None):
    """自动调整栏宽"""
    if min_widths is None:
        min_widths = {}
    
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        
        for cell in column:
            try:
                if cell.value:
                    cell_length = len(str(cell.value))
                    if cell_length > max_length:
                        max_length = cell_length
            except:
                pass
        
        # 设定最小宽度
        min_width = min_widths.get(column_letter, 10)
        adjusted_width = max(min_width, min(max_length + 2, 50))
        ws.column_dimensions[column_letter].width = adjusted_width
