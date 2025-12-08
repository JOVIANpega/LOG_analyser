import os
import re
from collections import defaultdict
from pathlib import Path

# 掃描所有 LOG 檔案
log_dir = Path(r"d:\((Python TOOL\4cam_DEBUG_suggestion_tool\LOG")
log_files = list(log_dir.rglob("*.log"))

print(f"找到 {len(log_files)} 個 LOG 檔案")

# 儲存所有錯誤模式
error_patterns = defaultdict(int)

for log_file in log_files:
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # 1. 找 doesn't match 錯誤
        for match in re.finditer(r"doesn't match @([^\r\n]+)", content, re.IGNORECASE):
            context = match.group(1).strip()
            # 簡化：只取前 50 個字元作為關鍵字
            key = context[:50] if len(context) > 50 else context
            error_patterns[f"doesn't match @{key}"] += 1
            
        # 2. 找 ERROR 錯誤
        for match in re.finditer(r'(ERROR[^\r\n]{0,80})', content, re.IGNORECASE):
            msg = match.group(1).strip()
            # 過濾掉包含 PASS 的
            if 'PASS' not in msg.upper():
                error_patterns[msg[:80]] += 1
                
        # 3. 找 FAIL 錯誤
        for match in re.finditer(r'(FAIL[^\r\n]{0,80})', content, re.IGNORECASE):
            msg = match.group(1).strip()
            # 過濾掉包含 PASS 的
            if 'PASS' not in msg.upper() and 'Test is Pass' not in msg:
                error_patterns[msg[:80]] += 1
                
    except Exception as e:
        print(f"處理 {log_file.name} 時出錯: {e}")

# 排序並顯示前 20 個最常見的錯誤
sorted_errors = sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)

print(f"\n找到 {len(sorted_errors)} 種獨特錯誤模式")
print("\n前 20 個最常見的錯誤：")
print("=" * 100)

for i, (error, count) in enumerate(sorted_errors[:20], 1):
    print(f"{i:2d}. [{count:3d}次] {error}")
