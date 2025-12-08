#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
詳細測試Log分析器功能
"""

import os
import pandas as pd
from log_analyzer import LogAnalyzer

def detailed_test():
    """詳細測試分析器功能"""
    print("=== 詳細測試Log分析器 ===")
    
    # 建立分析器實例
    analyzer = LogAnalyzer()
    
    # 測試載入log檔案
    log_file = "MINE/LOG/1+Funtion-WE33-20250708141022-PASS.log"
    
    if not os.path.exists(log_file):
        print(f"❌ Log檔案不存在: {log_file}")
        return
    
    print(f"📁 載入log檔案: {log_file}")
    success = analyzer.load_log_file(log_file)
    
    if not success:
        print("❌ Log檔案載入失敗")
        return
    
    print("✅ Log檔案載入成功")
    
    # 解析測試步驟
    print("\n🔍 開始解析測試步驟...")
    pass_tests, fail_tests = analyzer.parse_test_steps()
    
    print(f"✅ 解析完成:")
    print(f"   📊 PASS測試: {len(pass_tests)} 項")
    print(f"   📊 FAIL測試: {len(fail_tests)} 項")
    
    # 詳細分析PASS測試
    if pass_tests:
        print(f"\n📋 PASS測試詳細分析 (顯示前5項):")
        for i, test in enumerate(pass_tests[:5]):
            print(f"  {i+1}. {test['step_name']}")
            print(f"     測試ID: {test['test_id']}")
            print(f"     執行時間: {test['execution_time']:.3f}秒")
            print(f"     指令數量: {len(test['commands'])}")
            print(f"     回應數量: {len(test['responses'])}")
            if test['commands']:
                print(f"     範例指令: {test['commands'][0]}")
            if test['responses']:
                print(f"     範例回應: {test['responses'][0]}")
            print()
    
    # 詳細分析FAIL測試
    if fail_tests:
        print(f"\n📋 FAIL測試詳細分析 (顯示前5項):")
        for i, test in enumerate(fail_tests[:5]):
            print(f"  {i+1}. {test['step_name']}")
            print(f"     測試ID: {test['test_id']}")
            print(f"     重試次數: {test['retry_count']}")
            print(f"     執行時間: {test['execution_time']:.3f}秒")
            print(f"     錯誤訊息: {test['error_message']}")
            print()
    
    # 統計分析
    total_tests = len(pass_tests) + len(fail_tests)
    if total_tests > 0:
        pass_rate = len(pass_tests) / total_tests * 100
        print(f"\n📈 統計分析:")
        print(f"   總測試數: {total_tests}")
        print(f"   通過數: {len(pass_tests)}")
        print(f"   失敗數: {len(fail_tests)}")
        print(f"   成功率: {pass_rate:.1f}%")
        
        # 計算平均執行時間
        if pass_tests:
            avg_pass_time = sum(test['execution_time'] for test in pass_tests) / len(pass_tests)
            print(f"   平均PASS時間: {avg_pass_time:.3f}秒")
        
        if fail_tests:
            avg_fail_time = sum(test['execution_time'] for test in fail_tests) / len(fail_tests)
            print(f"   平均FAIL時間: {avg_fail_time:.3f}秒")
    
    # 測試Excel匯出
    print(f"\n💾 測試Excel匯出...")
    output_file = "detailed_test_output.xlsx"
    export_success = analyzer.export_to_excel(output_file)
    
    if export_success:
        print(f"✅ Excel匯出成功: {output_file}")
        
        # 驗證Excel檔案內容
        try:
            with pd.ExcelFile(output_file) as xls:
                sheets = xls.sheet_names
                print(f"📊 Excel工作表: {sheets}")
                
                # 讀取PASS測試工作表
                if 'PASS測試' in sheets:
                    pass_df = pd.read_excel(output_file, sheet_name='PASS測試')
                    print(f"   PASS測試工作表: {len(pass_df)} 行")
                
                # 讀取FAIL測試工作表
                if 'FAIL測試' in sheets:
                    fail_df = pd.read_excel(output_file, sheet_name='FAIL測試')
                    print(f"   FAIL測試工作表: {len(fail_df)} 行")
                
                # 讀取統計摘要工作表
                if '統計摘要' in sheets:
                    summary_df = pd.read_excel(output_file, sheet_name='統計摘要')
                    print(f"   統計摘要工作表: {len(summary_df)} 行")
                    
        except Exception as e:
            print(f"❌ Excel檔案驗證失敗: {e}")
    else:
        print("❌ Excel匯出失敗")
    
    print("\n✅ 詳細測試完成!")

if __name__ == "__main__":
    detailed_test() 