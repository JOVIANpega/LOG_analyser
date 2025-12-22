# -*- coding: utf-8 -*-
"""
Summary Builder Module
Handles creation of Summary and Data sheets for both PASS and FAIL workbooks.
"""
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from .excel_utils import (
    sanitize_cell_text,
    extract_isn_from_filename,
    extract_station_from_filename,
    format_filename_with_timestamp,
    auto_fit_columns
)

class SummaryBuilder:
    """構建 Excel 匯總頁面 (Summary/Data)"""

    def __init__(self):
        self.header_font = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
        self.content_font = Font(name='Calibri', size=11)
        self.fill_blue = PatternFill('solid', fgColor='4472C4')
        self.center_align = Alignment(horizontal='center', vertical='center')
        self.left_top_align = Alignment(horizontal='left', vertical='top', wrap_text=True)

    def create_summary_sheet(self, wb, logs, title="Summary"):
        """建立匯總頁面"""
        ws = wb.create_sheet(title, 0)
        
        # 標題
        headers = ["測試記錄 (合併資訊)", "狀態", "操作", "工作表連結"]
        for col, h in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=h)
            cell.font = self.header_font
            cell.fill = self.fill_blue
            cell.alignment = self.center_align
            
        for row, entry in enumerate(logs, 2):
            fname = entry.get('file_name', entry.get('filename', ''))
            isn = extract_isn_from_filename(fname)
            station = extract_station_from_filename(fname)
            
            # 合併資訊 (由使用者要求的格式)
            system = entry.get('system_info', {})
            info = [
                f"File: {fname}",
                f"ISN: {isn}",
                f"Station: {station}"
            ]
            if system.get('Script'): info.append(f"Script: {system['Script']}")
            if system.get('SFIS'): info.append(f"SFIS: {system['SFIS']}")
            
            test_time = "Unknown"
            if 'raw_lines' in entry:
                from .excel_utils import extract_total_secs
                secs, _ = extract_total_secs(entry['raw_lines'])
                if secs: test_time = f"{secs:.2f} Sec"
            info.append(f"Time: {test_time}")
            
            # 寫入第一欄 (合併資訊)
            cell_info = ws.cell(row=row, column=1, value="\n".join(info))
            cell_info.alignment = self.left_top_align
            cell_info.font = self.content_font
            
            # 寫入狀態
            status = "PASS" if not entry.get('fail_items') else "FAIL"
            cell_status = ws.cell(row=row, column=2, value=status)
            cell_status.alignment = self.center_align
            if status == "FAIL":
                cell_status.font = Font(color="FF0000", bold=True)
            
            # 工作表格式化名稱
            sheet_name = entry.get('sheet_name', isn or fname[:25])
            
            # 連結
            cell_link = ws.cell(row=row, column=4, value=f"查看 {sheet_name}")
            cell_link.hyperlink = f"#'{sheet_name}'!A1"
            cell_link.font = Font(color="0000FF", underline="single")
            
        auto_fit_columns(ws, {1: 60, 2: 10, 3: 15, 4: 25})
        return ws
