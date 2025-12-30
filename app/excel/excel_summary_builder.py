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
        
        # 1. 預留頂部空間並插入匯總資訊 (A1:B6 區域)
        # 這裡需要先計算出 logs 的時間資料
        time_labels_data = []
        for entry in logs:
            fname = entry.get('file_name', entry.get('filename', ''))
            isn = extract_isn_from_filename(fname)
            from .excel_utils import extract_total_secs
            test_secs, _ = extract_total_secs(entry.get('raw_lines', []))
            if test_secs:
                label = isn if isn else fname[:20]
                time_labels_data.append((label, test_secs))
        
        self._add_summary_header(ws, len(logs), time_labels_data)
        
        # 2. 寫入清單標題 (從第 9 行開始，留出空間給 Top Summary)
        list_start_row = 9
        headers = ["測試記錄 (合併資訊)", "狀態", "操作", "工作表連結"]
        for col, h in enumerate(headers, 1):
            cell = ws.cell(row=list_start_row, column=col, value=h)
            cell.font = self.header_font
            cell.fill = self.fill_blue
            cell.alignment = self.center_align
            
        # 3. 填寫清單資料
        for row_idx, entry in enumerate(logs, 0):
            curr_row = list_start_row + 1 + row_idx
            fname = entry.get('file_name', entry.get('filename', ''))
            isn = extract_isn_from_filename(fname)
            
            # 寫入第一欄 (合併資訊)
            from .excel_utils import generate_header_info_text
            info_str = generate_header_info_text(entry)
            cell_info = ws.cell(row=curr_row, column=1, value=info_str)
            cell_info.alignment = self.left_top_align
            cell_info.font = self.content_font
            
            # 寫入狀態
            status = "PASS" if not entry.get('fail_items') else "FAIL"
            cell_status = ws.cell(row=curr_row, column=2, value=status)
            cell_status.alignment = self.center_align
            if status == "FAIL":
                cell_status.font = Font(color="FF0000", bold=True)
            
            # 工作表格式化名稱
            sheet_name = entry.get('sheet_name', isn or fname[:25])
            
            # 連結 (變更文字)
            cell_link = ws.cell(row=curr_row, column=4, value=f"查看LOG {sheet_name}")
            cell_link.hyperlink = f"#'{sheet_name}'!A1"
            cell_link.font = Font(color="0000FF", underline="single")
            
        auto_fit_columns(ws, {1: 60, 2: 10, 3: 15, 4: 25})
        
        # 4. 新增隱藏的數據分頁 (給圖表用) 或是在 Z 軸之後
        if time_labels_data:
            self._add_time_distribution_chart(ws, time_labels_data)
            
        return ws

    def _add_summary_header(self, ws, total_count, time_data):
        """插入頂部置頂資訊與統計 (同步 FAIL 風格)"""
        # 標題列
        ws.merge_cells('A1:F1')
        title_cell = ws.cell(row=1, column=1, value=" 📋 PASS 分析匯總報告 (Summary & List) ")
        title_cell.font = Font(name='Calibri', size=16, bold=True, color='FFFFFF')
        title_cell.fill = PatternFill('solid', fgColor='2E7D32') # 綠色
        title_cell.alignment = Alignment(horizontal='center', vertical='center')

        # 統計數據 (A3:B6)
        avg_time = sum(d[1] for d in time_data) / len(time_data) if time_data else 0
        max_time = max(d[1] for d in time_data) if time_data else 0
        min_time = min(d[1] for d in time_data) if time_data else 0

        stats = [
            ("項目數量", f"{total_count} 筆"),
            ("平均時間", f"{avg_time:.2f} Sec"),
            ("最長時間", f"{max_time:.2f} Sec"),
            ("最短時間", f"{min_time:.2f} Sec")
        ]

        for i, (label, val) in enumerate(stats):
            row = 3 + i
            # Label
            ws.cell(row=row, column=1, value=label).font = Font(bold=True)
            # Value
            v_cell = ws.cell(row=row, column=2, value=val)
            v_cell.alignment = Alignment(horizontal='center')

    def _add_time_distribution_chart(self, ws, time_data):
        """新增測試時間分佈圖 (點圖/Dot Map) 錨定在頂部 E3"""
        try:
            from openpyxl.chart import LineChart, Reference
            
            # 使用 Z 欄之後儲存隱藏數據
            data_col = 26 # Z
            for i, (label, val) in enumerate(time_data):
                ws.cell(row=i+1, column=data_col, value=label)
                ws.cell(row=i+1, column=data_col+1, value=val)
            
            chart = LineChart()
            chart.title = "測試時間分佈圖 (Time Curve)"
            chart.style = 13
            chart.y_axis.title = "秒數 (Sec)"
            chart.x_axis.title = "測試項 (ID)"
            
            # 設定座標軸刻度單位 (100 sec)
            chart.y_axis.majorUnit = 100
            
            # 數據引用 (時間值在 AA 欄)
            data_ref = Reference(ws, min_col=data_col+1, min_row=1, max_row=len(time_data))
            # 分類引用 (ISN 在 Z 欄)
            cats_ref = Reference(ws, min_col=data_col, min_row=1, max_row=len(time_data))
            
            chart.add_data(data_ref)
            chart.set_categories(cats_ref)
            
            # 配置數據系列
            series = chart.series[0]
            series.marker.symbol = "circle"
            series.marker.size = 5
            
            # 配色與線條
            from openpyxl.drawing.fill import SolidFillProperties
            # 這裡我們保留線條，讓它看起來像曲線 (Curve)
            series.graphicalProperties.line.solidFill = SolidFillProperties(srgbClr="2E7D32") # 綠色線
            series.marker.graphicalProperties.solidFill = SolidFillProperties(srgbClr="FF0000") # 紅色點
            
            chart.legend = None # 單一數據不需要圖例
            chart.width = 30
            chart.height = 10
            
            # 錨定在 E3
            ws.add_chart(chart, "E3")
            
        except Exception as e:
            print(f"[WARNING] PASS 時間分布圖生成失敗: {e}")

    def _add_time_statistics_table(self, ws, times):
        """(過時) 舊的時間統計表，目前由 _add_time_distribution_chart 取代"""
        pass

