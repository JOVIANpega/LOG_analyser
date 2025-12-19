# -*- coding: utf-8 -*-
"""
EnhancedText组件 - 增强型Text元件
支援语法高亮和区段标签
"""
import tkinter as tk
from tkinter import messagebox
import re

class EnhancedText:
    """增強型Text元件，支援語法高亮和區段標籤"""
    
    def __init__(self, parent, **kwargs):
        # 創建框架來容納Text和滾動條
        self.frame = tk.Frame(parent)
        self.text = tk.Text(self.frame, **kwargs)
        self.setup_tags()
        self.step_positions = {}  # 儲存每個step的位置
        self.setup_search_functionality()
        self.setup_scrollbars()
    
    def setup_scrollbars(self):
        """設定滾動條"""
        # 垂直滾動條
        self.v_scrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.text.yview, width=20)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 水平滾動條
        self.h_scrollbar = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.text.xview, width=20)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 配置Text元件的滾動
        self.text.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def pack(self, **kwargs):
        """打包Text元件框架"""
        return self.frame.pack(**kwargs)
    
    def clear(self):
        """清空文字內容"""
        self.text.delete(1.0, tk.END)
        self.step_positions.clear()

    def append(self, text, tag=None):
        """追加文字內容並自動捲動"""
        try:
            self.text.insert(tk.END, str(text) + "\n", tag)
            self.text.see(tk.END)
        except Exception as e:
            print(f"Append text failed: {e}")
    
    def setup_tags(self):
        """設定文字標籤樣式"""
        # 行號樣式
        self.text.tag_configure('line_number', foreground='gray', font=('Consolas', 9))
        
        # Step區段背景色
        self.text.tag_configure('step_bg_1', background='#E8F4FD')  # 淺藍
        self.text.tag_configure('step_bg_2', background='#F0E8FF')  # 淺紫
        
        # PASS/FAIL文字顏色
        self.text.tag_configure('pass_text', foreground='green', font=('Arial', 10, 'bold'))
        self.text.tag_configure('fail_text', foreground='red', font=('Arial', 10, 'bold'))
        
        # 嚴重錯誤樣式
        self.text.tag_configure('critical_error', foreground='darkred', font=('Arial', 10, 'bold'), background='#FFE6E6')
        
        # 指令和回應樣式
        self.text.tag_configure('command', foreground='blue', font=('Arial', 9, 'bold'))
        self.text.tag_configure('response', foreground='purple', font=('Arial', 9))
        
        # 錯誤區塊樣式
        self.text.tag_configure('error_block', background='#FFE4E1', foreground='red')
        
        # Hover效果
        self.text.tag_configure('step_hover', background='#FFFF99')
        
        # 置頂Header樣式 (綠底黑字，放大)
        self.text.tag_configure('header_style', background='#90EE90', foreground='black', font=('Consolas', 14, 'bold'))
        
        # 綁定點擊事件
        self.text.tag_bind('step_clickable', '<Button-1>', self._on_step_click)
        self.text.tag_bind('step_clickable', '<Enter>', self._on_step_hover)
        self.text.tag_bind('step_clickable', '<Leave>', self._on_step_leave)
    
    def setup_search_functionality(self):
        """設定搜尋功能"""
        self.search_frame = None
        self.search_var = tk.StringVar()
        self.search_index = '1.0'
        
        # 綁定Ctrl+F
        self.text.bind('<Control-f>', self._show_search_dialog)
        self.text.bind('<Control-F>', self._show_search_dialog)
    
    def _show_search_dialog(self, event=None):
        """顯示搜尋對話框"""
        if self.search_frame:
            self.search_frame.destroy()
        
        # 創建搜尋框架
        from tkinter import ttk
        self.search_frame = ttk.Frame(self.text.master, style='secondary.TFrame')
        self.search_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        
        ttk.Label(self.search_frame, text=" 🔍 搜尋: ").pack(side=tk.LEFT, padx=5)
        
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.search_entry.focus()
        
        ttk.Button(self.search_frame, text="下一個", command=self._find_next, style='info.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(self.search_frame, text="上一個", command=self._find_prev, style='success.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(self.search_frame, text="關閉", command=self._close_search, style='danger.TButton').pack(side=tk.LEFT, padx=2)
        
        # 綁定Enter鍵
        self.search_entry.bind('<Return>', lambda e: self._find_next())
        self.search_entry.bind('<Escape>', lambda e: self._close_search())
        
        return "break"
    
    def _find_next(self):
        """尋找下一個"""
        search_text = self.search_var.get()
        if not search_text:
            return
        
        # 清除之前的高亮
        self.text.tag_remove('search_highlight', '1.0', tk.END)
        
        # 從當前位置開始搜尋
        pos = self.text.search(search_text, self.search_index, tk.END)
        if pos:
            # 計算結束位置
            end_pos = f"{pos}+{len(search_text)}c"
            
            # 高亮顯示
            self.text.tag_add('search_highlight', pos, end_pos)
            self.text.tag_configure('search_highlight', background='yellow', foreground='black')
            
            # 跳轉到該位置
            self.text.see(pos)
            self.text.mark_set(tk.INSERT, pos)
            
            # 更新搜尋位置
            self.search_index = end_pos
        else:
            # 從頭開始搜尋
            self.search_index = '1.0'
            # 避免遞歸調用，直接搜尋
            search_text = self.search_var.get()
            if search_text:
                pos = self.text.search(search_text, '1.0', stopindex=tk.END)
                if pos:
                    end_pos = f"{pos}+{len(search_text)}c"
                    self.text.tag_add('search_highlight', pos, end_pos)
                    self.text.see(pos)
                    self.text.mark_set(tk.INSERT, pos)
                    self.search_index = end_pos
                else:
                    messagebox.showinfo("搜尋結果", f"未找到 '{search_text}'")
    
    def _find_prev(self):
        """尋找上一個"""
        search_text = self.search_var.get()
        if not search_text:
            return
        
        # 清除之前的高亮
        self.text.tag_remove('search_highlight', '1.0', tk.END)
        
        # 從當前位置向前搜尋
        pos = self.text.search(search_text, self.search_index, '1.0', backwards=True)
        if pos:
            # 計算結束位置
            end_pos = f"{pos}+{len(search_text)}c"
            
            # 高亮顯示
            self.text.tag_add('search_highlight', pos, end_pos)
            self.text.tag_configure('search_highlight', background='yellow', foreground='black')
            
            # 跳轉到該位置
            self.text.see(pos)
            self.text.mark_set(tk.INSERT, pos)
            
            # 更新搜尋位置
            self.search_index = pos
        else:
            # 從末尾開始搜尋
            self.search_index = tk.END
            self._find_prev()
    
    def _close_search(self):
        """關閉搜尋框"""
        if self.search_frame:
            self.search_frame.destroy()
            self.search_frame = None
        
        # 清除高亮
        self.text.tag_remove('search_highlight', '1.0', tk.END)
        
        # 焦點回到文字框
        self.text.focus()
    
    def _on_step_click(self, event):
        """點擊step標籤跳轉"""
        # 獲取點擊的標籤內容
        index = self.text.index(tk.CURRENT)
        tags = self.text.tag_names(index)
        
        for tag in tags:
            if tag.startswith('step_'):
                step_name = tag.replace('step_', '').replace('_clickable', '')
                if step_name in self.step_positions:
                    self.jump_to_step(step_name)
                break
    
    def _on_step_hover(self, event):
        """step標籤hover效果"""
        index = self.text.index(tk.CURRENT)
        self.text.tag_add('step_hover', f"{index} linestart", f"{index} lineend")
        # 改變游標樣式
        self.text.config(cursor='hand2')
    
    def _on_step_leave(self, event):
        """移除hover效果"""
        self.text.tag_remove('step_hover', '1.0', tk.END)
        # 恢復游標樣式
        self.text.config(cursor='xterm')
    
    def insert_log_with_highlighting(self, log_content, test_results, header_content=None):
        """插入log內容並進行語法高亮"""
        self.text.delete('1.0', tk.END)
        self.step_positions.clear()
        
        # 插入置頂資訊 (Header)
        if header_content:
            self.text.insert(tk.INSERT, header_content + "\n", 'header_style')
            self.text.insert(tk.INSERT, "\n") # 空一行
        
        if not log_content:
            return
            
        lines = log_content.split('\n')
        current_step = None
        step_counter = 0
        bg_toggle = True
        
        for i, line in enumerate(lines):
            line_start = self.text.index(tk.INSERT)
            line_number = i + 1
            
            # 插入行號
            self.text.insert(tk.INSERT, f"{line_number:4d} ")
            self.text.tag_add('line_number', line_start, self.text.index(tk.INSERT))
            
            # 檢查是否為新的step
            step_match = re.search(r'Do @STEP\d+@([^@\n]+)', line)
            if step_match:
                current_step = step_match.group(1).strip()
                step_counter += 1
                bg_toggle = not bg_toggle
                
                # 記錄step位置
                self.step_positions[current_step] = line_start
                
                # 插入可點擊的step標籤
                self.text.insert(tk.INSERT, line + '\n')
                line_end = self.text.index(tk.INSERT)
                
                # 設定背景色
                bg_tag = 'step_bg_1' if bg_toggle else 'step_bg_2'
                self.text.tag_add(bg_tag, line_start, line_end)
                
                # 設定可點擊標籤
                step_tag = f"step_{current_step}_clickable"
                self.text.tag_add(step_tag, line_start, line_end)
                self.text.tag_add('step_clickable', line_start, line_end)
                
                continue
            
            # 檢查指令行
            if '>' in line:
                self.text.insert(tk.INSERT, line + '\n')
                line_end = self.text.index(tk.INSERT)
                self.text.tag_add('command', line_start, line_end)
                continue
            
            # 檢查回應行
            if '<' in line:
                self.text.insert(tk.INSERT, line + '\n')
                line_end = self.text.index(tk.INSERT)
                self.text.tag_add('response', line_start, line_end)
                continue
            
            # 檢查PASS/FAIL結果
            if 'Test is Pass' in line:
                self.text.insert(tk.INSERT, line + '\n')
                line_end = self.text.index(tk.INSERT)
                self.text.tag_add('pass_text', line_start, line_end)
                continue
            elif 'Test is Fail' in line or 'FAIL' in line or 'ERROR' in line:
                self.text.insert(tk.INSERT, line + '\n')
                line_end = self.text.index(tk.INSERT)
                self.text.tag_add('fail_text', line_start, line_end)
                continue
            
            # 檢查其他錯誤關鍵字
            line_lower = line.lower()
            if any(critical_error in line_lower for critical_error in [
                'segmentation fault', 'core dumped', 'executes fail', 
                "doesn't match", 'timeout', 'exception', 'wrong'
            ]):
                self.text.insert(tk.INSERT, line + '\n')
                line_end = self.text.index(tk.INSERT)
                self.text.tag_add('critical_error', line_start, line_end)
                continue
            
            # 一般行
            self.text.insert(tk.INSERT, line + '\n')
    
    def jump_to_step(self, step_name):
        """跳轉到指定step"""
        if step_name in self.step_positions:
            position = self.step_positions[step_name]
            self.text.see(position)
            self.text.mark_set(tk.INSERT, position)
    
    def highlight_error_block(self, start_line, end_line):
        """高亮錯誤區塊"""
        # 如果有Header，行號會有偏移。
        # 簡單做法：重新計算位置或是讓使用者直接看文字，不特別依賴行號跳轉的精確度
        # 或者在插入 Header 時記錄行數
        # 暫時假設 start_line 是 log 的行號，需要加上 Header 的行數
        # 這裡先保持原樣，因為 EnhancedText 中行號是自己生成的，但 `see` 是看 index
        # 如果上方插入了 Header，原始的 "1.0" 會變成 "HeaderLines + 1.0"
        # 但我們下面是直接用 `start_line` 也就是 log 的行號去對應，Text widget 的行號是絕對的
        # 所以如果插入 Header，log 的第一行可能變成第 6 行
        # 因此這部分邏輯可能有問題，需要修正。
        # 為了安全，暫時不修改 highlight_error_block，而是讓 insert 完後回傳 log 起始行？.
        # 更好的方式： header 插入後，搜尋 "1    " 這樣的行號標記？
        # 或者簡單點： header 不影響行號？ 不，Text widget 是連續的。
        # 修正策略：讓 highlight_error_block 搜尋對應的 Log 行號標記
        
        start_pos = f"{start_line}.0" # 這是絕對行號，如果有 Header 這會錯
        
        # 尋找含有該行號的文字
        # 格式是 "   1 "
        search_str = f"{start_line:4d} "
        found = self.text.search(search_str, '1.0', tk.END)
        if found:
            # found 就是該行的起始位置
            self.text.tag_add('error_block', found, f"{found} lineend")
            self.text.see(found)
        else:
            # Fallback
             pass

    def focus_first_error_line(self):
        """聚焦到第一個錯誤行"""
        try:
            # 獲取所有文字內容
            content = self.text.get('1.0', tk.END)
            lines = content.split('\n')
            
            # 尋找第一個包含錯誤關鍵字的行
            # 注意：這裡 lines 包含了 Header 和行號
            for i, line in enumerate(lines):
                line_lower = line.lower()
                # 排除 Header 行 (通常 Header 沒有行號前綴)
                # 我們可以檢查是否以數字開頭 (行號格式 "   1 ")
                if not re.match(r'\s*\d+\s', line):
                     continue

                if (any(critical_error in line_lower for critical_error in [
                    'segmentation fault', 'core dumped', 'executes fail', 
                    "doesn't match", 'timeout', 'exception', 'wrong'
                ]) or 'is fail' in line_lower or 'is failed' in line_lower):
                    # 跳轉到該行
                    line_num = i + 1
                    self.text.see(f"{line_num}.0")
                    self.text.mark_set(tk.INSERT, f"{line_num}.0")
                    # 避免 Header 誤判，這一行必須包含行號
                    break
        except Exception as e:
            print(f"聚焦錯誤行失敗: {e}")

