
import sys
import os
import pprint

# Add current directory to path so we can import modules
sys.path.append(os.getcwd())

from log_parser import LogParser

def create_dummy_log(filename, content):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def test_parser():
    parser = LogParser()
    
    # Test Case 1: PASS Log
    pass_log_content = """
Do @STEP1@ Check Version
(LAN) > ver
(LAN) < 1.0.0
@STEP1@ Test is Pass !
Do @STEP2@ Check Status
(LAN) > status
(LAN) < OK
@STEP2@ Test is Pass !
"""
    create_dummy_log("test_pass.log", pass_log_content)
    print("--- Testing PASS Log ---")
    try:
        result = parser.parse_log_file("test_pass.log")
        print("PASS Items:")
        pprint.pprint(result['pass_items'])
        print("\nFAIL Items:")
        pprint.pprint(result['fail_items'])
    except Exception as e:
        print(f"Error parsing PASS log: {e}")

    # Test Case 2: FAIL Log
    fail_log_content = """
Do @STEP1@ Check Version
(LAN) > ver
(LAN) < 1.0.0
@STEP1@ Test is Pass !
Do @STEP2@ Check Status
(LAN) > status
(LAN) < ERROR
@STEP2@ Test is Fail !
"""
    create_dummy_log("test_fail.log", fail_log_content)
    print("\n--- Testing FAIL Log ---")
    try:
        result = parser.parse_log_file("test_fail.log")
        print("PASS Items:")
        pprint.pprint(result['pass_items'])
        print("\nFAIL Items:")
        pprint.pprint(result['fail_items'])
        
        # Verify keys for UI
        if result['fail_items']:
            item = result['fail_items'][0]
            required_keys = ['step_name', 'command', 'response', 'retry', 'error']
            missing_keys = [k for k in required_keys if k not in item]
            if missing_keys:
                print(f"CRITICAL: Missing keys in fail_item: {missing_keys}")
            else:
                print("All required keys present in fail_item.")
                
    except Exception as e:
        print(f"Error parsing FAIL log: {e}")

if __name__ == "__main__":
    test_parser()
