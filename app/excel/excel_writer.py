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
from openpyxl.styles import Font, Alignment, PatternFill

# Local imports
from .excel_utils import (
    auto_fit_columns, 
    unique_sheet_name,
    extract_isn_from_filename,
    extract_system_info,
    generate_header_info_text
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
        
        # 0. 先行確定所有工作表名稱，避免 Summary 連結失效
        for entry in logs:
            isn = extract_isn_from_filename(entry.get('file_name', ''))
            sheet_name = unique_sheet_name(wb, isn or "FAIL_Detail")
            entry['sheet_name'] = sheet_name
            # 在 wb 中預佔位置（建立空分頁）
            wb.create_sheet(sheet_name)
        
        # 1. 直接建立統一的 FAIL_LIST (包含 Summary 資訊)
        # 我們將它的建立延後到填寫詳細內容之後，以便取得正確的 error_excel_row
        
        # 2. 建立 FAIL_LIST (在填寫詳細內容之前，先計算錯誤行位置)
        # 註：我們需要先填寫詳細內容，才能得到精確的 error_excel_row
        # 所以這裡先暫存 FAIL_LIST 的建立，等詳細內容填完再建立
        
        # 3. 填寫詳細內容並記錄錯誤行位置
        for entry in logs:
            entry['log_type'] = 'FAIL'  # ⚠️ 確保標註為 FAIL 以觸發預覽框
            sheet_name = entry['sheet_name']
            ws = wb[sheet_name]
            error_row = self._write_detailed_log(ws, entry)
            # 將精確的錯誤行號存回 entry，供 FAIL_LIST 使用
            if error_row:
                entry['error_excel_row'] = error_row
        
        # 現在建立 FAIL_LIST (此時 entry 中已有 error_excel_row)
        self.fail_builder.build_fail_list_sheet(wb, logs)
        
        if "Sheet" in wb.sheetnames:
            del wb["Sheet"]
            
        return safe_save_workbook(wb, output_path)

    def _build_pass_workbook(self, output_path, logs):
        import openpyxl
        wb = openpyxl.Workbook()
        
        # 0. 先行確定所有工作表名稱
        for entry in logs:
            isn = extract_isn_from_filename(entry.get('file_name', ''))
            sheet_name = unique_sheet_name(wb, isn or "PASS_Detail")
            entry['sheet_name'] = sheet_name
            wb.create_sheet(sheet_name)
            
        # 1. 建立 Summary
        sws = self.summary_builder.create_summary_sheet(wb, logs, title="Summary")
        try:
            sws.sheet_properties.tabColor = '0000FF'
        except:
            pass
        
        # 2. 填寫詳細內容
        for entry in logs:
            entry['log_type'] = 'PASS'  # ⚠️ 標註為 PASS
            sheet_name = entry['sheet_name']
            ws = wb[sheet_name]
            self._write_detailed_log(ws, entry)

        if "Sheet" in wb.sheetnames:
            del wb["Sheet"]

        return safe_save_workbook(wb, output_path)

    def _write_detailed_log(self, ws, entry):
        """寫入詳細的 LOG 內容與標註 (同步 GUI 外觀並補回超連結)"""
        
        # 1. 置頂 [回到 Summary/FAIL_LIST] 連結 - Font 16, 深藍底白字
        link_font = Font(name='Calibri', size=16, bold=True, color="FFFFFF", underline="single")
        deep_blue_fill = PatternFill('solid', fgColor='000080')
        
        # 根據日誌類型決定返回目標
        log_type = entry.get('log_type', 'UNKNOWN')
        back_target = 'FAIL_LIST' if log_type == 'FAIL' else 'Summary'
        
        c_top = ws.cell(row=1, column=1, value=f"[回到 {back_target}]")
        c_top.hyperlink = f"#'{back_target}'!A1"
        c_top.font = link_font
        c_top.fill = deep_blue_fill
        c_top.alignment = Alignment(horizontal='center')
        
        # 2. 置頂資訊 (如果沒有預設資訊，則現場生成)
        header_info = entry.get('header_info', '')
        if not header_info:
            header_info = generate_header_info_text(entry)
            
        curr_row = insert_header_info(ws, header_info, start_row=3)
        
        # 3. 原始 LOG (帶有 Premium 背景顏色與文字顏色)
        raw_lines = entry.get('raw_lines', [])
        annotations = entry.get('ui_annotations', [])
        log_type = entry.get('log_type', 'UNKNOWN')  # ⚠️ 關鍵：取得日誌類型
        
        # 根據日誌類型取得對應的項目列表
        if log_type == 'PASS':
            items_to_display = entry.get('pass_items', [])
        else:
            items_to_display = entry.get('fail_items', [])
        
        content_font = Font(name='Consolas', size=11)
        
        # ⚠️ 傳入 log_type 和對應的項目列表
        # ⚠️ 接收返回的錯誤行位置信息
        last_row, error_excel_row = write_raw_log_with_annotations(ws, curr_row, raw_lines, annotations, content_font, fail_items=items_to_display, log_type=log_type)
        
        # 4. 置底 [回到 Summary/FAIL_LIST] 連結 - Font 16, 深藍底白字
        bottom_row = last_row + 2
        c_bot = ws.cell(row=bottom_row, column=1, value=f"[回到 {back_target}]")
        c_bot.hyperlink = f"#'{back_target}'!A1"
        c_bot.font = link_font
        c_bot.fill = deep_blue_fill
        c_bot.alignment = Alignment(horizontal='center')
        
        auto_fit_columns(ws, {1: 130})
        
        # 返回錯誤行位置 (供 FAIL_LIST 超鏈接使用)
        return error_excel_row

    # 向下相容
    def export(self, pass_items, fail_items, output_path):
        pass # 目前主要由 export_pass_fail_workbooks 負責