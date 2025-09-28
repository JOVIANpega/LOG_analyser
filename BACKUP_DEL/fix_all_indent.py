#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復 excel_writer.py 中所有的縮排錯誤
"""

def fix_all_indent():
    """修復 excel_writer.py 中所有的縮排錯誤"""
    
    # 讀取檔案
    with open('excel_writer.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修復所有縮排錯誤
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # 修復所有 for entry in logs: 迴圈內的縮排
        if 'for entry in logs:' in line:
            # 找到迴圈開始
            fixed_lines.append(line)
            continue
        
        # 檢查是否在 for entry in logs: 迴圈內
        in_loop = False
        for j in range(max(0, i-50), i):  # 檢查前面50行
            if 'for entry in logs:' in lines[j]:
                # 檢查是否已經離開迴圈
                for k in range(j+1, i):
                    if (lines[k].strip().startswith('def ') or 
                        lines[k].strip().startswith('class ') or 
                        (lines[k].strip() and not lines[k].startswith(' ') and not lines[k].startswith('\t'))):
                        break
                else:
                    in_loop = True
                break
        
        if in_loop and line.strip():
            # 修復迴圈內的縮排
            if line.startswith('                    '):  # 20個空格
                line = '            ' + line[20:]  # 改為12個空格
            elif line.startswith('                '):  # 16個空格
                line = '            ' + line[16:]  # 改為12個空格
            elif line.startswith('            '):  # 12個空格
                pass  # 保持不變
            elif line.startswith('        '):  # 8個空格
                line = '            ' + line[8:]  # 改為12個空格
            elif not line.startswith(' '):  # 沒有縮排
                line = '            ' + line  # 添加12個空格
        
        fixed_lines.append(line)
    
    # 寫回檔案
    with open('excel_writer.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print("所有縮排錯誤已修復")

if __name__ == '__main__':
    fix_all_indent()
