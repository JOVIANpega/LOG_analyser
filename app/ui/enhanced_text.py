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
        self.folded_items = {}  # 儲存折疊項目的內容 {item_id: {'start': index, 'end': index, 'content': str, 'is_folded': bool, 'type': 'pass'/'fail'}}
        self.item_counter = 0  # 用於生成唯一 item_id
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
        self.text.tag_configure('pass_text', foreground='green', font=('Consolas', 11, 'bold'))
        self.text.tag_configure('fail_text', foreground='red', font=('Consolas', 11, 'bold'))
        
        # 嚴重錯誤樣式
        self.text.tag_configure('critical_error', foreground='darkred', font=('Consolas', 11, 'bold'), background='#FFE6E6')
        
        # 指令和回應樣式
        self.text.tag_configure('command', foreground='blue', font=('Consolas', 11, 'bold'))
        self.text.tag_configure('response', foreground='purple', font=('Consolas', 11))
        
        # 錯誤區塊樣式
        self.text.tag_configure('error_block', background='#FFE4E1', foreground='red')
        
        # Hover效果
        self.text.tag_configure('step_hover', background='#FFFF99')
        
        # 置頂Header樣式 (綠底黑字，放大)
        self.text.tag_configure('header_style', background='#90EE90', foreground='black', font=('Consolas', 14, 'bold'))
        
        # 摘要/日誌樣式 (統一字體與大小，提升專業感)
        self.text.tag_configure('summary_info', foreground='#0056b3', font=('Consolas', 11, 'bold'))
        self.text.tag_configure('summary_path', background='#FFFF00', foreground='black', font=('Consolas', 11, 'bold'))
        self.text.tag_configure('summary_success', foreground='#28a745', font=('Consolas', 11, 'bold'))
        self.text.tag_configure('summary_warning', foreground='#ffc107', font=('Consolas', 11, 'bold'))
        
        # 綁定點擊事件
        self.text.tag_bind('step_clickable', '<Button-1>', self._on_step_click)
        self.text.tag_bind('step_clickable', '<Enter>', self._on_step_hover)
        self.text.tag_bind('step_clickable', '<Leave>', self._on_step_leave)
        
        # 折疊相關樣式
        self.text.tag_configure('fold_header_pass', foreground='#28a745', font=('Consolas', 11, 'bold'), background='#e8f5e9')
        self.text.tag_configure('fold_header_fail', foreground='#dc3545', font=('Consolas', 11, 'bold'), background='#ffebee')
        self.text.tag_configure('fold_icon', foreground='#666', font=('Consolas', 12, 'bold'))
        self.text.tag_configure('fold_icon_fail', foreground='#dc3545', font=('Consolas', 12, 'bold'))  # FAIL 項目的紅色圖示
        
        # 綁定折疊點擊事件
        self.text.tag_bind('foldable', '<Button-1>', self._on_fold_click)
        self.text.tag_bind('foldable', '<Enter>', lambda e: self.text.config(cursor='hand2'))
        self.text.tag_bind('foldable', '<Leave>', lambda e: self.text.config(cursor='xterm'))
    
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
        """插入log內容並進行語法高亮（帶折疊功能）"""
        self.text.delete('1.0', tk.END)
        self.step_positions.clear()
        self.folded_items.clear()
        self.item_counter = 0
        
        # 插入置頂資訊 (Header)
        if header_content:
            self.text.insert(tk.INSERT, header_content + "\n", 'header_style')
            self.text.insert(tk.INSERT, "\n") # 空一行
        
        if not log_content:
            return
        
        # 獲取 pass_items 和 fail_items
        pass_items = test_results.get('pass_items', [])
        fail_items = test_results.get('fail_items', [])
        
        # 如果有測試項目，使用折疊模式
        if pass_items or fail_items:
            self._insert_with_folding(log_content, pass_items, fail_items)
        else:
            # 否則使用原始的高亮模式
            self._insert_without_folding(log_content)
        
        # 預設折疊所有 PASS 項目（延遲執行以確保內容已完全插入）
        self.text.after(100, self._delayed_fold_pass_items)
    
    def _insert_with_folding(self, log_content, pass_items, fail_items):
        """插入帶折疊功能的LOG"""
        lines = log_content.split('\n')
        
        # DEBUG: 輸出測試項目信息
        print(f"[DEBUG] 開始折疊處理: {len(pass_items)} PASS, {len(fail_items)} FAIL")
        
        # 建立測試項目索引（使用 start_idx 直接定位）
        item_map = {}  # {line_number: {'item': item_data, 'type': 'pass'/'fail'}}
        
        # 處理 PASS 項目 - 使用 start_idx 直接定位
        for idx, item in enumerate(pass_items):
            start_idx = item.get('start_idx')
            step_name = item.get('step_name', '').strip()
            
            if start_idx is not None and start_idx < len(lines):
                # 直接使用 start_idx 作為行號
                item_map[start_idx] = {'item': item, 'type': 'pass', 'step_name': step_name}
                print(f"[DEBUG] PASS #{idx+1}: '{step_name}' 於行 {start_idx+1}")
            else:
                print(f"[DEBUG] PASS #{idx+1}: '{step_name}' 無 start_idx，跳過")
        
        # 處理 FAIL 項目 - 使用 start_idx 直接定位
        for idx, item in enumerate(fail_items):
            start_idx = item.get('start_idx')
            step_name = item.get('step_name', '').strip()
            
            if start_idx is not None and start_idx < len(lines):
                # 直接使用 start_idx 作為行號
                item_map[start_idx] = {'item': item, 'type': 'fail', 'step_name': step_name}
                print(f"[DEBUG] FAIL #{idx+1}: '{step_name}' 於行 {start_idx+1}")
            else:
                print(f"[DEBUG] FAIL #{idx+1}: '{step_name}' 無 start_idx，跳過")
        
        print(f"[DEBUG] 總共匹配到 {len(item_map)} 個測試項目")
        
        # 插入LOG並創建折疊結構
        current_item_id = None
        current_item_start = None
        current_item_content = []
        
        for i, line in enumerate(lines):
            line_number = i + 1
            
            # 檢查是否是新的測試項目
            if i in item_map:
                # 先完成前一個項目
                if current_item_id is not None:
                    self._finalize_folded_item(current_item_id, current_item_start, current_item_content)
                
                # 開始新項目
                item_data = item_map[i]
                item_type = item_data['type']
                step_name = item_data['step_name']
                result = item_data['item'].get('result', '')
                
                # 創建摘要行
                self.item_counter += 1
                current_item_id = str(self.item_counter)
                
                header_start = self.text.index(tk.INSERT)
                
                # 插入折疊圖示和摘要
                icon = "▼ "
                tag_type = 'fold_header_pass' if item_type == 'pass' else 'fold_header_fail'
                icon_tag = 'fold_icon' if item_type == 'pass' else 'fold_icon_fail'
                label = f"[PASS] {step_name}" if item_type == 'pass' else f"[FAIL] {step_name}"
                
                self.text.insert(tk.INSERT, icon, (icon_tag, f'fold_item_{current_item_id}', 'foldable'))
                self.text.insert(tk.INSERT, label + "\n", (tag_type, f'fold_item_{current_item_id}', 'foldable'))
                
                header_end = self.text.index(tk.INSERT)
                
                # 初始化折疊項目數據
                current_item_start = self.text.index(tk.INSERT)
                current_item_content = []
                
                self.folded_items[current_item_id] = {
                    'type': item_type,
                    'step_name': step_name,
                    'header_start': header_start,
                    'header_end': header_end,
                    'content_start': current_item_start,
                    'content_end': current_item_start,
                    'content': '',
                    'is_folded': False
                }
                
                continue
            
            # 收集當前項目的內容
            if current_item_id is not None:
                formatted_line = f"{line_number:4d} {line}\n"
                current_item_content.append(formatted_line)
            else:
                # 不屬於任何項目的行（直接插入）
                line_start = self.text.index(tk.INSERT)
                self.text.insert(tk.INSERT, f"{line_number:4d} ", 'line_number')
                self.text.insert(tk.INSERT, line + "\n")
        
        # 完成最後一個項目
        if current_item_id is not None:
            self._finalize_folded_item(current_item_id, current_item_start, current_item_content)
    
    def _finalize_folded_item(self, item_id, start_pos, content_lines):
        """完成折疊項目的內容插入"""
        if item_id not in self.folded_items:
            return
        
        item_data = self.folded_items[item_id]
        content_text = ''.join(content_lines)
        
        # 插入內容
        self.text.insert(start_pos, content_text)
        content_end = self.text.index(f"{start_pos} + {len(content_text)}c")
        
        # 如果是 FAIL 項目，套用紅色樣式
        if item_data['type'] == 'fail':
            self.text.tag_add('fail_text', start_pos, content_end)
        
        # 更新折疊項目數據
        self.folded_items[item_id]['content'] = content_text
        self.folded_items[item_id]['content_start'] = start_pos
        self.folded_items[item_id]['content_end'] = content_end
    
    def _delayed_fold_pass_items(self):
        """延遲折疊 PASS 項目（確保內容已完全插入）"""
        try:
            self.fold_all_pass_items()
        except Exception as e:
            print(f"延遲折疊失敗: {e}")
    
    def _insert_without_folding(self, log_content):
        """插入不帶折疊的LOG（原始高亮模式）"""
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
    
    def _on_fold_click(self, event):
        """處理折疊/展開點擊事件"""
        try:
            # 獲取點擊位置的所有標籤
            index = self.text.index(tk.CURRENT)
            tags = self.text.tag_names(index)
            
            # 找到對應的 item_id
            item_id = None
            for tag in tags:
                if tag.startswith('fold_item_'):
                    item_id = tag.replace('fold_item_', '')
                    break
            
            if item_id and item_id in self.folded_items:
                item_data = self.folded_items[item_id]
                if item_data['is_folded']:
                    self._unfold_item(item_id)
                else:
                    self._fold_item(item_id)
        except Exception as e:
            print(f"折疊點擊處理失敗: {e}")
    
    def _fold_item(self, item_id):
        """折疊指定項目"""
        try:
            if item_id not in self.folded_items:
                return
            
            item_data = self.folded_items[item_id]
            if item_data['is_folded']:
                return  # 已經折疊
            
            # 獲取摘要行的位置
            header_start = item_data['header_start']
            content_start = item_data['content_start']
            content_end = item_data['content_end']
            
            # 刪除內容部分
            self.text.delete(content_start, content_end)
            
            # 更新折疊圖示 (▶)
            icon_start = f"{header_start} linestart"
            icon_end = f"{header_start} linestart +2c"
            self.text.delete(icon_start, icon_end)
            icon_tag = 'fold_icon' if item_data['type'] == 'pass' else 'fold_icon_fail'
            self.text.insert(icon_start, "▶ ", (icon_tag, f'fold_item_{item_id}', 'foldable'))
            
            # 更新狀態
            item_data['is_folded'] = True
            
        except Exception as e:
            print(f"折疊項目失敗: {e}")
    
    def _unfold_item(self, item_id):
        """展開指定項目"""
        try:
            if item_id not in self.folded_items:
                return
            
            item_data = self.folded_items[item_id]
            if not item_data['is_folded']:
                return  # 已經展開
            
            # 獲取摘要行的位置
            header_start = item_data['header_start']
            header_end = item_data['header_end']
            
            # 更新折疊圖示 (▼)
            icon_start = f"{header_start} linestart"
            icon_end = f"{header_start} linestart +2c"
            self.text.delete(icon_start, icon_end)
            icon_tag = 'fold_icon' if item_data['type'] == 'pass' else 'fold_icon_fail'
            self.text.insert(icon_start, "▼ ", (icon_tag, f'fold_item_{item_id}', 'foldable'))
            
            # 在摘要行後插入內容
            insert_pos = f"{header_end}"
            self.text.insert(insert_pos, item_data['content'])
            
            # 更新 content_end 位置
            new_end = self.text.index(f"{insert_pos} + {len(item_data['content'])}c")
            item_data['content_end'] = new_end
            item_data['content_start'] = insert_pos
            
            # 更新狀態
            item_data['is_folded'] = False
            
        except Exception as e:
            print(f"展開項目失敗: {e}")
    
    def fold_all_pass_items(self):
        """折疊所有 PASS 項目"""
        for item_id, item_data in self.folded_items.items():
            if item_data['type'] == 'pass' and not item_data['is_folded']:
                self._fold_item(item_id)
    
    def unfold_all_items(self):
        """展開所有項目"""
        for item_id, item_data in self.folded_items.items():
            if item_data['is_folded']:
                self._unfold_item(item_id)
    
    def fold_all_fail_items(self):
        """折疊所有 FAIL 項目"""
        for item_id, item_data in self.folded_items.items():
            if item_data['type'] == 'fail' and not item_data['is_folded']:
                self._fold_item(item_id)
