#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試Log分析器功能
"""

import os
from log_analyzer import LogAnalyzer

def test_analyzer():
    """測試分析器功能"""
    print("開始測試Log分析器...")
    
    # 建立分析器實例
    analyzer = LogAnalyzer()
    
    # 測試載入log檔案
    log_file = "MINE/LOG/1+Funtion-WE33-20250708141022-PASS.log"
    
    if os.path.exists(log_file):
        print(f"載入log檔案: {log_file}")
        success = analyzer.load_log_file(log_file)
        
        if success:
            print("✅ Log檔案載入成功")
            
            # 解析測試步驟
            print("開始解析測試步驟...")
            pass_tests, fail_tests = analyzer.parse_test_steps()
            
            print(f"✅ 解析完成:")
            print(f"   - PASS測試: {len(pass_tests)} 項")
            print(f"   - FAIL測試: {len(fail_tests)} 項")
            
            # 顯示前幾個PASS測試
            if pass_tests:
                print("\n前3個PASS測試:")
                for i, test in enumerate(pass_tests[:3]):
                    print(f"  {i+1}. {test['step_name']} ({test['test_id']}) - {test['execution_time']:.3f}秒")
            
            # 顯示前幾個FAIL測試
            if fail_tests:
                print("\n前3個FAIL測試:")
                for i, test in enumerate(fail_tests[:3]):
                    print(f"  {i+1}. {test['step_name']} ({test['test_id']}) - {test['error_message']}")
            
            # 測試Excel匯出
            print("\n測試Excel匯出...")
            export_success = analyzer.export_to_excel("test_output.xlsx")
            if export_success:
                print("✅ Excel匯出成功: test_output.xlsx")
            else:
                print("❌ Excel匯出失敗")
                
        else:
            print("❌ Log檔案載入失敗")
    else:
        print(f"❌ Log檔案不存在: {log_file}")
    
    print("\n測試完成!")

if __name__ == "__main__":
    test_analyzer() 