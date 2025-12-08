#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復 PASS 匯總工作簿的縮排錯誤 - 第二版
"""

def fix_pass_workbook_indent():
    """修復 excel_writer.py 中 _build_pass_workbook 函數的縮排錯誤"""
    
    # 讀取檔案
    with open('excel_writer.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修復縮排錯誤 - 重新整理整個 for 迴圈
    lines = content.split('\n')
    fixed_lines = []
    
    in_pass_workbook_loop = False
    loop_start = -1
    
    for i, line in enumerate(lines):
        # 找到 for entry in logs: 迴圈
        if 'for entry in logs:' in line and '檔名欄' in lines[i+1] if i+1 < len(lines) else False:
            in_pass_workbook_loop = True
            loop_start = i
            fixed_lines.append(line)
            continue
        
        # 如果在迴圈內，修復縮排
        if in_pass_workbook_loop:
            # 檢查是否離開迴圈（遇到下一個函數或類別）
            if line.strip().startswith('def ') or line.strip().startswith('class ') or (line.strip() and not line.startswith(' ') and not line.startswith('\t')):
                in_pass_workbook_loop = False
                fixed_lines.append(line)
                continue
            
            # 修復迴圈內的縮排
            if line.strip():  # 非空行
                # 確保正確的縮排層級
                if line.startswith('        '):  # 8個空格
                    line = '            ' + line[8:]  # 改為12個空格
                elif line.startswith('    '):  # 4個空格
                    line = '            ' + line[4:]  # 改為12個空格
                elif line.startswith('            '):  # 已經是12個空格
                    pass  # 保持不變
                else:
                    line = '            ' + line  # 添加12個空格
        
        fixed_lines.append(line)
    
    # 寫回檔案
    with open('excel_writer.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print("PASS 匯總工作簿縮排錯誤已修復")

if __name__ == '__main__':
    fix_pass_workbook_indent()
