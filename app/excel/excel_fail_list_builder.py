import re
# 延後載入：openpyxl 將在內部方法載入以提升啟動速度

class FailListBuilder:
    """构建新格式的FAIL报告 - Dashboard + FAIL_LIST"""
    
    def __init__(self):
        # 错误类型颜色映射
        self.error_colors = {
            "系统崩溃": "FF0000",      # 红色
            "数值不匹配": "FFA500",    # 橙色
            "超时错误": "FFFF00",      # 黄色
            "执行失败": "FF69B4",      # 粉色
            "参数错误": "FFC0CB",      # 浅粉色
            "其他错误": "D3D3D3"       # 灰色
        }
        
        # 错误关键字分类
        self.error_categories = {
            "Segmentation Fault": "系统崩溃",
            "core dumped": "系统崩溃",
            "doesn't match": "数值不匹配",
            "timeout": "超时错误",
            "executes fail": "执行失败",
            "Wrong": "参数错误",
            "exception": "参数错误",
            "FAIL": "其他错误",
            "ERROR": "其他错误"
        }
    
    def build_dashboard_sheet(self, wb, logs):
        """
        创建Dashboard工作表 - 结构化摘要
        
        列: 状态 | ISN | Station | 错误类型 | 错误详情 | 发生时间 | Retry次数 | 查看详细
        """
        from openpyxl.styles import Font, Alignment, PatternFill
        from .excel_utils import auto_fit_columns
        ws = wb.create_sheet("Dashboard", 0)
        
        # 标题行
        headers = ["状态", "ISN", "Station", "错误类型", "错误详情", "发生时间", "Retry次数", "查看详细"]
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.font = Font(name='Calibri', size=11, bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="4472C4", fill_type="solid")
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # 数据行
        for row_num, log_entry in enumerate(logs, 2):
            error_info = self._extract_error_info(log_entry)
            
            # 状态
            ws.cell(row=row_num, column=1, value="🔴")
            
            # ISN
            ws.cell(row=row_num, column=2, value=error_info['isn'])
            
            # Station
            ws.cell(row=row_num, column=3, value=error_info['station'])
            
            # 错误类型
            error_type_cell = ws.cell(row=row_num, column=4, value=error_info['error_type'])
            error_category = error_info['error_category']
            if error_category in self.error_colors:
                error_type_cell.fill = PatternFill(
                    start_color=self.error_colors[error_category],
                    fill_type="solid"
                )
            error_type_cell.font = Font(bold=True)
            
            # 错误详情
            ws.cell(row=row_num, column=5, value=error_info['error_detail'])
            
            # 发生时间
            ws.cell(row=row_num, column=6, value=error_info['timestamp'])
            
            # Retry次数
            ws.cell(row=row_num, column=7, value=error_info['retry_count'])
            
            # 查看详细 (超链接到对应工作表)
            sheet_name = log_entry.get('sheet_name', '')
            if sheet_name:
                link_cell = ws.cell(row=row_num, column=8, value="[查看LOG]")
                link_cell.hyperlink = f"#{sheet_name}!A1"
                link_cell.font = Font(color="0000FF", underline="single")
        
        # 自动调整列宽
        auto_fit_columns(ws, {
            'A': 6,   # 状态
            'B': 15,  # ISN
            'C': 20,  # Station
            'D': 20,  # 错误类型
            'E': 40,  # 错误详情
            'F': 12,  # 发生时间
            'G': 10,  # Retry次数
            'H': 12   # 查看详细
        })
        
        return ws
    
    def build_fail_list_sheet(self, wb, logs):
        """
        创建FAIL_LIST工作表 - 详细列表
        
        列: ISN | Station | 测试项目 | 错误类型 | 错误原因 | 执行指令
        """
        from openpyxl.styles import Font, Alignment, PatternFill
        from .excel_utils import auto_fit_columns
        ws = wb.create_sheet("FAIL_LIST", 1)
        
        # 标题行
        headers = ["ISN", "Station", "测试项目", "错误类型", "错误原因", "执行指令"]
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.font = Font(name='Calibri', size=11, bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="C00000", fill_type="solid")
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # 数据行
        row_num = 2
        for log_entry in logs:
            error_info = self._extract_error_info(log_entry)
            fail_items = log_entry.get('fail_items', [])
            
            if not fail_items:
                # 如果没有具体的fail项，至少显示一行
                ws.cell(row=row_num, column=1, value=error_info['isn'])
                ws.cell(row=row_num, column=2, value=error_info['station'])
                ws.cell(row=row_num, column=3, value="Unknown")
                ws.cell(row=row_num, column=4, value=error_info['error_type'])
                ws.cell(row=row_num, column=5, value=error_info['error_detail'])
                ws.cell(row=row_num, column=6, value="")
                row_num += 1
            else:
                # 为每个fail项创建一行
                for item in fail_items:
                    ws.cell(row=row_num, column=1, value=error_info['isn'])
                    ws.cell(row=row_num, column=2, value=error_info['station'])
                    ws.cell(row=row_num, column=3, value=item.get('step_name', ''))
                    ws.cell(row=row_num, column=4, value=error_info['error_type'])
                    ws.cell(row=row_num, column=5, value=item.get('error_reason', ''))
                    ws.cell(row=row_num, column=6, value=item.get('command', ''))
                    row_num += 1
        
        # 自动调整列宽
        auto_fit_columns(ws, {
            'A': 15,  # ISN
            'B': 20,  # Station
            'C': 25,  # 测试项目
            'D': 20,  # 错误类型
            'E': 40,  # 错误原因
            'F': 30   # 执行指令
        })
        
        return ws
    
    def _extract_error_info(self, log_entry):
        """从LOG条目提取结构化错误信息"""
        from .excel_utils import extract_isn_from_filename, extract_station_from_filename
        filename = log_entry.get('filename', '')
        error_text = log_entry.get('error_text', '')
        summary = log_entry.get('summary', {})
        
        # 提取ISN
        isn = extract_isn_from_filename(filename)
        
        # 提取Station
        station = extract_station_from_filename(filename)
        
        # 提取错误类型和分类
        error_type, error_category = self._classify_error(error_text)
        
        # 提取错误详情
        error_detail = self._extract_error_detail(error_text)
        
        # 提取时间戳
        timestamp = summary.get('测试日期时间', '')
        
        # Retry次数
        retry_count = log_entry.get('retry_count', 0)
        
        return {
            'isn': isn,
            'station': station,
            'error_type': error_type,
            'error_category': error_category,
            'error_detail': error_detail,
            'timestamp': timestamp,
            'retry_count': retry_count
        }
    
    def _classify_error(self, error_text):
        """
        分类错误类型
        返回: (错误类型, 错误分类)
        """
        error_text_lower = error_text.lower()
        
        # 按优先级检查错误关键字
        for keyword, category in self.error_categories.items():
            if keyword.lower() in error_text_lower:
                return (keyword, category)
        
        return ("Unknown Error", "其他错误")
    
    def _extract_error_detail(self, error_text):
        """提取错误详细信息 (简短版本)"""
        # 提取第一行包含错误的文字
        lines = error_text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['fail', 'error', 'wrong', 'timeout']):
                # 截断过长的行
                if len(line) > 100:
                    return line[:97] + "..."
                return line.strip()
        
        # 如果没找到，返回前100个字符
        if len(error_text) > 100:
            return error_text[:97] + "..."
        return error_text.strip()
