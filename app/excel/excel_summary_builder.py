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
    generate_header_info_text,
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
            
        # 變更連結文字：從 "查看 {sheet_name}" 改為 "查看LOG {sheet_name}"
        # 並收集所有時間與檔名用於最後的圖表顯示
        time_data = [] # List of (filename, seconds)
        
        for row, entry in enumerate(logs, 2):
            fname = entry.get('file_name', entry.get('filename', ''))
            # 合併資訊
            info_str = generate_header_info_text(entry)
            
            # 寫入第一欄 (合併資訊)
            cell_info = ws.cell(row=row, column=1, value=info_str)
            cell_info.alignment = self.left_top_align
            cell_info.font = self.content_font
            
            # 收集數據用於圖表
            fname = entry.get('file_name', entry.get('filename', ''))
            isn = extract_isn_from_filename(fname)
            from .excel_utils import extract_total_secs
            test_secs, _ = extract_total_secs(entry.get('raw_lines', []))
            if test_secs:
                label = isn if isn else fname[:15]
                time_data.append((label, test_secs))
            
            # 寫入狀態
            status = "PASS" if not entry.get('fail_items') else "FAIL"
            cell_status = ws.cell(row=row, column=2, value=status)
            cell_status.alignment = self.center_align
            if status == "FAIL":
                cell_status.font = Font(color="FF0000", bold=True)
            
            # 工作表格式化名稱
            sheet_name = entry.get('sheet_name', isn or fname[:25])
            
            # 連結 (變更文字)
            cell_link = ws.cell(row=row, column=4, value=f"查看LOG {sheet_name}")
            cell_link.hyperlink = f"#'{sheet_name}'!A1"
            cell_link.font = Font(color="0000FF", underline="single")
            
        auto_fit_columns(ws, {1: 60, 2: 10, 3: 15, 4: 25})
        
        # 新增測試時間分佈圖 (取代原本的總數統計)
        if time_data:
            self._add_time_distribution_chart(ws, time_data)
            
        return ws

    def _add_time_distribution_chart(self, ws, time_data):
        """新增測試時間分佈圖 (點圖/Dot Map)"""
        try:
            from openpyxl.chart import LineChart, Reference, Series
            from openpyxl.drawing.fill import SolidFillProperties
            
            start_row = ws.max_row + 3
            
            # 1. 寫入統計匯總表格
            ws.cell(row=start_row, column=1, value=" 📊 測試時間分佈統計 ").font = Font(name='Arial', size=12, bold=True, color='FFFFFF')
            ws.cell(row=start_row, column=1).fill = PatternFill('solid', fgColor='2E7D32')
            
            stats_data = [
                ("總分析數量", f"{len(time_data)} 筆"),
                ("平均測試時間", f"{sum(d[1] for d in time_data) / len(time_data):.2f} Sec"),
                ("最長測試時間", f"{max(d[1] for d in time_data):.2f} Sec"),
                ("最短測試時間", f"{min(d[1] for d in time_data):.2f} Sec"),
            ]
            
            for i, (k, v) in enumerate(stats_data):
                ws.cell(row=start_row + 1 + i, column=1, value=k).font = Font(bold=True)
                ws.cell(row=start_row + 1 + i, column=2, value=v)
                
            # 2. 寫入原始數據表 (用於圖表引用)
            data_header_row = start_row + len(stats_data) + 2
            ws.cell(row=data_header_row, column=1, value=" ID / ISN ").font = self.header_font
            ws.cell(row=data_header_row, column=1).fill = self.fill_blue
            ws.cell(row=data_header_row, column=2, value=" 時間 (Sec) ").font = self.header_font
            ws.cell(row=data_header_row, column=2).fill = self.fill_blue
            
            data_start = data_header_row + 1
            for i, (label, val) in enumerate(time_data):
                ws.cell(row=data_start + i, column=1, value=label)
                ws.cell(row=data_start + i, column=2, value=val)
            
            # 3. 建立點圖 (使用 LineChart 但隱藏線條)
            chart = LineChart()
            chart.title = "測試時間分佈點圖 (Time Dot Map)"
            chart.style = 13
            chart.y_axis.title = "秒數 (Sec)"
            chart.x_axis.title = "測試項"
            
            # 數據引用
            data_ref = Reference(ws, min_col=2, min_row=data_start, max_row=data_start + len(time_data) - 1)
            cats_ref = Reference(ws, min_col=1, min_row=data_start, max_row=data_start + len(time_data) - 1)
            
            chart.add_data(data_ref)
            chart.set_categories(cats_ref)
            
            # 配置數據系列：顯示點，隱藏線
            series = chart.series[0]
            series.marker.symbol = "circle"
            series.marker.size = 8
            
            # 設定點的顏色為紅色 (使用正確的 SolidFillProperties 結構)
            from openpyxl.drawing.fill import SolidFillProperties
            series.marker.graphicalProperties.solidFill = SolidFillProperties(srgbClr="FF0000") 
            series.marker.graphicalProperties.line.solidFill = SolidFillProperties(srgbClr="FF0000")
            
            # 重要：移除連線
            series.graphicalProperties.line.noFill = True
            
            # 隱藏圖例 (因為只有一個系列)
            chart.legend = None
            
            chart.width = 30
            chart.height = 15
            ws.add_chart(chart, f"E{start_row}")
            
        except Exception as e:
            print(f"[WARNING] 時間點分佈圖生成失敗: {e}")

    def _add_time_statistics_table(self, ws, times):
        """(過時) 舊的時間統計表，目前由 _add_time_distribution_chart 取代"""
        pass

