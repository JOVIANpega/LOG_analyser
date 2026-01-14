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
    
    def __init__(self, parent, settings=None, **kwargs):
        # 創建框架來容納Text和滾動條
        self.frame = tk.Frame(parent)
        self.text = tk.Text(self.frame, **kwargs)
        self.settings = settings or {}
        self.setup_tags()
        self.step_positions = {}  # 儲存每個step的位置
        self.folded_items = {}  # 儲存折疊項目的內容 {item_id: {'start': index, 'end': index, 'content': str, 'is_folded': bool, 'type': 'pass'/'fail'}}
        self.item_counter = 0  # 用於生成唯一 item_id
        self.setup_search_functionality()
        self.setup_scrollbars()
        
        # 綁定滑鼠移動事件 (用於行高亮)
        self.text.bind('<Motion>', self._on_mouse_move)
        self.text.bind('<Leave>', self._on_mouse_leave)
        
        # 🟢 新增：綁定鍵盤/點擊事件 (確保反黃效果跟隨鍵盤選擇)
        self.text.bind('<KeyRelease>', self._on_cursor_move)
        self.text.bind('<ButtonRelease-1>', self._on_cursor_move)
        
        self.last_highlighted_line = None
    
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
            insert_pos = self.text.index(tk.END + "-1c")
            self.text.insert(tk.END, str(text) + "\n", tag)
            
            # 🟢 鍵盤導航增強：如果是在追加測項章節，額外加上 header_style 標籤
            if '@STEP' in str(text):
                end_pos = self.text.index(tk.END + "-1c")
                self.text.tag_add('header_style', insert_pos, end_pos)

            self.text.see(tk.END)
        except Exception as e:
            print(f"Append text failed: {e}")
    
    def update_hover_color(self, color_hex):
        """即時更新懸停高亮顏色"""
        try:
            self.text.tag_configure('current_line_highlight', background=color_hex)
            self.text.tag_configure('step_hover', background=color_hex)
        except Exception as e:
            print(f"Update hover color failed: {e}")

    def setup_tags(self):
        """設定文字標籤樣式"""
        # 滑鼠懸停高亮 (預設淡黃色背景，可從 settings 讀取)
        hover_bg = self.settings.get('log_hover_color', '#FFF9C4')
        self.text.tag_configure('current_line_highlight', background=hover_bg)
        
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
        self.text.tag_configure('step_hover', background=hover_bg)
        
        # 置頂Header樣式 (綠底黑字，放大)
        self.text.tag_configure('header_style', background='#90EE90', foreground='black', font=('Consolas', 14, 'bold'))
        
        # 摘要/日誌樣式 (統一字體與大小，提升專業感)
        self.text.tag_configure('summary_info', foreground='#0056b3', font=('Consolas', 11, 'bold'))
        self.text.tag_configure('summary_path', background='#FFFF00', foreground='black', font=('Consolas', 11, 'bold'))
        self.text.tag_configure('summary_success', foreground='#28a745', font=('Consolas', 11, 'bold'))
        self.text.tag_configure('summary_warning', foreground='#ffc107', font=('Consolas', 11, 'bold'))
        self.text.tag_configure('summary_highlight', background='#FFFF00', foreground='black', font=('Consolas', 14, 'bold'))
        
        # 綁定點擊事件
        self.text.tag_bind('step_clickable', '<Button-1>', self._on_step_click)
        self.text.tag_bind('step_clickable', '<Enter>', self._on_step_hover)
        self.text.tag_bind('step_clickable', '<Leave>', self._on_step_leave)
        
        # 搜尋高亮樣式
        self.text.tag_configure('search_highlight', background='yellow', foreground='black')
        
    
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
    
    def insert_log_with_highlighting(self, log_content, test_results, header_content=None, ui_annotations=None, error_preview_data=None):
        """插入log內容並進行語法高亮（使用解析器提供的標註）"""
        self.text.delete('1.0', tk.END)
        self.step_positions.clear()
        self.folded_items.clear()
        self.item_counter = 0
        
        # 插入置頂資訊 (Header)
        if header_content:
            self.text.insert(tk.INSERT, header_content + "\n", 'header_style')
            self.text.insert(tk.INSERT, "\n") # 空一行
            
        # === 插入錯誤原因預覽 (置頂顯示錯誤區塊) ===
        if error_preview_data:
            # 設定預覽框樣式 (同步 Excel)
            if 'error_preview_critical' not in self.text.tag_names():
                # 🔴 真正錯誤的反白 (紅底白字)
                self.text.tag_configure('error_preview_critical', 
                                      background='red', foreground='white', 
                                      font=('Consolas', 11, 'bold'))
                # 🔴 一般錯誤原因 (僅紅字)
                self.text.tag_configure('error_preview_standard', 
                                      foreground='red', 
                                      font=('Consolas', 11, 'bold'))
                self.text.tag_configure('preview_title', 
                                      foreground='red', font=('Arial', 12, 'bold'))

            # 標籤頭
            self.text.insert(tk.INSERT, "┌──────────────── [ 發現錯誤點 (預覽) ] ────────────────┐\n", 'preview_title')
            
            for item in error_preview_data:
                p_line = item.get('content', '')
                l_idx = item.get('line_idx')
                if not p_line.strip(): continue
                
                # 建立唯一標籤用於跳轉
                p_tag = f"p_jump_{self.item_counter}"
                self.item_counter += 1
                
                # 決定標籤 (反白 vs 一般紅字)
                is_crit = item.get('is_critical', False)
                base_tag = 'error_preview_critical' if is_crit else 'error_preview_standard'
                
                display_text = "  >> " + p_line + "\n"
                self.text.insert(tk.INSERT, display_text, (base_tag, p_tag, 'step_clickable'))
                
                # 綁定點擊事件 (優先使用行號)
                if l_idx is not None:
                     # 向下宣告 _jump_to_log_line
                     self.text.tag_bind(p_tag, '<Button-1>', lambda e, idx=l_idx: self._jump_to_log_line(idx))
                else:
                     # Fallback: 模糊搜尋
                     search_key = p_line.strip()
                     self.text.tag_bind(p_tag, '<Button-1>', lambda e, sk=search_key: self._jump_to_log_content(sk))
            
            self.text.insert(tk.INSERT, "└───────────────────────────────────────────────────────┘\n\n", 'preview_title')
        
        if not log_content:
            return
        
        # 計算 Header 佔用的行數偏移量
        try:
            current_pos = self.text.index(tk.INSERT)
            header_offset = int(current_pos.split('.')[0]) - 1
        except:
            header_offset = 0
            
        # 獲取 pass_items 和 fail_items
        fail_items = test_results.get('fail_items', [])
        
        # 1. 使用解析器提供的 ui_annotations 進行渲染
        if ui_annotations:
            self._insert_with_annotations(ui_annotations)
        else:
            # Fallback (如果沒提供標註)
            self._insert_without_folding(log_content)
        
        # 2. 額外處理 FAIL 區域的高亮顯示 (保持原有邏輯作為雙重保障)
        if fail_items:
            self._highlight_fail_regions(fail_items, header_offset)
    
    def _insert_with_annotations(self, annotations):
        """使用解析器的 UI 標註資訊逐行插入並著色 (同步 Excel 視覺邏輯)"""
        
        # 預先定義統一風格標籤
        if 'phase_separator' not in self.text.tag_names():
            self.text.tag_configure('phase_separator', 
                                 background='#2E7D32', foreground='white', 
                                 font=('Consolas', 12, 'bold'), justify='center')

        for i, ann in enumerate(annotations):
            line_content = ann.get('line_content', '')
            
            # --- PHASE 大章節標頭 (同步 Excel 綠色能量條) ---
            if ann.get('show_separator'):
                title = ann.get('separator_title', 'TEST PHASE')
                # 建立一個佔滿寬度的標題行
                sep_text = f"\n [ {title} ] \n\n"
                
                sep_start = self.text.index(tk.INSERT)
                self.text.insert(tk.INSERT, sep_text, 'phase_separator')
                
                # 記錄跳轉位置
                self.step_positions[title] = sep_start
            
            # --- 插入 LOG 本體 ---
            line_start = self.text.index(tk.INSERT)
            line_number = i + 1
            
            # 1. 插入行號 (灰字)
            self.text.insert(tk.INSERT, f"{line_number:5d} ")
            self.text.tag_add('line_number', line_start, self.text.index(tk.INSERT))
            
            # 2. 插入內容
            content_start = self.text.index(tk.INSERT)
            self.text.insert(tk.INSERT, line_content + '\n')
            content_end = self.text.index(tk.INSERT)
            
            # 3. 應用視覺樣式 (解析器主導)
            color = ann.get('color', 'black')
            background = ann.get('background', 'white')
            is_bold = ann.get('is_bold', False)
            
            # 動態生成標籤樣式
            clean_bg = background.replace('#', '')
            style_tag = f"tag_{color}_{clean_bg}_{'b' if is_bold else 'n'}"
            
            if style_tag not in self.text.tag_names():
                # 獲取當前 Text 元件字體大小
                try:
                    current_font = self.text.cget('font')
                    if isinstance(current_font, (list, tuple)):
                        f_size = current_font[1]
                    else:
                        f_size = 11 # fallback
                except:
                    f_size = 11
                    
                font_cfg = ['Consolas', f_size]
                if is_bold:
                    font_cfg.append('bold')
                
                bg_val = background if background.lower() != 'white' else None
                self.text.tag_configure(style_tag, foreground=color, background=bg_val, font=tuple(font_cfg))
            
            # 著色 (套用到整行，包含行號背景，讓視覺更一致)
            self.text.tag_add(style_tag, line_start, content_end)
            
            # 4. 章節與跳轉點標記 (用於鍵盤上下鍵切換章節)
            if '@STEP' in line_content:
                # 著色為標題樣式
                self.text.tag_add('header_style', line_start, content_end)
                
                # 提取測項名稱用於內部跳轉索引
                step_match = re.search(r'Do @STEP\d+@([^@\n]+)', line_content)
                if step_match:
                    step_name = step_match.group(1).strip()
                    click_tag = f"step_jump_{step_name}"
                    self.text.tag_add(click_tag, content_start, content_end)
                    self.text.tag_add('step_clickable', content_start, content_end)
                    if step_name not in self.step_positions:
                        self.step_positions[step_name] = line_start


        # 提升高亮優先級 (安全檢查，避免 tag 未定義錯誤)
        for tag_name in ['step_hover', 'search_highlight', 'phase_separator']:
            if tag_name in self.text.tag_names():
                self.text.tag_raise(tag_name)
    
    def _insert_without_folding(self, log_content):
        """插入不帶折疊的LOG（原始備用模式）"""
        lines = log_content.split('\n')
        bg_toggle = True
        
        for i, line in enumerate(lines):
            line_start = self.text.index(tk.INSERT)
            # ... (其餘邏輯維持 fallback)
            self.text.insert(tk.INSERT, f"{i+1:4d} ")
            self.text.insert(tk.INSERT, line + '\n')
    
    def jump_to_step(self, step_name):
        """跳轉到指定step"""
        if step_name in self.step_positions:
            position = self.step_positions[step_name]
            self.text.see(position)
            self.text.mark_set(tk.INSERT, position)
    
    def _jump_to_log_line(self, line_idx):
        """根據解析時的原始行號精確跳轉"""
        # 因為 Text widget 前方插入了 Header 和 預覽框，所以行號會偏移
        # 策略：搜尋行首帶有 "   50 " (對應 line_idx=49) 格式的行號標記
        search_str = f"{line_idx + 1:5d} "
        pos = self.text.search(search_str, "20.0", tk.END)
        if pos:
            # 高亮該行
            self.text.tag_remove('search_highlight', '1.0', tk.END)
            self.text.tag_add('search_highlight', pos, f"{pos} lineend")
            self.text.tag_raise('search_highlight')
            
            # 跳轉並中心對齊
            self.text.see(pos)
            self.text.mark_set(tk.INSERT, pos)
            self.text.yview_scroll(-3, 'units')
        else:
            # 如果找不到帶行號的標記 (可能被折疊或格式不同)，則嘗試直接計算 (較不準)
            pass

    def _jump_to_log_content(self, search_text):
        """從預覽區點擊跳轉到日誌本體中的對應行"""
        if not search_text: return
        
        # 搜尋時避開置頂的預覽區 (從 30.0 開始搜尋通常比較安全)
        pos = self.text.search(search_text, "20.0", tk.END)
        if pos:
            # 高亮該行
            self.text.tag_remove('search_highlight', '1.0', tk.END)
            self.text.tag_add('search_highlight', pos, f"{pos} lineend")
            self.text.tag_raise('search_highlight')
            
            # 跳轉並中心對齊
            self.text.see(pos)
            self.text.mark_set(tk.INSERT, pos)
            # 輔助：稍微滾動一點點讓它靠近中間
            self.text.yview_scroll(-3, 'units')
        else:
            # 如果沒找到精確匹配，嘗試部分匹配
            parts = search_text.split(']')
            if len(parts) > 1:
                self._jump_to_log_content(parts[0] + ']')

    def highlight_error_block(self, start_line, end_line):
        """高亮錯誤區塊"""
        # 搜尋對應的 Log 行號標記
        search_str = f"{start_line:5d} "
        found = self.text.search(search_str, '1.0', tk.END)
        if found:
            self.text.tag_add('error_block', found, f"{found} lineend")
            self.text.see(found)

    def focus_first_error_line(self):
        """聚焦到第一個錯誤行 (優先顯示置頂摘要)"""
        try:
            # 如果有標題或預覽框，就留在最上面
            tags = self.text.tag_names()
            if 'preview_title' in tags or 'header_style' in tags:
                self.text.see("1.0")
                self.text.mark_set(tk.INSERT, "1.0")
                return

            # 原有邏輯：尋找第一個包含錯誤關鍵字的行
            content = self.text.get('1.0', tk.END)
            lines = content.split('\n')
            for i, line in enumerate(lines):
                line_lower = line.lower()
                if not re.match(r'\s*\d+\s', line): continue

                if (any(critical_error in line_lower for critical_error in [
                    'segmentation fault', 'core dumped', 'executes fail', 
                    "doesn't match", 'timeout', 'exception', 'wrong'
                ]) or 'is fail' in line_lower or 'is failed' in line_lower):
                    line_num = i + 1
                    self.text.see(f"{line_num}.0")
                    self.text.mark_set(tk.INSERT, f"{line_num}.0")
                    break
        except Exception as e:
            print(f"聚焦錯誤行失敗: {e}")

    def _highlight_fail_regions(self, fail_items, header_offset):
        """將所有FAIL項目區域標記為紅色高亮 (不再自動跳轉離置頂區域)"""
        try:
           last_idx = self.text.index("end-1c")
           total_lines = int(last_idx.split('.')[0])
        except:
           total_lines = 999999
        
        for item in fail_items:
            start_idx = item.get('start_idx')
            end_idx = item.get('end_idx') or start_idx
            
            if start_idx is not None:
                start_line = start_idx + 1 + header_offset
                end_line = end_idx + 1 + header_offset
                
                if start_line > total_lines: continue
                
                start_pos = f"{start_line}.0"
                end_pos = f"{end_line + 1}.0"
                
                self.text.tag_add('error_block', start_pos, end_pos)
                self.text.tag_add('fail_text', start_pos, end_pos)
        
        # 修改：預設回到最頂部看摘要
        self.text.see("1.0")
        self.text.mark_set(tk.INSERT, "1.0")

    def _on_mouse_move(self, event):
        """處理滑鼠移動，高亮當前行 (優化效能)"""
        try:
            # 獲取滑鼠當前位置的索引
            pos = f"@{event.x},{event.y}"
            index = self.text.index(pos)
            
            # 獲取行號
            current_line = index.split('.')[0]
            
            # 如果行號沒變，這一步就跳過
            if current_line == self.last_highlighted_line:
                return
            
            # 移除舊的高亮 (僅針對上一行)
            if self.last_highlighted_line:
                self.text.tag_remove('current_line_highlight', f"{self.last_highlighted_line}.0", f"{self.last_highlighted_line}.end+1c")
            
            # 添加新高亮
            line_start = f"{current_line}.0"
            line_end = f"{current_line}.end+1c"
            self.text.tag_add('current_line_highlight', line_start, line_end)
            
            # 提升優先級
            self.text.tag_raise('current_line_highlight')
            
            self.last_highlighted_line = current_line
            
        except Exception:
            pass

    def _on_mouse_leave(self, event):
        """滑鼠離開時移除高亮"""
        if self.last_highlighted_line:
            self.text.tag_remove('current_line_highlight', f"{self.last_highlighted_line}.0", f"{self.last_highlighted_line}.end+1c")
        self.last_highlighted_line = None

    def _on_cursor_move(self, event=None):
        """處理鍵盤/點擊後的游標移動，高亮當前行 (反黃跟隨)"""
        try:
            # 1. 獲取當前游標所在的行號
            index = self.text.index(tk.INSERT)
            current_line = index.split('.')[0]
            
            # 2. 如果行號沒變，不重複處理
            if current_line == self.last_highlighted_line:
                return
                
            # 3. 移除舊的高亮
            if self.last_highlighted_line:
                self.text.tag_remove('current_line_highlight', f"{self.last_highlighted_line}.0", f"{self.last_highlighted_line}.end+1c")
                
            # 4. 添加新高亮
            line_start = f"{current_line}.0"
            line_end = f"{current_line}.end+1c"
            self.text.tag_add('current_line_highlight', line_start, line_end)
            self.text.tag_raise('current_line_highlight')
            
            self.last_highlighted_line = current_line
        except Exception:
            pass
    
