# -*- coding: utf-8 -*-
"""
FAIL_LIST Builder Module
Handles the construction of the FAIL_LIST sheet and error statistics.
"""
import re
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.chart import PieChart, Reference
from openpyxl.chart.label import DataLabelList
from .excel_utils import (
    sanitize_cell_text, 
    extract_isn_from_filename, 
    extract_station_from_filename,
    auto_fit_columns
)

class FailListBuilder:
    """構建 FAIL_LIST 工作表與錯誤統計"""
    
    def __init__(self):
        self.header_font = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
        self.content_font = Font(name='Calibri', size=11)
        self.fill_blue = PatternFill('solid', fgColor='4472C4')
        self.fill_red = PatternFill('solid', fgColor='FF0000')
        self.center_align = Alignment(horizontal='center', vertical='center')
        self.top_left_align = Alignment(wrap_text=True, vertical='top', horizontal='left')

    def build_fail_list_sheet(self, wb, logs):
        """建立 FAIL_LIST 工作表 (依使用者要求的 CSV 格式，並統計相同錯誤)"""
        ws = wb.create_sheet("FAIL_LIST", 0) # 放在第一頁
        try:
            ws.sheet_properties.tabColor = 'FFFF0000' # 紅色標籤
        except Exception:
            pass
        
        # 設定標題 (新增 Count 欄位)
        headers = ['ISN', 'Station', 'FAIL Item', 'FAIL Reason', 'suggestion', 'Count']
        ws.append(headers)
        
        # 標題樣式
        for col in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col)
            cell.font = self.header_font
            # FAIL Reason (Column D) 使用紅色背景
            if col == 4:
                cell.fill = self.fill_red
            else:
                cell.fill = self.fill_blue
            cell.alignment = self.center_align
        
        # 1. 收集所有資料行與統計錯誤
        pending_rows = []
        error_counts = {}
        
        for entry in logs:
            fail_items = entry.get('fail_items', [])
            if not fail_items:
                continue
                
            fname = entry.get('file_name', entry.get('filename', ''))
            isn = extract_isn_from_filename(fname)
            station = extract_station_from_filename(fname)
            suggestion = "請參閱 PEGA SOP"
            
            for item in fail_items:
                step_name = item.get('step_name', '')
                result = item.get('result', '')
                fail_item_str = f"{step_name}"
                if result and result not in step_name:
                     fail_item_str += f" {result}"
                
                # 清理 Item 名稱：移除冗餘的 FAIL/is Fail
                fail_item_str = re.sub(r'\s+\b(is\s+)?FAIL\b.*$', '', fail_item_str, flags=re.IGNORECASE).strip()
                fail_item_str = fail_item_str.strip() or "Unknown Item"
                
                reason = item.get('error', '')
                if not reason or reason == 'FAIL':
                    reason = item.get('response', '')
                
                # 統計
                error_counts[fail_item_str] = error_counts.get(fail_item_str, 0) + 1
                
                pending_rows.append({
                    'isn': isn,
                    'station': station,
                    'item': fail_item_str,
                    'reason': reason,
                    'suggestion': suggestion,
                    'norm_key': fail_item_str
                })
        
        # 2. 排序資料 (依內容分類，讓同類型錯誤擺在一起)
        pending_rows.sort(key=lambda x: (x['item'], x['isn']))
        
        # 3. 寫入資料
        for row_data in pending_rows:
            count = error_counts.get(row_data['norm_key'], 0)
            
            row_values = [
                sanitize_cell_text(row_data['isn']),
                sanitize_cell_text(row_data['station']),
                sanitize_cell_text(row_data['item']),
                sanitize_cell_text(row_data['reason']),
                sanitize_cell_text(row_data['suggestion']),
                count
            ]
            ws.append(row_values)
            
            current_row = ws.max_row
            for col_idx, value in enumerate(row_values, 1):
                cell = ws.cell(row=current_row, column=col_idx)
                cell.font = self.content_font
                if col_idx in (1, 2, 3, 6): # ISN, Station, FAIL Item, Count 不換行且置中
                    cell.alignment = self.center_align
                elif col_idx == 4: # FAIL Reason 換行且靠上
                    cell.alignment = self.top_left_align
                else: # suggestion 置中靠上
                    cell.alignment = Alignment(wrap_text=True, vertical='center', horizontal='left')
                
        # 強制自動調整欄寬
        min_widths = {
            1: 25, # ISN
            2: 30, # Station
            3: 45, # FAIL Item
            4: 65, # FAIL Reason
            5: 20, # suggestion
            6: 12  # Count
        }
        auto_fit_columns(ws, min_widths=min_widths)
        
        # 4. 添加統計圖表
        if error_counts:
            self._add_pie_chart(ws, error_counts)
            
        return ws

    def _add_pie_chart(self, ws, error_counts):
        """在 FAIL_LIST 頁面添加圓餅圖與統計表"""
        try:
            table_start_row = ws.max_row + 3
            
            ws.cell(row=table_start_row, column=1, value="FAIL Item 統計 (記數)").font = Font(name='Calibri', size=12, bold=True)
            ws.cell(row=table_start_row + 1, column=1, value="FAIL Item 名稱").font = self.header_font
            ws.cell(row=table_start_row + 1, column=2, value="數量").font = self.header_font
            ws.cell(row=table_start_row + 1, column=3, value="佔比").font = self.header_font
            
            total_errors = sum(error_counts.values())
            summary_start_row = table_start_row + 2
            
            sorted_items = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
            yellow_fill = PatternFill('solid', fgColor='FFFF00')
            from openpyxl.styles import Border, Side
            thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                               top=Side(style='thin'), bottom=Side(style='thin'))
            
            for idx, (error_type, count) in enumerate(sorted_items):
                row = summary_start_row + idx
                percentage = (count / total_errors * 100) if total_errors > 0 else 0
                
                c1 = ws.cell(row=row, column=1, value=sanitize_cell_text(error_type))
                c2 = ws.cell(row=row, column=2, value=count)
                c3 = ws.cell(row=row, column=3, value=f"{percentage:.1f}%")
                
                # 套用樣式與黃色背景
                for c in [c1, c2, c3]:
                    c.font = Font(name='Calibri', size=11)
                    c.fill = yellow_fill
                    c.border = thin_border
                    
                c2.alignment = self.center_align
                c3.alignment = self.center_align
            
            # 圖表
            chart = PieChart()
            chart.title = "FAIL Item 佔比統計"
            chart.style = 10 
            chart.legend = None # 不顯示圖例 (數列1, 數列2...)
            
            max_r = summary_start_row + len(error_counts) - 1
            data = Reference(ws, min_col=2, min_row=summary_start_row, max_row=max_r)
            cats = Reference(ws, min_col=1, min_row=summary_start_row, max_row=max_r)
            
            chart.add_data(data, titles_from_data=False)
            chart.set_categories(cats)
            
            # 設定 Data Labels 格式
            chart.dataLabels = DataLabelList()
            chart.dataLabels.showPercent = True
            chart.dataLabels.showCatName = True
            chart.dataLabels.showSerName = False 
            
            # 設定字體大小 (14pt)
            try:
                from openpyxl.drawing.text import CharacterProperties, Paragraph, ParagraphProperties, RichTextProperties
                cp = CharacterProperties(sz=1400)  # 14pt
                chart.dataLabels.txPr = RichTextProperties(p=[Paragraph(pPr=ParagraphProperties(defRPr=cp), endParaRPr=cp)])
            except:
                pass
            
            # 設定高度與寬度
            chart.height = 13
            chart.width = 18
            
            # 放置在表格下方 (數據結束行 + 6，即空5行)
            # 表格佔用 Col 1-3，圖表放在 Col A 會比較整齊
            chart_row = max_r + 6
            ws.add_chart(chart, f"A{chart_row}")
        except Exception as e:
            print(f"[WARNING] 圓餅圖生成失敗: {e}")
