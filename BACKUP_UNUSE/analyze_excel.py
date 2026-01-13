"""
分析并提取excel_writer.py的脚本
"""
import re

source_file = r"d:\((Python TOOL\解析LOG2\app\excel_writer.py"
with open(source_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    content = ''.join(lines)

print(f"Total lines: {len(lines)}")

# 分析方法分组
# 工具方法: _sanitize_*, _extract_*, _unique_*, _format_*
# PASS构建: _build_pass_*
# FAIL构建: _build_fail_*
# 主方法: export*, _safe_save_*

utility_methods = []
pass_methods = []
fail_methods = []
main_methods = []

for i, line in enumerate(lines):
    match = re.match(r'^\s{4}def\s+(\w+)', line)
    if match:
        method_name = match.group(1)
        if any(prefix in method_name for prefix in ['_sanitize', '_extract', '_unique', '_format', '_auto_fit']):
            utility_methods.append((i+1, method_name))
        elif '_build_pass' in method_name or method_name == '_build_pass_workbook':
            pass_methods.append((i+1, method_name))
        elif '_build_fail' in method_name or method_name == '_build_fail_workbook':
            fail_methods.append((i+1, method_name))
        else:
            main_methods.append((i+1, method_name))

print(f"\n工具方法 ({len(utility_methods)}):")
for line_num, method in utility_methods:
    print(f"  Line {line_num}: {method}")

print(f"\nPASS构建方法 ({len(pass_methods)}):")
for line_num, method in pass_methods:
    print(f"  Line {line_num}: {method}")

print(f"\nFAIL构建方法 ({len(fail_methods)}):")
for line_num, method in fail_methods:
    print(f"  Line {line_num}: {method}")

print(f"\n主方法 ({len(main_methods)}):")
for line_num, method in main_methods:
    print(f"  Line {line_num}: {method}")
