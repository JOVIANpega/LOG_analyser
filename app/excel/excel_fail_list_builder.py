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
    generate_header_info_text,
    auto_fit_columns
)

class FailListBuilder:
    """構建統一的 FAIL 分析報告 (合併 Summary 與 FAIL_LIST)"""
    
    def __init__(self):
        self.title_font = Font(name='Calibri', size=16, bold=True, color='FFFFFF')
        self.header_font = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
        self.content_font = Font(name='Calibri', size=11)
        self.fill_blue = PatternFill('solid', fgColor='4472C4')
        self.fill_red = PatternFill('solid', fgColor='FF0000')
        self.fill_green = PatternFill('solid', fgColor='2E7D32')
        self.fill_yellow = PatternFill('solid', fgColor='FFFF00')
        self.center_align = Alignment(horizontal='center', vertical='center')
        self.top_left_align = Alignment(wrap_text=True, vertical='top', horizontal='left')

    def build_fail_list_sheet(self, wb, logs):
        """建立統一的 FAIL 分析總表 (Summary at Top)"""
        ws = wb.create_sheet("FAIL_LIST", 0)
        try:
            ws.sheet_properties.tabColor = 'FFFF0000'
        except Exception:
            pass
        
        # 1. 插入置頂匯總標題與統計資訊
        self._add_summary_header(ws, logs)
        
        # 2. 插入錯誤各項計數統計 (Breakdown)
        error_counts = self._calculate_counts(logs)
        self._add_item_breakdown_table(ws, error_counts, start_col=1, start_row=8)
        
        # 3. 準備清單數據 (從 Breakdown 之後開始)
        headers = ['ISN', 'Station', 'FAIL Item', 'FAIL Reason', 'suggestion', 'Count']
        start_row = ws.max_row + 2
        
        # 寫入清單標題
        for col, h in enumerate(headers, 1):
            cell = ws.cell(row=start_row, column=col, value=h)
            cell.font = self.header_font
            if col == 4: cell.fill = self.fill_red
            else: cell.fill = self.fill_blue
            cell.alignment = self.center_align
            
        # 4. 收集並準備資料行
        pending_rows = []
        for entry in logs:
            primary_fail = entry.get('last_fail')
            if not primary_fail and entry.get('fail_items'):
                primary_fail = entry['fail_items'][-1]
            if not primary_fail: continue
                
            fname = entry.get('file_name', entry.get('filename', ''))
            isn = extract_isn_from_filename(fname)
            station = extract_station_from_filename(fname)
            suggestion = "請參閱 PEGA SOP"

            step_name = primary_fail.get('step_name', '')
            result_val = primary_fail.get('result', '')
            fail_item_str = f"{step_name}"
            if result_val and result_val not in step_name:
                 fail_item_str += f" {result_val}"
            
            fail_item_str = re.sub(r'\s+\b(is\s+)?FAIL\b.*$', '', fail_item_str, flags=re.IGNORECASE).strip()
            fail_item_str = fail_item_str.strip() or "Unknown Item"
            
            # 理由提取 logic
            reason = ""
            full_log = primary_fail.get('full_log', [])
            for log_line in reversed(full_log):
                if "doesn't match" in log_line.lower():
                    reason = log_line.strip()
                    break
            if not reason: reason = primary_fail.get('error', '')
            if not reason or reason == 'FAIL': reason = primary_fail.get('response', '')
            
            # 合併資訊
            merged_info = generate_header_info_text(entry)
            
            pending_rows.append({
                'merged_info': merged_info,
                'item': fail_item_str,
                'reason': reason,
                'suggestion': suggestion,
                'norm_key': fail_item_str,
                'sheet_name': entry.get('sheet_name', ''),
                'error_row': entry.get('error_excel_row', 1)
            })
        
        # 排序並寫入細節
        pending_rows.sort(key=lambda x: (x['item']))
        
        data_start_row = start_row + 1
        for i, row_data in enumerate(pending_rows):
            curr_row = data_start_row + i
            count = error_counts.get(row_data['norm_key'], 0)
            
            row_vals = [row_data['merged_info'], row_data['item'], row_data['reason'], row_data['suggestion'], count]
            for col_idx, val in enumerate(row_vals, 1):
                cell = ws.cell(row=curr_row, column=col_idx, value=sanitize_cell_text(val))
                cell.font = self.content_font
                
                if col_idx == 1:
                    cell.alignment = self.top_left_align
                    # 在首行添加超鏈接
                    cell.hyperlink = f"#'{row_data['sheet_name']}'!A{row_data.get('error_row', 1)}"
                    cell.font = Font(name='Calibri', size=11, color='0563C1', underline='single')
                elif col_idx in (2, 5): 
                    cell.alignment = self.center_align
                elif col_idx == 3:
                    cell.alignment = self.top_left_align
                else: 
                    cell.alignment = Alignment(wrap_text=True, vertical='center', horizontal='left')

        # 自動調整欄寬
        auto_fit_columns(ws, {1: 60, 2: 45, 3: 65, 4: 25, 5: 12})
        return ws

    def _calculate_counts(self, logs):
        """計算各錯誤項目的數量"""
        counts = {}
        for entry in logs:
            primary_fail = entry.get('last_fail')
            if not primary_fail and entry.get('fail_items'):
                primary_fail = entry['fail_items'][-1]
            if not primary_fail: continue
            
            step_name = primary_fail.get('step_name', '')
            fail_item_str = re.sub(r'\s+\b(is\s+)?FAIL\b.*$', '', step_name, flags=re.IGNORECASE).strip()
            fail_item_str = fail_item_str.strip() or "Unknown Item"
            counts[fail_item_str] = counts.get(fail_item_str, 0) + 1
        return counts

    def _add_summary_header(self, ws, logs):
        """插入頂部資訊與圖表"""
        ws.merge_cells('A1:F1')
        title_cell = ws.cell(row=1, column=1, value=" 📋 FAIL 分析匯總報告 (Summary & List) ")
        title_cell.font = self.title_font
        title_cell.fill = self.fill_green
        title_cell.alignment = self.center_align
        
        # 統計數據 (A3:B6)
        from .excel_utils import extract_total_secs
        times = []
        for entry in logs:
            t, _ = extract_total_secs(entry.get('raw_lines', []))
            if t: times.append((extract_isn_from_filename(entry.get('file_name', '')), t))
            
        stats = [
            ("項目數量", f"{len(logs)} 筆"),
            ("平均時間", f"{sum(t[1] for t in times)/len(times):.2f} Sec" if times else "N/A"),
            ("最長時間", f"{max(t[1] for t in times):.2f} Sec" if times else "N/A"),
            ("最短時間", f"{min(t[1] for t in times):.2f} Sec" if times else "N/A")
        ]
        
        for i, (label, val) in enumerate(stats):
            row = 3 + i
            ws.cell(row=row, column=1, value=label).font = Font(bold=True)
            ws.cell(row=row, column=2, value=val).alignment = self.center_align
            
        # 圖表 - 錨定在 E3
        if times:
            try:
                from openpyxl.chart import LineChart, Reference
                chart = LineChart()
                chart.title = "測試時間分佈點圖"
                chart.legend = None
                chart.width = 25
                chart.height = 10
                
                # 建立隱藏數據區域於 Column Z 之後，避免汙染主畫面
                data_col = 26 # Z
                for i, (label, val) in enumerate(times):
                    ws.cell(row=i+1, column=data_col, value=label)
                    ws.cell(row=i+1, column=data_col+1, value=val)
                
                data_ref = Reference(ws, min_col=data_col+1, min_row=1, max_row=len(times))
                chart.add_data(data_ref)
                ws.add_chart(chart, "E3")
            except: pass

    def _add_item_breakdown_table(self, ws, error_counts, start_col=1, start_row=8):
        """插入分組統計表格"""
        ws.cell(row=start_row, column=start_col, value=" 📊 FAIL Item 統計 (記數) ").font = Font(bold=True)
        h_row = start_row + 1
        c1 = ws.cell(row=h_row, column=start_col, value="FAIL Item 名稱")
        c2 = ws.cell(row=h_row, column=start_col+1, value="數量")
        for c in [c1, c2]:
            c.font = self.header_font
            c.fill = self.fill_blue
            c.alignment = self.center_align
            
        sorted_items = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        for i, (item, count) in enumerate(sorted_items):
            curr_r = h_row + 1 + i
            v1 = ws.cell(row=curr_r, column=start_col, value=item)
            v2 = ws.cell(row=curr_r, column=start_col+1, value=count)
            v1.fill = self.fill_yellow
            v2.fill = self.fill_yellow
            v2.alignment = self.center_align

    def _add_pie_chart(self, ws, error_counts):
        """原有的圓餅圖函數 (目前不再調用，保留供未來參考)"""
        try:
            # 原本的完整統計邏輯在上面已經抽離為 _add_error_statistics_table
            pass
        except Exception:
            pass

