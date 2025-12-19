import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import glob
from datetime import datetime
import re
# 延後載入：pandas, openpyxl 將在內部方法載入以提升啟動速度
class CSVProcessor:
    def __init__(self, app):
        self.app = app
        self.csv_files = []
        self.analysis_dir = None
        self.max_display_length = 50  # 預設最大顯示長度
        self.selected_files = []  # 使用者選擇的檔案
        
    def select_directory(self):
        """讓使用者選擇包含CSV檔案的目錄"""
        directory = filedialog.askdirectory(title="選擇包含CSV檔案的目錄")
        if directory:
            self.scan_csv_files(directory)
            return True
        return False
    
    def select_files(self):
        """讓使用者直接選擇CSV檔案（支援多選）"""
        file_paths = filedialog.askopenfilenames(
            title="選擇CSV檔案（可多選）",
            filetypes=[
                ("CSV檔案", "*.csv"),
                ("所有檔案", "*.*")
            ]
        )
        if file_paths:
            self.csv_files = list(file_paths)
            self.show_csv_selection_window()
            return True
        return False
    
    def scan_csv_files(self, directory):
        """掃描目錄中的CSV檔案"""
        self.csv_files = []
        patterns = ['*.csv', '*.CSV']
        
        for pattern in patterns:
            files = glob.glob(os.path.join(directory, pattern))
            self.csv_files.extend(files)
        
        # 顯示找到的CSV檔案
        if self.csv_files:
            self.show_csv_selection_window()
        else:
            messagebox.showinfo("提示", "在選擇的目錄中沒有找到CSV檔案")
    
    def show_csv_selection_window(self):
        """顯示CSV檔案選擇視窗（含checkbox）"""
        # 創建新視窗顯示CSV檔案列表
        self.selection_window = tk.Toplevel(self.app.root)
        self.selection_window.title("選擇要處理的CSV檔案")
        self.selection_window.geometry("700x500")
        self.selection_window.resizable(True, True)
        
        # 主框架
        main_frame = tk.Frame(self.selection_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 標題
        title_label = tk.Label(main_frame, text=f"找到 {len(self.csv_files)} 個CSV檔案", 
                              font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # 說明文字
        info_label = tk.Label(main_frame, 
                             text="請選擇要處理的CSV檔案（至少選擇一個）", 
                             font=('Arial', 10), fg='blue')
        info_label.pack(pady=(0, 10))
        
        # 全選/全不選按鈕框架
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(button_frame, text="全選", 
                 command=self.select_all_files,
                 bg='#4CAF50', fg='white', font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="全不選", 
                 command=self.deselect_all_files,
                 bg='#f44336', fg='white', font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        
        # 檔案列表框架
        list_frame = tk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 創建Treeview with checkboxes
        columns = ('選擇', '檔案名稱', '檔案大小', '修改時間')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # 設定欄位寬度
        self.tree.heading('選擇', text='選擇')
        self.tree.heading('檔案名稱', text='檔案名稱')
        self.tree.heading('檔案大小', text='檔案大小')
        self.tree.heading('修改時間', text='修改時間')
        
        self.tree.column('選擇', width=60, anchor='center')
        self.tree.column('檔案名稱', width=300)
        self.tree.column('檔案大小', width=100)
        self.tree.column('修改時間', width=150)
        
        # 添加檔案資訊
        self.checkbox_vars = []  # 儲存checkbox變數
        
        for i, file_path in enumerate(self.csv_files):
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            mod_time = os.path.getmtime(file_path)
            
            # 創建checkbox變數
            var = tk.BooleanVar()
            var.set(i == 0)  # 預設第一個打勾
            self.checkbox_vars.append(var)
            
            # 插入資料
            self.tree.insert('', 'end', values=(
                '☑' if var.get() else '☐',  # checkbox顯示
                file_name,
                f"{file_size:,} bytes",
                datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            # 綁定checkbox變更事件
            var.trace('w', lambda *args, idx=i: self.update_checkbox_display(idx))
        
        # 滾動條
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 綁定點擊事件
        self.tree.bind('<Button-1>', self.on_tree_click)
        
        # 底部按鈕框架
        bottom_frame = tk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 狀態標籤
        self.status_label = tk.Label(bottom_frame, text="已選擇 1 個檔案", 
                                    font=('Arial', 10), fg='green')
        self.status_label.pack(side=tk.LEFT)
        
        # 按鈕
        tk.Button(bottom_frame, text="開始處理", 
                 command=self.start_processing,
                 bg='#4CAF50', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(bottom_frame, text="取消", 
                 command=self.selection_window.destroy,
                 bg='#f44336', fg='white').pack(side=tk.RIGHT, padx=5)
        
        # 更新狀態
        self.update_status_label()
    
    def on_tree_click(self, event):
        """處理Treeview點擊事件"""
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        
        if item and column == '#1':  # 點擊選擇欄位
            # 找到對應的檔案索引
            item_index = self.tree.index(item)
            if 0 <= item_index < len(self.checkbox_vars):
                # 切換checkbox狀態
                current_value = self.checkbox_vars[item_index].get()
                self.checkbox_vars[item_index].set(not current_value)
    
    def update_checkbox_display(self, index):
        """更新checkbox顯示"""
        if 0 <= index < len(self.checkbox_vars):
            var = self.checkbox_vars[index]
            items = list(self.tree.get_children())
            if 0 <= index < len(items):
                item = items[index]
                values = list(self.tree.item(item, 'values'))
                values[0] = '☑' if var.get() else '☐'
                self.tree.item(item, values=values)
                self.update_status_label()
    
    def select_all_files(self):
        """全選所有檔案"""
        for var in self.checkbox_vars:
            var.set(True)
    
    def deselect_all_files(self):
        """全不選所有檔案"""
        for var in self.checkbox_vars:
            var.set(False)
    
    def update_status_label(self):
        """更新狀態標籤"""
        selected_count = sum(1 for var in self.checkbox_vars if var.get())
        self.status_label.config(text=f"已選擇 {selected_count} 個檔案")
        
        # 更新開始處理按鈕狀態
        if selected_count == 0:
            self.status_label.config(fg='red')
        else:
            self.status_label.config(fg='green')
    
    def start_processing(self):
        """開始處理選中的CSV檔案"""
        # 檢查是否至少選擇一個檔案
        selected_files = []
        for i, var in enumerate(self.checkbox_vars):
            if var.get():
                selected_files.append(self.csv_files[i])
        
        if not selected_files:
            messagebox.showwarning("警告", "請至少選擇一個CSV檔案進行處理")
            return
        
        self.selected_files = selected_files
        self.selection_window.destroy()
        
        # 創建Analysis_CSV_FILE目錄
        self.create_analysis_directory()
        
        # 複製檔案並處理
        self.copy_and_process_files()
    
    def create_analysis_directory(self):
        """創建Analysis_CSV_FILE目錄"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.analysis_dir = os.path.join(current_dir, "Analysis_CSV_FILE")
        
        if not os.path.exists(self.analysis_dir):
            os.makedirs(self.analysis_dir)
            print(f"已創建目錄: {self.analysis_dir}")
    
    def copy_and_process_files(self):
        """複製檔案並逐一處理"""
        progress_window = self.create_progress_window()
        
        for i, csv_file in enumerate(self.selected_files):
            try:
                # 更新進度
                progress_window.update_progress(i, len(self.selected_files), os.path.basename(csv_file))
                
                # 複製檔案
                copied_file = self.copy_file(csv_file)
                
                # 處理CSV檔案
                self.process_csv_file(copied_file)
                
            except Exception as e:
                print(f"處理檔案 {csv_file} 時發生錯誤: {e}")
        
        progress_window.complete()
        
        # 處理完成後詢問是否開啟檔案
        self.ask_open_files()
    
    def ask_open_files(self):
        """詢問使用者是否要開啟處理後的檔案"""
        # 獲取所有生成的Excel檔案
        excel_files = []
        for file in os.listdir(self.analysis_dir):
            if file.endswith('.xlsx'):
                excel_files.append(os.path.join(self.analysis_dir, file))
        
        if not excel_files:
            messagebox.showinfo("完成", "CSV檔案處理完成！")
            return
        
        # 詢問是否開啟檔案
        result = messagebox.askyesno(
            "處理完成", 
            f"CSV檔案處理完成！\n\n已生成 {len(excel_files)} 個Excel檔案。\n\n是否要開啟Analysis_CSV_FILE資料夾？"
        )
        
        if result:
            # 開啟資料夾
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                subprocess.run(["explorer", self.analysis_dir])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", self.analysis_dir])
            else:  # Linux
                subprocess.run(["xdg-open", self.analysis_dir])
    
    def copy_file(self, source_file):
        """複製檔案到Analysis_CSV_FILE目錄"""
        file_name = os.path.basename(source_file)
        dest_file = os.path.join(self.analysis_dir, file_name)
        shutil.copy2(source_file, dest_file)
        return dest_file
    
    def detect_header_row(self, csv_file, encoding, sep):
        """檢測CSV檔案的列標題行位置和元數據行"""
        try:
            with open(csv_file, 'r', encoding=encoding, errors='ignore') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= 20:  # 只檢查前20行
                        break
                    lines.append(line.strip())
            
            # 常見的列標題關鍵字
            common_headers = ['serial', 'id', 'time', 'result', 'test', 'project', 'station', 
                            'factory', 'operator', 'cycle', 'diag', 'gui', 'fixture']
            
            header_row_index = None
            metadata_rows = []
            
            for i, line in enumerate(lines):
                if not line:
                    continue
                
                # 分割行
                parts = line.split(sep)
                line_lower = line.lower()
                
                # 檢查是否包含常見的列標題關鍵字（至少3個匹配）
                matches = sum(1 for header in common_headers if header in line_lower)
                
                # 如果匹配度夠高，且列數合理（至少3列），認為是標題行
                if matches >= 3 and len(parts) >= 3:
                    header_row_index = i
                    metadata_rows = lines[:i]  # 前面的行都是元數據
                    break
            
            return header_row_index, metadata_rows
        except:
            return None, []
    
    def parse_metadata(self, metadata_rows):
        """解析元數據行，提取有用信息"""
        metadata = {
            'contact': '',
            'error_codes': {},
            'limits': {}
        }
        
        for row in metadata_rows:
            row_lower = row.lower()
            # 提取聯繫信息
            if 'email' in row_lower or 'contact' in row_lower:
                metadata['contact'] = row
            # 提取ErrorCode
            elif 'errorcode' in row_lower:
                metadata['error_codes']['header'] = row
            # 提取Upperlimit/Lowerlimit
            elif 'upperlimit' in row_lower:
                metadata['limits']['upper'] = row
            elif 'lowerlimit' in row_lower:
                metadata['limits']['lower'] = row
        
        return metadata
    
    def process_csv_file(self, csv_file):
        """處理單個CSV檔案 - 改進版，支持元數據行檢測"""
        try:
            df = None
            encoding_used = None
            separator_used = None
            header_row_index = None
            metadata_rows = []
            metadata_info = {}
            original_line_count = 0
            
            # 先計算原始行數
            original_line_count = self.count_csv_lines(csv_file)
            
            # 嘗試多種編碼和分隔符
            encodings = ['utf-8', 'utf-8-sig', 'gbk', 'big5', 'latin-1', 'cp1252', 'iso-8859-1']
            separators = [',', ';', '\t', '|']
            
            for encoding in encodings:
                for sep in separators:
                    try:
                        # 先檢測標題行位置
                        header_row, metadata = self.detect_header_row(csv_file, encoding, sep)
                        import pandas as pd
                        if header_row is not None:
                            # 使用檢測到的標題行讀取
                            df = pd.read_csv(csv_file, encoding=encoding, sep=sep,
                                            skiprows=header_row,
                                            engine='python', on_bad_lines='skip',
                                            keep_default_na=False, na_values=[''])
                            
                            if len(df) > 0:
                                encoding_used = encoding
                                separator_used = sep
                                header_row_index = header_row
                                metadata_rows = metadata
                                metadata_info = self.parse_metadata(metadata)
                                print(f"✓ 檢測到元數據行（前{header_row}行），使用編碼 {encoding} 和分隔符 '{sep}'")
                                break
                        else:
                            # 如果沒檢測到，嘗試第一行作為標題
                            df = pd.read_csv(csv_file, encoding=encoding, sep=sep, 
                                            engine='python', on_bad_lines='skip',
                                            keep_default_na=False, na_values=[''])
                            if len(df) > 0:
                                encoding_used = encoding
                                separator_used = sep
                                print(f"✓ 使用編碼 {encoding} 和分隔符 '{sep}' 讀取檔案（無元數據行）")
                                break
                    except (UnicodeDecodeError, pd.errors.EmptyDataError):
                        continue
                    except Exception as e:
                        continue
                
                if df is not None and len(df) > 0:
                    break
            
            # 如果還是失敗，嘗試自動檢測分隔符
            if df is None or len(df) == 0:
                for encoding in encodings:
                    try:
                        import pandas as pd
                        df = pd.read_csv(csv_file, encoding=encoding, sep=None, 
                                        engine='python', on_bad_lines='skip',
                                        keep_default_na=False, na_values=[''])
                        if len(df) > 0:
                            encoding_used = encoding
                            print(f"✓ 使用編碼 {encoding} (自動檢測分隔符) 讀取檔案")
                            break
                    except:
                        continue
            
            if df is None or len(df) == 0:
                raise Exception("無法讀取CSV檔案，請檢查檔案格式和編碼")
            
            # 驗證資料完整性
            print(f"  原始CSV行數: {original_line_count}, 讀取行數: {len(df)}, 列數: {len(df.columns)}")
            if original_line_count > 0 and len(df) < (original_line_count - 1) * 0.9:
                print(f"  ⚠️ 警告：讀取的行數可能少於原始檔案（可能因編碼或格式問題）")
            
            # 將元數據信息附加到DataFrame
            df.attrs['metadata'] = metadata_info
            df.attrs['header_row'] = header_row_index
            df.attrs['metadata_rows'] = metadata_rows
            
            # 創建新的Excel檔案
            output_file = self.create_output_filename(csv_file)
            self.create_formatted_excel(df, output_file, csv_file)
            
        except Exception as e:
            error_msg = f"處理CSV檔案 {os.path.basename(csv_file)} 失敗: {e}"
            print(error_msg)
            messagebox.showerror("錯誤", error_msg)
    
    def count_csv_lines(self, csv_file):
        """計算CSV檔案的原始行數（用於驗證）"""
        try:
            encodings = ['utf-8', 'utf-8-sig', 'gbk', 'big5', 'latin-1', 'cp1252']
            for encoding in encodings:
                try:
                    with open(csv_file, 'r', encoding=encoding, errors='ignore') as f:
                        return sum(1 for _ in f)
                except:
                    continue
            return 0
        except:
            return 0
    
    def create_output_filename(self, csv_file):
        """創建輸出檔案名稱"""
        base_name = os.path.splitext(os.path.basename(csv_file))[0]
        return os.path.join(self.analysis_dir, f"{base_name}_Analysis_CSV.xlsx")
    
    def create_formatted_excel(self, df, output_file, csv_file):
        """創建格式化的Excel檔案 - 增強版報表"""
        from openpyxl import Workbook
        wb = Workbook()
        
        # 獲取元數據信息
        metadata_info = df.attrs.get('metadata', {})
        metadata_rows = df.attrs.get('metadata_rows', [])
        
        # 創建主要數據工作表（放在第一個）
        ws_data = wb.active
        ws_data.title = "📋 數據明細"
        self.create_data_sheet(ws_data, df)
        
        # 創建統計摘要工作表
        ws_summary = wb.create_sheet("📊 統計摘要", 0)
        self.create_summary_sheet(ws_summary, df, csv_file, metadata_info, metadata_rows)
        
        # 儲存檔案
        wb.save(output_file)
        print(f"✓ 已處理並儲存: {os.path.basename(output_file)}")
    
    def create_summary_sheet(self, ws, df, csv_file, metadata_info=None, metadata_rows=None):
        """創建統計摘要工作表 - 改進版，支持元數據和錯誤代碼分類"""
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        if metadata_info is None:
            metadata_info = {}
        if metadata_rows is None:
            metadata_rows = []
        # 樣式定義
        title_font = Font(bold=True, size=14, color="FFFFFF")
        header_font = Font(bold=True, size=11, color="FFFFFF")
        normal_font = Font(size=10)
        title_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_fill = PatternFill(start_color="5B9BD5", end_color="5B9BD5", fill_type="solid")
        info_fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
        pass_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
        fail_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        current_row = 1
        
        # 標題
        ws.merge_cells(f'A{current_row}:D{current_row}')
        title_cell = ws.cell(row=current_row, column=1, value="📊 CSV 數據分析報表")
        title_cell.fill = title_fill
        title_cell.font = title_font
        title_cell.alignment = Alignment(horizontal='center', vertical='center')
        current_row += 2
        
        # 元數據信息（如果有）
        if metadata_info or metadata_rows:
            ws.cell(row=current_row, column=1, value="📋 元數據信息:").font = Font(bold=True, size=11, color="4472C4")
            current_row += 1
            
            if metadata_info.get('contact'):
                contact_text = metadata_info['contact'][:100]  # 限制長度
                ws.cell(row=current_row, column=1, value="聯繫信息:").font = Font(bold=True, size=10)
                ws.cell(row=current_row, column=2, value=contact_text).font = normal_font
                ws.merge_cells(f'B{current_row}:D{current_row}')
                current_row += 1
            
            if metadata_info.get('limits', {}).get('upper'):
                ws.cell(row=current_row, column=1, value="上限值:").font = Font(bold=True, size=10)
                ws.cell(row=current_row, column=2, value=metadata_info['limits']['upper']).font = normal_font
                ws.merge_cells(f'B{current_row}:D{current_row}')
                current_row += 1
            
            if metadata_info.get('limits', {}).get('lower'):
                ws.cell(row=current_row, column=1, value="下限值:").font = Font(bold=True, size=10)
                ws.cell(row=current_row, column=2, value=metadata_info['limits']['lower']).font = normal_font
                ws.merge_cells(f'B{current_row}:D{current_row}')
                current_row += 1
            
            current_row += 1
        
        # 檔案資訊
        ws.cell(row=current_row, column=1, value="檔案名稱:").font = Font(bold=True, size=10)
        ws.cell(row=current_row, column=2, value=os.path.basename(csv_file)).font = normal_font
        current_row += 1
        
        ws.cell(row=current_row, column=1, value="處理時間:").font = Font(bold=True, size=10)
        ws.cell(row=current_row, column=2, value=datetime.now().strftime('%Y-%m-%d %H:%M:%S')).font = normal_font
        current_row += 1
        
        ws.cell(row=current_row, column=1, value="總行數:").font = Font(bold=True, size=10)
        ws.cell(row=current_row, column=2, value=f"{len(df):,}").font = normal_font
        current_row += 1
        
        ws.cell(row=current_row, column=1, value="總列數:").font = Font(bold=True, size=10)
        ws.cell(row=current_row, column=2, value=f"{len(df.columns)}").font = normal_font
        current_row += 2
        
        # 統計數據（包含錯誤代碼分類）
        pass_count = 0
        fail_count = 0
        fail_codes = {}  # 錯誤代碼統計 {錯誤代碼: 數量}
        
        for _, row in df.iterrows():
            if self.is_pass_row(row):
                pass_count += 1
            elif self.is_fail_row(row):
                fail_count += 1
                # 提取錯誤代碼
                fail_code = self.extract_fail_code(row)
                if fail_code:
                    fail_codes[fail_code] = fail_codes.get(fail_code, 0) + 1
                else:
                    fail_codes['未知錯誤'] = fail_codes.get('未知錯誤', 0) + 1
        
        total_count = len(df)
        other_count = total_count - pass_count - fail_count
        
        # 統計表格標題
        ws.cell(row=current_row, column=1, value="項目").fill = header_fill
        ws.cell(row=current_row, column=1).font = header_font
        ws.cell(row=current_row, column=1).border = border
        ws.cell(row=current_row, column=1).alignment = Alignment(horizontal='center', vertical='center')
        
        ws.cell(row=current_row, column=2, value="數量").fill = header_fill
        ws.cell(row=current_row, column=2).font = header_font
        ws.cell(row=current_row, column=2).border = border
        ws.cell(row=current_row, column=2).alignment = Alignment(horizontal='center', vertical='center')
        
        ws.cell(row=current_row, column=3, value="百分比").fill = header_fill
        ws.cell(row=current_row, column=3).font = header_font
        ws.cell(row=current_row, column=3).border = border
        ws.cell(row=current_row, column=3).alignment = Alignment(horizontal='center', vertical='center')
        current_row += 1
        
        # PASS統計
        ws.cell(row=current_row, column=1, value="✓ PASS").fill = pass_fill
        ws.cell(row=current_row, column=1).font = Font(bold=True, size=10)
        ws.cell(row=current_row, column=1).border = border
        ws.cell(row=current_row, column=2, value=pass_count).fill = pass_fill
        ws.cell(row=current_row, column=2).font = normal_font
        ws.cell(row=current_row, column=2).border = border
        ws.cell(row=current_row, column=2).alignment = Alignment(horizontal='center')
        percentage = (pass_count / total_count * 100) if total_count > 0 else 0
        ws.cell(row=current_row, column=3, value=f"{percentage:.1f}%").fill = pass_fill
        ws.cell(row=current_row, column=3).font = normal_font
        ws.cell(row=current_row, column=3).border = border
        ws.cell(row=current_row, column=3).alignment = Alignment(horizontal='center')
        current_row += 1
        
        # FAIL統計
        ws.cell(row=current_row, column=1, value="✗ FAIL").fill = fail_fill
        ws.cell(row=current_row, column=1).font = Font(bold=True, size=10)
        ws.cell(row=current_row, column=1).border = border
        ws.cell(row=current_row, column=2, value=fail_count).fill = fail_fill
        ws.cell(row=current_row, column=2).font = normal_font
        ws.cell(row=current_row, column=2).border = border
        ws.cell(row=current_row, column=2).alignment = Alignment(horizontal='center')
        percentage = (fail_count / total_count * 100) if total_count > 0 else 0
        ws.cell(row=current_row, column=3, value=f"{percentage:.1f}%").fill = fail_fill
        ws.cell(row=current_row, column=3).font = normal_font
        ws.cell(row=current_row, column=3).border = border
        ws.cell(row=current_row, column=3).alignment = Alignment(horizontal='center')
        current_row += 1
        
        # 其他統計
        if other_count > 0:
            ws.cell(row=current_row, column=1, value="○ 其他").fill = info_fill
            ws.cell(row=current_row, column=1).font = Font(bold=True, size=10)
            ws.cell(row=current_row, column=1).border = border
            ws.cell(row=current_row, column=2, value=other_count).fill = info_fill
            ws.cell(row=current_row, column=2).font = normal_font
            ws.cell(row=current_row, column=2).border = border
            ws.cell(row=current_row, column=2).alignment = Alignment(horizontal='center')
            percentage = (other_count / total_count * 100) if total_count > 0 else 0
            ws.cell(row=current_row, column=3, value=f"{percentage:.1f}%").fill = info_fill
            ws.cell(row=current_row, column=3).font = normal_font
            ws.cell(row=current_row, column=3).border = border
            ws.cell(row=current_row, column=3).alignment = Alignment(horizontal='center')
            current_row += 1
        
        # 總計
        ws.cell(row=current_row, column=1, value="總計").fill = header_fill
        ws.cell(row=current_row, column=1).font = header_font
        ws.cell(row=current_row, column=1).border = border
        ws.cell(row=current_row, column=2, value=total_count).fill = header_fill
        ws.cell(row=current_row, column=2).font = header_font
        ws.cell(row=current_row, column=2).border = border
        ws.cell(row=current_row, column=2).alignment = Alignment(horizontal='center')
        ws.cell(row=current_row, column=3, value="100.0%").fill = header_fill
        ws.cell(row=current_row, column=3).font = header_font
        ws.cell(row=current_row, column=3).border = border
        ws.cell(row=current_row, column=3).alignment = Alignment(horizontal='center')
        current_row += 2
        
        # 錯誤代碼分類統計（如果有）
        if fail_codes:
            ws.cell(row=current_row, column=1, value="🔍 錯誤代碼分類:").font = Font(bold=True, size=11, color="FF0000")
            current_row += 1
            
            # 錯誤代碼表格標題
            ws.cell(row=current_row, column=1, value="錯誤代碼").fill = header_fill
            ws.cell(row=current_row, column=1).font = header_font
            ws.cell(row=current_row, column=1).border = border
            ws.cell(row=current_row, column=1).alignment = Alignment(horizontal='center', vertical='center')
            
            ws.cell(row=current_row, column=2, value="數量").fill = header_fill
            ws.cell(row=current_row, column=2).font = header_font
            ws.cell(row=current_row, column=2).border = border
            ws.cell(row=current_row, column=2).alignment = Alignment(horizontal='center', vertical='center')
            
            ws.cell(row=current_row, column=3, value="百分比").fill = header_fill
            ws.cell(row=current_row, column=3).font = header_font
            ws.cell(row=current_row, column=3).border = border
            ws.cell(row=current_row, column=3).alignment = Alignment(horizontal='center', vertical='center')
            current_row += 1
            
            # 按數量排序錯誤代碼
            sorted_codes = sorted(fail_codes.items(), key=lambda x: x[1], reverse=True)
            
            for code, count in sorted_codes:
                ws.cell(row=current_row, column=1, value=code).fill = fail_fill
                ws.cell(row=current_row, column=1).font = Font(bold=True, size=10)
                ws.cell(row=current_row, column=1).border = border
                
                ws.cell(row=current_row, column=2, value=count).fill = fail_fill
                ws.cell(row=current_row, column=2).font = normal_font
                ws.cell(row=current_row, column=2).border = border
                ws.cell(row=current_row, column=2).alignment = Alignment(horizontal='center')
                
                percentage = (count / fail_count * 100) if fail_count > 0 else 0
                ws.cell(row=current_row, column=3, value=f"{percentage:.1f}%").fill = fail_fill
                ws.cell(row=current_row, column=3).font = normal_font
                ws.cell(row=current_row, column=3).border = border
                ws.cell(row=current_row, column=3).alignment = Alignment(horizontal='center')
                current_row += 1
            
            current_row += 1
        
        # 欄位資訊
        ws.cell(row=current_row, column=1, value="欄位列表:").font = Font(bold=True, size=11)
        current_row += 1
        
        ws.cell(row=current_row, column=1, value="欄位名稱").fill = header_fill
        ws.cell(row=current_row, column=1).font = header_font
        ws.cell(row=current_row, column=1).border = border
        ws.cell(row=current_row, column=2, value="資料類型").fill = header_fill
        ws.cell(row=current_row, column=2).font = header_font
        ws.cell(row=current_row, column=2).border = border
        ws.cell(row=current_row, column=3, value="非空值數量").fill = header_fill
        ws.cell(row=current_row, column=3).font = header_font
        ws.cell(row=current_row, column=3).border = border
        current_row += 1
        
        for col in df.columns:
            ws.cell(row=current_row, column=1, value=str(col)).font = normal_font
            ws.cell(row=current_row, column=1).border = border
            ws.cell(row=current_row, column=2, value=str(df[col].dtype)).font = normal_font
            ws.cell(row=current_row, column=2).border = border
            non_null_count = df[col].notna().sum()
            ws.cell(row=current_row, column=3, value=non_null_count).font = normal_font
            ws.cell(row=current_row, column=3).border = border
            ws.cell(row=current_row, column=3).alignment = Alignment(horizontal='center')
            current_row += 1
        
        # 調整欄寬
        ws.column_dimensions['A'].width = 20
        ws.column_dimensions['B'].width = 15
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 30
    
    def create_data_sheet(self, ws, df):
        """創建數據明細工作表"""
        # 樣式定義
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
        pass_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")  # 淺綠色
        fail_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")  # 淺紅色
        warning_fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")  # 淺黃色
        header_fill = PatternFill(start_color="5B9BD5", end_color="5B9BD5", fill_type="solid")  # 淺藍色
        header_font = Font(bold=True, size=11, color="FFFFFF")
        normal_font = Font(size=10)
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # 寫入標題行（確保正確處理標題）
        headers = []
        for col in df.columns:
            # 清理標題，移除可能的特殊字符和空白
            header_str = str(col).strip()
            # 確保標題不為空
            if not header_str:
                header_str = f"欄位{len(headers)+1}"
            headers.append(header_str)
        
        # 寫入標題行
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = border
        
        # 寫入資料並設定樣式
        for row_num, (_, row) in enumerate(df.iterrows(), 2):
            row_is_pass = self.is_pass_row(row)
            row_is_fail = self.is_fail_row(row)
            fail_code = None
            
            if row_is_fail:
                fail_code = self.extract_fail_code(row)
            
            for col_num, value in enumerate(row, 1):
                cell = ws.cell(row=row_num, column=col_num)
                
                # 處理文字內容（保留完整內容，不截斷）
                if pd.notna(value) and str(value).strip():
                    cell.value = str(value)
                else:
                    cell.value = ""
                
                cell.border = border
                
                # 根據內容判斷PASS/FAIL並設定顏色和字體
                if row_is_pass:
                    cell.fill = pass_fill
                    cell.font = normal_font
                elif row_is_fail:
                    cell.fill = fail_fill
                    # FAIL行使用粗體字體以突出顯示
                    cell.font = Font(size=10, bold=True)
                else:
                    cell.font = normal_font
                
                # 設定文字對齊（數字右對齊，文字左對齊）
                try:
                    float(str(value))
                    cell.alignment = Alignment(horizontal='right', vertical='center', wrap_text=True)
                except (ValueError, TypeError):
                    cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
        
        # 自動調整欄寬（優化版本）
        self.auto_adjust_column_width_optimized(ws)
        
        # 設定行高
        ws.row_dimensions[1].height = 25  # 標題行更高
        for row_idx in range(2, len(df) + 2):
            ws.row_dimensions[row_idx].height = 18
        
        # 凍結第一行（標題行）
        ws.freeze_panes = 'A2'
        
        # 啟用自動篩選（確保標題行正確）
        if len(df) > 0 and len(headers) > 0:
            last_col = get_column_letter(len(headers))
            last_row = len(df) + 1
            ws.auto_filter.ref = f"A1:{last_col}{last_row}"
    
    def is_pass_row(self, row):
        """判斷是否為PASS行 - 改進版，更精確的判斷"""
        pass_keywords = ['PASS', 'OK', 'SUCCESS', 'TRUE', 'PASSED', 'YES', 'Y']
        pass_phrases = ['TEST PASS', 'TEST OK', 'RESULT PASS', 'STATUS PASS', 'PASSED TEST', 'IS PASS']
        
        row_str = ' '.join([str(v) for v in row if pd.notna(v)]).upper()
        
        # 優先檢查完整短語（避免誤判）
        for phrase in pass_phrases:
            if phrase in row_str:
                return True
        
        # 檢查關鍵字（但排除包含FAIL的情況）
        if 'FAIL' in row_str:
            return False
        
        for value in row:
            if pd.notna(value):
                value_str = str(value).upper().strip()
                # 精確匹配關鍵字（避免部分匹配）
                for keyword in pass_keywords:
                    # 完整單詞匹配或獨立存在
                    if (keyword == value_str or 
                        f' {keyword} ' in f' {value_str} ' or
                        value_str.startswith(keyword + ' ') or
                        value_str.endswith(' ' + keyword)):
                        return True
        
        return False
    
    def is_fail_row(self, row):
        """判斷是否為FAIL行 - 改進版，支持FAIL:錯誤代碼格式"""
        # 優先檢查test_result列（如果存在）
        if hasattr(row, 'index') and 'test_result' in row.index:
            result = str(row['test_result']).strip()
            result_upper = result.upper()
            # 檢查FAIL:格式（如FAIL:BSFI15, FAIL:BSFE01）
            if result_upper.startswith('FAIL'):
                return True
        
        fail_keywords = ['FAIL', 'ERROR', 'NACK', 'TIMEOUT', 'FALSE', 'NO', 'N', 'ABORT', 'ABORTED']
        fail_phrases = ['TEST FAIL', 'TEST ERROR', 'RESULT FAIL', 'STATUS FAIL', 'FAILED TEST', 
                       'IS FAIL', 'EXECUTES FAIL', "DOESN'T MATCH", 'TEST ABORTED']
        
        row_str = ' '.join([str(v) for v in row if pd.notna(v)]).upper()
        
        # 優先檢查完整短語（避免誤判）
        for phrase in fail_phrases:
            if phrase in row_str:
                return True
        
        # 檢查FAIL:格式（支持錯誤代碼）
        if 'FAIL:' in row_str:
            return True
        
        # 檢查關鍵字
        for value in row:
            if pd.notna(value):
                value_str = str(value).upper().strip()
                # 精確匹配關鍵字
                for keyword in fail_keywords:
                    # 完整單詞匹配或獨立存在
                    if (keyword == value_str or 
                        f' {keyword} ' in f' {value_str} ' or
                        value_str.startswith(keyword + ' ') or
                        value_str.endswith(' ' + keyword)):
                        # 排除包含PASS的情況（避免誤判）
                        if 'PASS' not in value_str:
                            return True
        
        # 檢查數值狀態碼（常見的錯誤碼）
        for value in row:
            if pd.notna(value):
                try:
                    num_val = float(str(value))
                    # 如果數值為負數，可能是錯誤狀態
                    if num_val < 0:
                        return True
                except (ValueError, TypeError):
                    pass
        
        return False
    
    def extract_fail_code(self, row):
        """從行中提取FAIL錯誤代碼（如BSFI15, BSFE01）"""
        # 優先檢查test_result列
        if hasattr(row, 'index') and 'test_result' in row.index:
            result = str(row['test_result']).strip()
            if 'FAIL:' in result.upper():
                # 提取FAIL:後面的錯誤代碼
                parts = result.split(':')
                if len(parts) > 1:
                    return parts[1].strip()
        
        # 檢查整行
        row_str = ' '.join([str(v) for v in row if pd.notna(v)])
        if 'FAIL:' in row_str.upper():
            import re
            match = re.search(r'FAIL:\s*([A-Z0-9]+)', row_str, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def auto_adjust_column_width_optimized(self, ws):
        """優化的自動調整欄寬功能"""
        for column in ws.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            
            # 只檢查前100行以提升性能（標題行+前100行數據）
            cells_to_check = list(column[:101]) if len(column) > 101 else list(column)
            
            for cell in cells_to_check:
                try:
                    if cell.value:
                        # 計算文字長度（考慮中文字符）
                        text_length = len(str(cell.value))
                        
                        # 中文字符權重調整（中文字符通常更寬）
                        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', str(cell.value)))
                        adjusted_length = text_length + chinese_chars * 0.8
                        
                        if adjusted_length > max_length:
                            max_length = adjusted_length
                except:
                    pass
            
            # 設定欄寬（優化計算）
            if max_length == 0:
                adjusted_width = 10
            elif max_length < 10:
                adjusted_width = max_length + 2
            elif max_length <= 20:
                adjusted_width = max_length + 3
            elif max_length <= 50:
                adjusted_width = max_length + 4
            else:
                # 對於很長的內容，設定合理上限，但允許更寬
                adjusted_width = min(max_length + 5, 80)
            
            # 設定最小和最大寬度
            adjusted_width = max(adjusted_width, 8)  # 最小寬度
            adjusted_width = min(adjusted_width, 80)  # 最大寬度（增加到80）
            
            ws.column_dimensions[column_letter].width = adjusted_width
    
    def create_progress_window(self):
        """創建進度視窗"""
        return ProgressWindow(self.app.root, "處理CSV檔案")

class ProgressWindow:
    def __init__(self, parent, title):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("400x150")
        self.window.resizable(False, False)
        
        # 進度條
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.window, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(pady=20, padx=20, fill=tk.X)
        
        # 狀態標籤
        self.status_label = tk.Label(self.window, text="準備中...", font=('Arial', 10))
        self.status_label.pack(pady=10)
        
        # 檔案名稱標籤
        self.file_label = tk.Label(self.window, text="", font=('Arial', 9), fg='gray')
        self.file_label.pack()
        
        self.window.update()
    
    def update_progress(self, current, total, filename):
        """更新進度"""
        progress = (current / total) * 100
        self.progress_var.set(progress)
        self.status_label.config(text=f"處理中... ({current}/{total})")
        self.file_label.config(text=f"當前檔案: {filename}")
        self.window.update()
    
    def complete(self):
        """完成處理"""
        self.progress_var.set(100)
        self.status_label.config(text="處理完成！")
        self.file_label.config(text="所有選中的CSV檔案已處理完成")
        
        # 3秒後自動關閉
        self.window.after(3000, self.window.destroy)

