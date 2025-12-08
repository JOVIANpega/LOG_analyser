#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試Log分析器GUI應用程式
提供現代化的圖形使用者介面來分析測試log檔案
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from datetime import datetime
from log_analyzer import LogAnalyzer
import pandas as pd

class LogAnalyzerGUI:
    """
    測試Log分析器GUI類別
    提供完整的圖形使用者介面功能
    """
    
    def __init__(self, root):
        """
        初始化GUI應用程式
        
        Args:
            root: tkinter根視窗
        """
        self.root = root
        self.root.title("測試Log分析器 v1.0")
        self.root.geometry("1200x800")
        
        # 初始化分析器
        self.analyzer = LogAnalyzer()
        
        # 設定變數
        self.log_path = tk.StringVar()
        self.script_path = tk.StringVar()
        self.analysis_running = False
        
        # 建立GUI元件
        self._create_widgets()
        self._setup_styles()
        
        # 綁定事件
        self._bind_events()
    
    def _create_widgets(self):
        """建立GUI元件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 設定網格權重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 標題
        title_label = ttk.Label(main_frame, text="測試Log分析器", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 檔案選擇區域
        self._create_file_selection(main_frame)
        
        # 控制按鈕區域
        self._create_control_buttons(main_frame)
        
        # 分頁控制
        self._create_notebook(main_frame)
        
        # 狀態列
        self._create_status_bar(main_frame)
    
    def _create_file_selection(self, parent):
        """建立檔案選擇區域"""
        # Log檔案選擇
        log_frame = ttk.LabelFrame(parent, text="Log檔案選擇", padding="10")
        log_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        log_frame.columnconfigure(1, weight=1)
        
        ttk.Label(log_frame, text="Log檔案/資料夾:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(log_frame, textvariable=self.log_path, width=50).grid(row=0, column=1, padx=(10, 5), sticky=(tk.W, tk.E))
        ttk.Button(log_frame, text="選擇檔案", command=self._select_log_file).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(log_frame, text="選擇資料夾", command=self._select_log_directory).grid(row=0, column=3)
        
        # 腳本檔案選擇
        script_frame = ttk.LabelFrame(parent, text="測試腳本選擇 (可選)", padding="10")
        script_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        script_frame.columnconfigure(1, weight=1)
        
        ttk.Label(script_frame, text="Excel腳本檔案:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(script_frame, textvariable=self.script_path, width=50).grid(row=0, column=1, padx=(10, 5), sticky=(tk.W, tk.E))
        ttk.Button(script_frame, text="選擇檔案", command=self._select_script_file).grid(row=0, column=2)
    
    def _create_control_buttons(self, parent):
        """建立控制按鈕區域"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        # 移除開始分析按鈕 - 改為自動分析
        
        self.export_button = ttk.Button(button_frame, text="匯出Excel", 
                                       command=self._export_excel, state="disabled")
        self.export_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="清除結果", 
                                      command=self._clear_results)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 進度條
        self.progress = ttk.Progressbar(button_frame, mode='indeterminate')
        self.progress.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
    
    def _create_notebook(self, parent):
        """建立分頁控制"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # PASS測試分頁
        self.pass_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.pass_frame, text="✅ PASS測試")
        self._create_pass_tab()
        
        # FAIL測試分頁
        self.fail_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.fail_frame, text="❌ FAIL測試")
        self._create_fail_tab()
        
        # 腳本比對分頁
        self.compare_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.compare_frame, text="📊 腳本比對")
        self._create_compare_tab()
        
        # 原始Log分頁
        self.raw_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.raw_frame, text="📄 原始Log")
        self._create_raw_tab()
    
    def _create_pass_tab(self):
        """建立PASS測試分頁"""
        # 建立Treeview
        columns = ('Step Name', 'Test ID', '指令', '回應', '執行時間(秒)')
        self.pass_tree = ttk.Treeview(self.pass_frame, columns=columns, show='headings', height=15)
        
        # 設定欄位標題
        for col in columns:
            self.pass_tree.heading(col, text=col)
            self.pass_tree.column(col, width=150)
        
        # 捲軸
        pass_scrollbar = ttk.Scrollbar(self.pass_frame, orient=tk.VERTICAL, command=self.pass_tree.yview)
        self.pass_tree.configure(yscrollcommand=pass_scrollbar.set)
        
        # 佈局
        self.pass_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        pass_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.pass_frame.columnconfigure(0, weight=1)
        self.pass_frame.rowconfigure(0, weight=1)
        
        # 統計標籤
        self.pass_stats_label = ttk.Label(self.pass_frame, text="PASS測試: 0 項")
        self.pass_stats_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
    
    def _create_fail_tab(self):
        """建立FAIL測試分頁"""
        # 建立Treeview
        columns = ('Step Name', 'Test ID', '指令', '錯誤回應', 'Retry次數', 'FAIL原因', '執行時間(秒)')
        self.fail_tree = ttk.Treeview(self.fail_frame, columns=columns, show='headings', height=15)
        
        # 設定欄位標題
        for col in columns:
            self.fail_tree.heading(col, text=col)
            self.fail_tree.column(col, width=120)
        
        # 捲軸
        fail_scrollbar = ttk.Scrollbar(self.fail_frame, orient=tk.VERTICAL, command=self.fail_tree.yview)
        self.fail_tree.configure(yscrollcommand=fail_scrollbar.set)
        
        # 佈局
        self.fail_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        fail_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.fail_frame.columnconfigure(0, weight=1)
        self.fail_frame.rowconfigure(0, weight=1)
        
        # 統計標籤
        self.fail_stats_label = ttk.Label(self.fail_frame, text="FAIL測試: 0 項")
        self.fail_stats_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
    
    def _create_compare_tab(self):
        """建立腳本比對分頁"""
        # 建立Treeview
        columns = ('Test ID', 'Status', 'Note')
        self.compare_tree = ttk.Treeview(self.compare_frame, columns=columns, show='headings', height=15)
        
        # 設定欄位標題
        for col in columns:
            self.compare_tree.heading(col, text=col)
            self.compare_tree.column(col, width=200)
        
        # 捲軸
        compare_scrollbar = ttk.Scrollbar(self.compare_frame, orient=tk.VERTICAL, command=self.compare_tree.yview)
        self.compare_tree.configure(yscrollcommand=compare_scrollbar.set)
        
        # 佈局
        self.compare_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        compare_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.compare_frame.columnconfigure(0, weight=1)
        self.compare_frame.rowconfigure(0, weight=1)
        
        # 統計標籤
        self.compare_stats_label = ttk.Label(self.compare_frame, text="腳本比對: 未載入腳本")
        self.compare_stats_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
    
    def _create_raw_tab(self):
        """建立原始Log分頁"""
        # 建立文字區域
        self.raw_text = scrolledtext.ScrolledText(self.raw_frame, wrap=tk.WORD, height=20)
        self.raw_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.raw_frame.columnconfigure(0, weight=1)
        self.raw_frame.rowconfigure(0, weight=1)
    
    def _create_status_bar(self, parent):
        """建立狀態列"""
        self.status_var = tk.StringVar()
        self.status_var.set("就緒")
        
        status_bar = ttk.Label(parent, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def _setup_styles(self):
        """設定GUI樣式"""
        style = ttk.Style()
        
        # 設定主題
        try:
            style.theme_use('clam')
        except:
            pass
        
        # 自訂按鈕樣式
        style.configure("Accent.TButton", background="#0078d4", foreground="white")
    
    def _bind_events(self):
        """綁定事件"""
        # 雙擊事件
        self.pass_tree.bind('<Double-1>', self._on_pass_double_click)
        self.fail_tree.bind('<Double-1>', self._on_fail_double_click)
        self.compare_tree.bind('<Double-1>', self._on_compare_double_click)
    
    def _select_log_file(self):
        """選擇Log檔案"""
        file_path = filedialog.askopenfilename(
            title="選擇Log檔案",
            filetypes=[("Log檔案", "*.log"), ("文字檔案", "*.txt"), ("所有檔案", "*.*")]
        )
        if file_path:
            self.log_path.set(file_path)
    
    def _select_log_directory(self):
        """選擇Log資料夾"""
        dir_path = filedialog.askdirectory(title="選擇Log資料夾")
        if dir_path:
            self.log_path.set(dir_path)
    
    def _select_script_file(self):
        """選擇腳本檔案"""
        file_path = filedialog.askopenfilename(
            title="選擇Excel腳本檔案",
            filetypes=[("Excel檔案", "*.xlsx *.xls"), ("所有檔案", "*.*")]
        )
        if file_path:
            self.script_path.set(file_path)
    
    def _start_analysis(self):
        """開始分析"""
        if not self.log_path.get():
            messagebox.showerror("錯誤", "請先選擇Log檔案或資料夾")
            return
        
        if self.analysis_running:
            return
        
        self.analysis_running = True
        self.analyze_button.config(state="disabled")
        self.progress.start()
        self.status_var.set("正在分析...")
        
        # 在新執行緒中執行分析
        thread = threading.Thread(target=self._run_analysis)
        thread.daemon = True
        thread.start()
    
    def _run_analysis(self):
        """執行分析（在背景執行緒中）"""
        try:
            # 清除舊結果
            self.analyzer.clear_results()
            
            # 載入Log檔案
            log_path = self.log_path.get()
            if os.path.isfile(log_path):
                success = self.analyzer.load_log_file(log_path)
            else:
                success = self.analyzer.load_log_directory(log_path)
            
            if not success:
                self.root.after(0, lambda: messagebox.showerror("錯誤", "無法載入Log檔案"))
                return
            
            # 載入腳本檔案（如果有的話）
            if self.script_path.get():
                self.analyzer.load_script_excel(self.script_path.get())
            
            # 解析測試步驟
            pass_tests, fail_tests = self.analyzer.parse_test_steps()
            
            # 更新UI（在主執行緒中）
            self.root.after(0, lambda: self._update_ui(pass_tests, fail_tests))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("錯誤", f"分析過程中發生錯誤: {str(e)}"))
        finally:
            self.root.after(0, self._analysis_completed)
    
    def _update_ui(self, pass_tests, fail_tests):
        """更新UI顯示"""
        # 更新PASS測試
        self.pass_tree.delete(*self.pass_tree.get_children())
        for test in pass_tests:
            commands_str = "; ".join(test['commands']) if test['commands'] else ""
            responses_str = "; ".join(test['responses']) if test['responses'] else ""
            
            self.pass_tree.insert('', 'end', values=(
                test['step_name'],
                test['test_id'],
                commands_str,
                responses_str,
                f"{test['execution_time']:.3f}"
            ))
        
        # 更新FAIL測試
        self.fail_tree.delete(*self.fail_tree.get_children())
        for test in fail_tests:
            commands_str = "; ".join(test['commands']) if test['commands'] else ""
            responses_str = "; ".join(test['responses']) if test['responses'] else ""
            
            self.fail_tree.insert('', 'end', values=(
                test['step_name'],
                test['test_id'],
                commands_str,
                responses_str,
                test['retry_count'],
                test['error_message'],
                f"{test['execution_time']:.3f}"
            ))
        
        # 更新統計標籤
        self.pass_stats_label.config(text=f"PASS測試: {len(pass_tests)} 項")
        self.fail_stats_label.config(text=f"FAIL測試: {len(fail_tests)} 項")
        
        # 更新腳本比對
        self._update_compare_tab()
        
        # 更新原始Log
        self.raw_text.delete(1.0, tk.END)
        self.raw_text.insert(1.0, self.analyzer.log_content)
        
        # 啟用匯出按鈕
        self.export_button.config(state="normal")
    
    def _update_compare_tab(self):
        """更新腳本比對分頁"""
        self.compare_tree.delete(*self.compare_tree.get_children())
        
        if not self.analyzer.script_tests:
            self.compare_stats_label.config(text="腳本比對: 未載入腳本")
            return
        
        comparison = self.analyzer.compare_with_script()
        
        # 已執行且通過的測試
        for test_id in comparison.get('executed_pass', []):
            self.compare_tree.insert('', 'end', values=(
                test_id, '✅ PASS', '已執行且通過'
            ))
        
        # 已執行但失敗的測試
        for test_id in comparison.get('executed_fail', []):
            self.compare_tree.insert('', 'end', values=(
                test_id, '❌ FAIL', '已執行但失敗'
            ))
        
        # 未執行的測試
        for test_id in comparison.get('not_executed', []):
            self.compare_tree.insert('', 'end', values=(
                test_id, '⚠️ NOT EXECUTED', '腳本中有但未執行'
            ))
        
        # 額外執行的測試
        for test_id in comparison.get('extra_executed', []):
            self.compare_tree.insert('', 'end', values=(
                test_id, '➕ EXTRA', '執行但腳本中沒有'
            ))
        
        total_tests = len(self.analyzer.pass_tests) + len(self.analyzer.fail_tests)
        pass_rate = f"{len(self.analyzer.pass_tests) / total_tests * 100:.1f}%" if total_tests > 0 else "0%"
        
        self.compare_stats_label.config(text=f"腳本比對: 總計 {total_tests} 項, 通過率 {pass_rate}")
    
    def _analysis_completed(self):
        """分析完成"""
        self.analysis_running = False
        self.analyze_button.config(state="normal")
        self.progress.stop()
        self.status_var.set("分析完成")
    
    def _export_excel(self):
        """匯出Excel檔案"""
        if not self.analyzer.pass_tests and not self.analyzer.fail_tests:
            messagebox.showwarning("警告", "沒有可匯出的資料")
            return
        
        # 選擇儲存位置
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"log_analysis_{timestamp}.xlsx"
        
        file_path = filedialog.asksaveasfilename(
            title="儲存Excel檔案",
            defaultextension=".xlsx",
            filetypes=[("Excel檔案", "*.xlsx")],
            initialfile=default_filename
        )
        
        if file_path:
            success = self.analyzer.export_to_excel(file_path)
            if success:
                messagebox.showinfo("成功", f"Excel檔案已匯出至:\n{file_path}")
                self.status_var.set("Excel匯出完成")
            else:
                messagebox.showerror("錯誤", "匯出Excel檔案失敗")
    
    def _clear_results(self):
        """清除結果"""
        self.analyzer.clear_results()
        
        # 清除所有Treeview
        self.pass_tree.delete(*self.pass_tree.get_children())
        self.fail_tree.delete(*self.fail_tree.get_children())
        self.compare_tree.delete(*self.compare_tree.get_children())
        self.raw_text.delete(1.0, tk.END)
        
        # 重置統計標籤
        self.pass_stats_label.config(text="PASS測試: 0 項")
        self.fail_stats_label.config(text="FAIL測試: 0 項")
        self.compare_stats_label.config(text="腳本比對: 未載入腳本")
        
        # 停用匯出按鈕
        self.export_button.config(state="disabled")
        
        # 清除檔案路徑
        self.log_path.set("")
        self.script_path.set("")
        
        self.status_var.set("已清除所有結果")
    
    def _on_pass_double_click(self, event):
        """PASS測試雙擊事件"""
        item = self.pass_tree.selection()[0]
        values = self.pass_tree.item(item, 'values')
        self._show_test_details("PASS測試詳細資訊", values)
    
    def _on_fail_double_click(self, event):
        """FAIL測試雙擊事件"""
        item = self.fail_tree.selection()[0]
        values = self.fail_tree.item(item, 'values')
        self._show_test_details("FAIL測試詳細資訊", values)
    
    def _on_compare_double_click(self, event):
        """比對結果雙擊事件"""
        item = self.compare_tree.selection()[0]
        values = self.compare_tree.item(item, 'values')
        self._show_test_details("測試比對詳細資訊", values)
    
    def _show_test_details(self, title, values):
        """顯示測試詳細資訊"""
        detail_window = tk.Toplevel(self.root)
        detail_window.title(title)
        
        # 設定最小和最大尺寸
        detail_window.minsize(400, 300)
        detail_window.maxsize(1000, 800)
        detail_window.geometry("600x400")
        
        # 讓視窗居中顯示
        detail_window.transient(self.root)
        detail_window.grab_set()
        detail_window.update_idletasks()
        
        text_widget = scrolledtext.ScrolledText(detail_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 顯示詳細資訊
        detail_text = f"測試詳細資訊:\n\n"
        for i, value in enumerate(values):
            detail_text += f"{value}\n"
        
        text_widget.insert(1.0, detail_text)
        text_widget.config(state=tk.DISABLED)
        
        # 自動調整視窗大小以適應內容
        self._auto_resize_detail_window(detail_window, text_widget)
    
    def _auto_resize_detail_window(self, detail_window, text_widget):
        """根據文字內容自動調整詳細視窗大小，確保導航按鈕始終可見"""
        try:
            # 獲取文字內容的行數和最大行寬度
            content = text_widget.get('1.0', tk.END)
            lines = content.split('\n')
            max_line_length = max(len(line) for line in lines) if lines else 0
            total_lines = len(lines)
            
            # 計算合適的視窗尺寸
            # 每行大約需要 8-10 像素寬度，每行大約需要 16-18 像素高度
            char_width = 8  # 每個字符的寬度
            char_height = 16  # 每行的高度
            
            # 計算文字區域的寬度和高度（更緊湊的計算）
            text_width = min(max_line_length * char_width + 80, 700)   # 減少邊距，最大700
            text_height = min(total_lines * char_height + 120, 500)    # 減少邊距，最大500
            
            # 設定視窗大小（更緊湊）
            window_width = max(400, text_width + 40)   # 減少額外寬度
            window_height = max(300, text_height + 80)  # 減少額外高度，確保導航按鈕可見
            
            # 限制最大尺寸（更嚴格，避免視窗過大）
            window_width = min(window_width, 800)   # 從1000減少到800
            window_height = min(window_height, 600)  # 從800減少到600
            
            # 更新視窗大小
            detail_window.geometry(f"{window_width}x{window_height}")
            
            # 重新居中視窗
            detail_window.update_idletasks()
            x = (detail_window.winfo_screenwidth() // 2) - (window_width // 2)
            y = (detail_window.winfo_screenheight() // 2) - (window_height // 2)
            detail_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
        except Exception as e:
            print(f"自動調整詳細視窗大小失敗: {e}")

def main():
    """主函數"""
    root = tk.Tk()
    app = LogAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 