#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復 excel_writer.py 中所有的縮排錯誤 - 第三十二版
"""

def fix_excel_indent():
    """修復 excel_writer.py 中所有的縮排錯誤"""
    
    # 讀取檔案
    with open('excel_writer.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修復所有縮排錯誤
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # 修復第244-248行的縮排錯誤
        if i >= 243 and i <= 247:  # 行號從0開始
            if line.strip() and not line.startswith('            '):
                line = '            ' + line.strip()  # 添加12個空格
        
        # 修復第249-252行的縮排錯誤
        elif i >= 248 and i <= 251:
            if line.strip() and not line.startswith('        '):
                line = '        ' + line.strip()  # 添加8個空格
        
        fixed_lines.append(line)
    
    # 寫回檔案
    with open('excel_writer.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print("Excel 縮排錯誤已修復")

if __name__ == '__main__':
    fix_excel_indent()
