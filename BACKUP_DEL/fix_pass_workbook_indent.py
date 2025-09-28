#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復 PASS 匯總工作簿的縮排錯誤
"""

def fix_pass_workbook_indent():
    """修復 excel_writer.py 中 _build_pass_workbook 函數的縮排錯誤"""
    
    # 讀取檔案
    with open('excel_writer.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修復縮排錯誤
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # 修復第256行附近的縮排錯誤
        if i >= 255 and i <= 265:  # 行號從0開始，所以255對應第256行
            # 移除多餘的縮排
            if line.startswith('                '):
                line = line[4:]  # 移除4個空格
            elif line.startswith('            '):
                line = line[4:]  # 移除4個空格
        
        fixed_lines.append(line)
    
    # 寫回檔案
    with open('excel_writer.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print("PASS 匯總工作簿縮排錯誤已修復")

if __name__ == '__main__':
    fix_pass_workbook_indent()
