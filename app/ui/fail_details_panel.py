# -*- coding: utf-8 -*-
"""
FailDetailsPanel组件 - FAIL详细资讯面板
"""
import tkinter as tk

class FailDetailsPanel:
    """FAIL詳細資訊面板"""
    
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """設定UI"""
        from tkinter import ttk
        # 標題
        title_label = ttk.Label(self.frame, text=" 🔴 錯誤完整區塊 ", 
                               font=('Arial', 12, 'bold'), style='danger.TLabel')
        title_label.pack(pady=(10, 5))
        
        # 錯誤內容文字框（可複製）
        self.error_text = tk.Text(self.frame, height=8, wrap=tk.WORD, 
                                 bg='#FFF0F0', fg='darkred', font=('Consolas', 10),
                                 relief=tk.FLAT, padx=5, pady=5)
        self.error_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 滾動條
        scrollbar = ttk.Scrollbar(self.frame, command=self.error_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.error_text.config(yscrollcommand=scrollbar.set)
    
    def show_error_details(self, error_content):
        """顯示錯誤詳細內容"""
        self.error_text.delete('1.0', tk.END)
        self.error_text.insert('1.0', error_content)
        self.error_text.config(state=tk.NORMAL)  # 允許複製
    
    def clear(self):
        """清空內容"""
        self.error_text.delete('1.0', tk.END)
