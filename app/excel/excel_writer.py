# -*- coding: utf-8 -*-
"""
ExcelWriter Main Module (Modularized)
Coordinates the creation of PASS and FAIL workbooks.
"""
from __future__ import annotations
import os
import time
import traceback
from datetime import datetime
from openpyxl.styles import Font, Alignment

# Local imports
from .excel_utils import (
    auto_fit_columns, 
    unique_sheet_name,
    extract_isn_from_filename,
    extract_system_info
)
from .excel_fail_list_builder import FailListBuilder
from .excel_summary_builder import SummaryBuilder
from .sheet_builder import write_raw_log_with_annotations, insert_header_info

def safe_save_workbook(wb, output_path):
    """安全保存工作簿，處理權限錯誤"""
    try:
        wb.save(output_path)
    except PermissionError:
        ts = datetime.now().strftime("%H%M%S")
        name, ext = os.path.splitext(output_path)
        new_path = f"{name}_{ts}{ext}"
        wb.save(new_path)
        return new_path
    return output_path

class ExcelWriter:
    """Excel 匯出核心類別 (座標員)"""
    
    def __init__(self):
        self.fail_builder = FailListBuilder()
        self.summary_builder = SummaryBuilder()

    def _extract_total_secs(self, raw_lines: list):
        """便利方法：調用工具函數提取秒數"""
        from .excel_utils import extract_total_secs
        return extract_total_secs(raw_lines)

    def _extract_isn_from_filename(self, filename: str):
         """便利方法：調用工具函數提取 ISN"""
         from .excel_utils import extract_isn_from_filename
         return extract_isn_from_filename(filename)

    def export_pass_fail_workbooks(self, folder_path: str, pass_logs: list, fail_logs: list):
        """
        輸出兩個活頁簿
        """
        # 1. 處理 FAIL 活頁簿
        fail_path = os.path.join(folder_path, "FAIL匯總.xlsx")
        fail_saved_path = self._build_fail_workbook(fail_path, fail_logs)
        
        # 2. 處理 PASS 活頁簿
        pass_path = os.path.join(folder_path, "PASS匯總.xlsx")
        pass_saved_path = self._build_pass_workbook(pass_path, pass_logs)
        
        return pass_saved_path, fail_saved_path, None

    def _build_fail_workbook(self, output_path, logs):
        import openpyxl
        wb = openpyxl.Workbook()
        
        # 1. 建立 Summary (使用者要求回復)
        self.summary_builder.create_summary_sheet(wb, logs, title="Summary")
        
        # 2. 建立 FAIL_LIST
        self.fail_builder.build_fail_list_sheet(wb, logs)
        
        # 2. 建立每個檔案的詳細頁面
        for entry in logs:
            isn = extract_isn_from_filename(entry.get('file_name', ''))
            sheet_name = unique_sheet_name(wb, isn or "FAIL_Detail")
            entry['sheet_name'] = sheet_name
            ws = wb.create_sheet(sheet_name)
            self._write_detailed_log(ws, entry)
        
        if "Sheet" in wb.sheetnames:
            del wb["Sheet"]
            
        return safe_save_workbook(wb, output_path)

    def _build_pass_workbook(self, output_path, logs):
        import openpyxl
        wb = openpyxl.Workbook()
        
        # 1. 建立 Summary
        self.summary_builder.create_summary_sheet(wb, logs, title="Summary")
        
        # 2. 建立每個檔案的頁面
        for entry in logs:
            isn = extract_isn_from_filename(entry.get('file_name', ''))
            sheet_name = unique_sheet_name(wb, isn or "PASS_Detail")
            entry['sheet_name'] = sheet_name
            ws = wb.create_sheet(sheet_name)
            self._write_detailed_log(ws, entry)

        if "Sheet" in wb.sheetnames:
            del wb["Sheet"]

        return safe_save_workbook(wb, output_path)

    def _write_detailed_log(self, ws, entry):
        """寫入詳細的 LOG 內容與標註 (維持 Premium 外觀)"""
        # 1. 回到 Summary 連結
        ws.cell(row=1, column=2, value="[回到 Summary]").hyperlink = f"#'Summary'!A1"
        ws.cell(row=1, column=2).font = Font(color="0000FF", underline="single")
        
        # 2. 置頂資訊
        header_info = entry.get('header_info', '')
        curr_row = insert_header_info(ws, header_info, start_row=4)
        
        # 3. 原始 LOG
        raw_lines = entry.get('raw_lines', [])
        annotations = entry.get('ui_annotations', [])
        content_font = Font(name='Consolas', size=10)
        
        write_raw_log_with_annotations(ws, curr_row, raw_lines, annotations, content_font)
        
        auto_fit_columns(ws, {1: 100})

    # 向下相容
    def export(self, pass_items, fail_items, output_path):
        pass # 目前主要由 export_pass_fail_workbooks 負責