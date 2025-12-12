"""
自动化代码重构脚本
将ui_enhanced_fixed.py切割为多个模块
"""
import re
import os

# 读取原始文件
source_file = r"d:\((Python TOOL\解析LOG2\app\ui_enhanced_fixed.py"
with open(source_file, 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

print(f"Total lines: {len(lines)}")
print(f"File size: {len(content)} bytes")

# 找到类的边界
class_pattern = r'^class\s+(\w+)'
classes_found = []
for i, line in enumerate(lines):
    match = re.match(class_pattern, line)
    if match:
        classes_found.append((i+1, match.group(1)))
        print(f"Line {i+1}: class {match.group(1)}")

print(f"\nFound {len(classes_found)} classes")
