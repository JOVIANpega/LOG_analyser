"""
提取EnhancedText和FailDetailsPanel类的脚本
"""
import os

# 读取原始文件
source_file = r"d:\((Python TOOL\解析LOG2\app\ui_enhanced_fixed.py"
with open(source_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines read: {len(lines)}")

# 提取 EnhancedText 类 (行1695-2064, 索引1694-2063)
enhanced_text_header = [
    '# -*- coding: utf-8 -*-\n',
    '"""\n',
    'EnhancedText组件 - 增强型Text元件\n',
    '支援语法高亮和区段标签\n',
    '"""\n',
    'import tkinter as tk\n',
    'from tkinter import messagebox\n',
    'import re\n',
    '\n'
]
enhanced_text_lines = enhanced_text_header + lines[1694:2064]

output_file1 = r"d:\((Python TOOL\解析LOG2\app\ui\enhanced_text.py"
with open(output_file1, 'w', encoding='utf-8') as f:
    f.writelines(enhanced_text_lines)
print(f"EnhancedText extracted to: {output_file1}")
print(f"Lines written: {len(enhanced_text_lines)}")

# 提取 FailDetailsPanel 类 (行2065-2097, 索引2064-2096)
fail_panel_header = [
    '# -*- coding: utf-8 -*-\n',
    '"""\n',
    'FailDetailsPanel组件 - FAIL详细资讯面板\n',
    '"""\n',
    'import tkinter as tk\n',
    '\n'
]
fail_panel_lines = fail_panel_header + lines[2064:2097]

output_file2 = r"d:\((Python TOOL\解析LOG2\app\ui\fail_details_panel.py"
with open(output_file2, 'w', encoding='utf-8') as f:
    f.writelines(fail_panel_lines)
print(f"FailDetailsPanel extracted to: {output_file2}")
print(f"Lines written: {len(fail_panel_lines)}")

print("\nExtraction completed successfully!")
