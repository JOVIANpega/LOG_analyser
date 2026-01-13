import re

class MockLogParser:
    def __init__(self):
        self.step_pattern = re.compile(r'Do\s+(@STEP\d+@[^@\n]+)')
        
    def _is_step_end_line(self, line, step_number):
        if not step_number:
            return False
        # 原本的邏輯
        end_pattern = re.compile(rf'@{step_number}@.*Test is Pass !', re.IGNORECASE)
        print(f"Testing line: '{line.strip()}' against pattern '{end_pattern.pattern}'")
        match = end_pattern.search(line)
        print(f"Match result: {match is not None}")
        return match is not None

parser = MockLogParser()

# 模擬情況
lines_to_test = [
    "2025/08/07 09:12:35 [1]	B7PL025-098:@STEP044@Check Charging Test is Pass ! 		----- 16.0633436 Sec.",
    "B7PL025-018:@STEP013@Check Valo360 model Test is Pass !     ----- 0 Sec.", 
    "2025/08/07 09:10:02 [1] B7PL025-018:@STEP013@Check Valo360 model Test is Pass !      ----- 0 Sec."
]

step_numbers = ["STEP044", "STEP013", "STEP013"]

print("--- Testing End Line Detection ---")
for line, step_num in zip(lines_to_test, step_numbers):
    parser._is_step_end_line(line, step_num)

print("\n--- Testing Step Extraction ---")
start_line = "2025/08/07 09:12:19 [1] Do @STEP044@Check Charging"
match = parser.step_pattern.search(start_line)
if match:
    full_str = match.group(1)
    print(f"Captured: '{full_str}'")
    parts = full_str.split('@')
    print(f"Parts: {parts}")
    if len(parts) >= 2:
        print(f"Extracted Step Number: '{parts[1]}'")
else:
    print("No match for start line")
