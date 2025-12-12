"""
提取EnhancedTreeview类的脚本
"""
import os

# 读取原始文件
source_file = r"d:\((Python TOOL\解析LOG2\app\ui_enhanced_fixed.py"
with open(source_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines read: {len(lines)}")

# 提取文件头部 (行1-6, 索引0-5)
header_lines = lines[0:6]

# 提取 EnhancedTreeview 类 (行7-1694, 索引6-1693)
enhanced_treeview_lines = header_lines + lines[6:1694]

output_file = r"d:\((Python TOOL\解析LOG2\app\ui\enhanced_treeview.py"
with open(output_file, 'w', encoding='utf-8') as f:
    f.writelines(enhanced_treeview_lines)
print(f"EnhancedTreeview extracted to: {output_file}")
print(f"Lines written: {len(enhanced_treeview_lines)}")

print("\nEnhancedTreeview extraction completed!")
