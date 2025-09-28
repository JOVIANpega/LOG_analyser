#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復 PASS 匯總工作簿的縮排錯誤 - 第三版
直接替換整個有問題的區塊
"""

def fix_pass_workbook_indent():
    """修復 excel_writer.py 中 _build_pass_workbook 函數的縮排錯誤"""
    
    # 讀取檔案
    with open('excel_writer.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到有問題的區塊並替換
    old_block = """        for entry in logs:
                # 檔名欄
                base = self._sanitize_cell_text(entry.get('file_name') or '')
                base_fmt = self._format_filename_with_timestamp(base)
            sfis = (entry.get('summary') or {}).get('SFIS','')
                sfis = (sfis or '').upper()
            secs = self._extract_total_secs(entry.get('raw_lines') or [])
                sec_txt = f"測試總時間:{secs:.1f} Sec." if secs is not None else ''
                suffix = f"_SFIS_{sfis}" if sfis else ''
            display_name = f"{base_fmt}{suffix} {sec_txt}".strip()
            r = ws.max_row + 1
            cell_name = ws.cell(row=r, column=1, value=self._sanitize_cell_text(display_name))
            cell_name.number_format='@'
            cell_name.font = Font(name='Microsoft JhengHei', size=10, color='FF000000')
                cell_name.alignment = Alignment(wrap_text=True, horizontal='left', vertical='top', shrink_to_fit=True)
                # 備註與超連結
                sheet = sheet_map.get(entry.get('file_name'))
                try:
                    cell_name.comment = Comment(self._build_preview_comment(entry), "LOG Analyzer")
                    cell_name.comment.width = 400
                    cell_name.comment.height = 500
                except Exception:
                    pass
                if sheet:
                    cell_name.hyperlink = f"#'{sheet}'!A1"
                    self._add_input_prompt(ws, cell_name, '對應工作表', entry.get('file_name') or '')
                # PASS步驟數欄"""
    
    new_block = """        for entry in logs:
            # 檔名欄
            base = self._sanitize_cell_text(entry.get('file_name') or '')
            base_fmt = self._format_filename_with_timestamp(base)
            sfis = (entry.get('summary') or {}).get('SFIS','')
            sfis = (sfis or '').upper()
            secs = self._extract_total_secs(entry.get('raw_lines') or [])
            sec_txt = f"測試總時間:{secs:.1f} Sec." if secs is not None else ''
            suffix = f"_SFIS_{sfis}" if sfis else ''
            display_name = f"{base_fmt}{suffix} {sec_txt}".strip()
            r = ws.max_row + 1
            cell_name = ws.cell(row=r, column=1, value=self._sanitize_cell_text(display_name))
            cell_name.number_format='@'
            cell_name.font = Font(name='Microsoft JhengHei', size=10, color='FF000000')
            cell_name.alignment = Alignment(wrap_text=True, horizontal='left', vertical='top', shrink_to_fit=True)
            # 備註與超連結
            sheet = sheet_map.get(entry.get('file_name'))
            try:
                cell_name.comment = Comment(self._build_preview_comment(entry), "LOG Analyzer")
                cell_name.comment.width = 400
                cell_name.comment.height = 500
            except Exception:
                pass
            if sheet:
                cell_name.hyperlink = f"#'{sheet}'!A1"
                self._add_input_prompt(ws, cell_name, '對應工作表', entry.get('file_name') or '')
            # PASS步驟數欄"""
    
    # 替換內容
    if old_block in content:
        content = content.replace(old_block, new_block)
        print("找到並替換了有問題的區塊")
    else:
        print("未找到完全匹配的區塊，嘗試部分替換")
        # 如果完全匹配失敗，嘗試部分替換
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # 修復第253-279行的縮排
            if i >= 252 and i <= 278:  # 行號從0開始
                # 移除多餘的縮排，確保都是12個空格
                if line.startswith('                '):  # 16個空格
                    line = '            ' + line[16:]  # 改為12個空格
                elif line.startswith('            '):  # 12個空格
                    pass  # 保持不變
                elif line.startswith('        '):  # 8個空格
                    line = '            ' + line[8:]  # 改為12個空格
                elif line.strip() and not line.startswith(' '):  # 沒有縮排
                    line = '            ' + line  # 添加12個空格
            
            fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
    
    # 寫回檔案
    with open('excel_writer.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("PASS 匯總工作簿縮排錯誤已修復")

if __name__ == '__main__':
    fix_pass_workbook_indent()
