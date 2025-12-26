# ui_enhanced.py
# 用途：提供進階的GUI元件，包含顏色標籤、hover效果、文字格式化等
import tkinter as tk
from tkinter import ttk, messagebox
import re

class EnhancedTreeview:
    """增強型TreeView，支援顏色標籤和hover效果"""
    
    def __init__(self, parent, columns, show='headings', settings=None):
        self.tree = ttk.Treeview(parent, columns=columns, show=show)
        self.full_content_storage = {}  # 用字典存儲完整內容
        self.all_items_data = []  # 存儲所有測試項的資料
        self.font_size = 11
        self.settings = settings or {}
        self._hover_popup = None
        self._hover_row = None
        self.setup_styles()
        self.setup_hover_effects()
        self.setup_scrollbars(parent)
    
    def setup_styles(self):
        """設定樣式"""
        # 獲取主題的前景和背景色
        try:
            from ttkbootstrap import Style
            theme_style = Style().colors
            fg_color = theme_style.inputfg
            bg_color = theme_style.inputbg
            pass_color = theme_style.success
            fail_color = theme_style.danger
            hover_color = theme_style.selectbg
        except:
            fg_color = "black"
            bg_color = "white"
            pass_color = "green"
            fail_color = "red"
            hover_color = "#E8F4FD"

        self.style = ttk.Style()
        
        # PASS項目樣式
        self.style.configure("Pass.Treeview", foreground=pass_color, font=('Arial', self.font_size))
        
        # FAIL項目樣式
        self.style.configure("Fail.Treeview", foreground=fail_color, font=('Arial', self.font_size))
        
        # Hover效果樣式
        self.style.configure("Hover.Treeview.Item", background=hover_color)
        
        # 一般TreeView樣式
        self.style.configure("Treeview", font=('Arial', self.font_size))
        self.style.configure("Treeview.Heading", font=('Arial', self.font_size, 'bold'))
    
    def setup_hover_effects(self):
        """設定hover效果"""
        self.tree.bind('<Motion>', self._on_hover)
        self.tree.bind('<Leave>', self._on_leave)
        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<Control-c>', self._on_copy)  # 支援Ctrl+C複製
        
        # 綁定選擇改變事件
        self.tree.bind('<<TreeviewSelect>>', self._on_selection_change)
        
        # 綁定ENTER鍵事件
        self.tree.bind('<Return>', self._on_enter_key)
        
        self.current_hover_item = None
    
    def setup_scrollbars(self, parent):
        """設定滾動條"""
        # 垂直滾動條
        self.v_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.v_scrollbar.set)
        
        # 水平滾動條
        self.h_scrollbar = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscrollcommand=self.h_scrollbar.set)
    
    def pack_with_scrollbars(self, **kwargs):
        """打包TreeView和滾動條"""
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 從kwargs中提取pack參數，避免衝突
        pack_kwargs = {}
        for key, value in kwargs.items():
            if key in ['fill', 'expand', 'side', 'padx', 'pady', 'ipadx', 'ipady', 'anchor']:
                pack_kwargs[key] = value
        
        # 設定預設值
        if 'fill' not in pack_kwargs:
            pack_kwargs['fill'] = tk.BOTH
        if 'expand' not in pack_kwargs:
            pack_kwargs['expand'] = 1
            
        # 直接使用pack_kwargs，不傳遞kwargs
        self.tree.pack(**pack_kwargs)
    
    def _on_hover(self, event):
        """滑鼠懸停效果"""
        item = self.tree.identify_row(event.y)
        if item != self.current_hover_item:
            if self.current_hover_item:
                # 取消舊的hover標籤
                tags = list(self.tree.item(self.current_hover_item, 'tags'))
                if 'hover' in tags:
                    tags.remove('hover')
                self.tree.item(self.current_hover_item, tags=tuple(tags))
            if item:
                tags = list(self.tree.item(item, 'tags'))
                if 'hover' not in tags:
                    tags.append('hover')
                self.tree.item(item, tags=tuple(tags))
                self.current_hover_item = item
        # 額外：顯示懸停浮窗（整列只要有保存內容即可顯示）
        self._maybe_show_hover_popup(event)
    
    def _on_leave(self, event):
        """滑鼠離開效果"""
        if self.current_hover_item:
            self.tree.item(self.current_hover_item, tags=())
            self.current_hover_item = None
        self._hover_row = None
        self._hide_hover_popup()
    
    def _on_double_click(self, event):
        """雙擊展開詳細內容"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            # 從字典中獲取完整內容
            full_content = self.full_content_storage.get(item)
            if full_content:
                self._show_detail_dialog(full_content, current_item_id=item)
            else:
                print("沒有找到詳細內容")
    
    def _on_selection_change(self, event):
        """處理選擇改變事件，同步彈窗顯示"""
        selected_items = self.tree.selection()
        if not selected_items:
            # 沒有選中項目時隱藏彈窗
            self._hide_hover_popup()
            return
        
        current_item = selected_items[0]
        if current_item != self._hover_row:
            # 如果當前項目有內容，顯示彈窗
            if self.full_content_storage.get(current_item):
                self._maybe_show_hover_popup_for_keyboard(current_item)
    
    def _on_enter_key(self, event):
        """ENTER鍵處理，開啟詳細視窗"""
        selected_items = self.tree.selection()
        if not selected_items:
            return "break"
        
        current_item = selected_items[0]
        # 從字典中獲取完整內容
        full_content = self.full_content_storage.get(current_item)
        if full_content:
            self._show_detail_dialog(full_content, current_item_id=current_item)
        else:
            print("沒有找到詳細內容")
        
        return "break"

    def set_font_size(self, size: int):
        """設定展開視窗字體大小"""
        try:
            sz = int(size)
        except Exception:
            sz = 11
        self.font_size = max(10, min(15, sz))
        
        # 更新TreeView內容字體大小
        self.style.configure("Treeview", font=('Arial', self.font_size))
        self.style.configure("Treeview.Heading", font=('Arial', self.font_size, 'bold'))
        self.style.configure("Pass.Treeview", font=('Arial', self.font_size))
        self.style.configure("Pass.Treeview.Item", font=('Arial', self.font_size))
        self.style.configure("Fail.Treeview", font=('Arial', self.font_size))
        self.style.configure("Fail.Treeview.Item", font=('Arial', self.font_size))
        
        # 更新懸停浮窗字體
        if self._hover_popup and self._hover_popup.winfo_exists():
            try:
                self._hover_text.config(font=('Consolas', self.font_size))
            except Exception:
                pass
    
    def _on_copy(self, event):
        """處理Ctrl+C複製選中項目"""
        try:
            selected_items = self.tree.selection()
            if selected_items:
                item = selected_items[0]
                values = self.tree.item(item, 'values')
                if values:
                    # 複製選中行的所有內容
                    content = '\t'.join(str(v) for v in values)
                    self._copy_to_clipboard(content)
        except Exception as e:
            print(f"複製選中項目失敗: {e}")
    
    def _maybe_show_hover_popup(self, event):
        """顯示懸停彈窗，支援滑鼠和鍵盤選擇"""
        # 檢查是否有滑鼠事件
        if not event or not hasattr(event, 'y'):
            return
            
        row = self.tree.identify_row(event.y)
        if not row:
            self._hover_row = None
            self._hide_hover_popup()
            return
        content = self.full_content_storage.get(row)
        if not content:
            if self._hover_row != row:
                self._hover_row = None
                self._hide_hover_popup()
            return
        # 位置計算 - 檢查是否靠近下方
        abs_x = self.tree.winfo_rootx() + event.x + 12
        abs_y = self.tree.winfo_rooty() + event.y + 12
        
        # 檢查是否靠近螢幕下方，如果是則往上顯示
        screen_height = self.tree.winfo_screenheight()
        popup_height = 400
        if abs_y + popup_height > screen_height - 50:  # 距離底部50像素時往上顯示
            abs_y = screen_height - popup_height - 50
        
        if self._hover_row == row and self._hover_popup and self._hover_popup.winfo_exists():
            try:
                self._hover_popup.geometry(f"700x400+{abs_x}+{abs_y}")
            except Exception:
                pass
            return
        self._hover_row = row
        self._show_hover_popup("完整內容", content, abs_x, abs_y)
    
    def _maybe_show_hover_popup_for_keyboard(self, item_id):
        """為鍵盤選擇的項目顯示彈窗"""
        if not item_id:
            return
        
        content = self.full_content_storage.get(item_id)
        if not content:
            return
        
        # 獲取項目位置
        bbox = self.tree.bbox(item_id, column=0)
        if not bbox:
            return
        
        x, y, width, height = bbox
        abs_x = self.tree.winfo_rootx() + x + width + 12
        abs_y = self.tree.winfo_rooty() + y + 12
        
        # 檢查是否靠近螢幕下方，如果是則往上顯示
        screen_height = self.tree.winfo_screenheight()
        popup_height = 400
        if abs_y + popup_height > screen_height - 50:
            abs_y = screen_height - popup_height - 50
        
        # 檢查是否靠近螢幕右側，如果是則往左顯示
        screen_width = self.tree.winfo_screenwidth()
        popup_width = 700
        if abs_x + popup_width > screen_width - 50:
            abs_x = screen_width - popup_width - 50
        
        # 如果彈窗已存在且是同一行，只更新位置
        if self._hover_row == item_id and self._hover_popup and self._hover_popup.winfo_exists():
            try:
                self._hover_popup.geometry(f"700x400+{abs_x}+{abs_y}")
            except Exception:
                pass
            return
        
        # 顯示新的彈窗
        self._hover_row = item_id
        self._show_hover_popup("完整內容", content, abs_x, abs_y)

    def _show_hover_popup(self, title, content, x, y):
        if self._hover_popup and self._hover_popup.winfo_exists():
            try:
                self._hover_text.config(state=tk.NORMAL)
                self._hover_text.delete('1.0', tk.END)
                
                # 檢查是否為FAIL項目，如果是則優先顯示錯誤原因
                if self._is_fail_content(content):
                    error_reason = self._extract_error_reason_from_content(content)
                    if error_reason:
                        # 顯示錯誤原因標題
                        self._hover_text.insert('1.0', "🔴 錯誤原因:\n", 'error_title')
                        self._hover_text.insert(tk.END, error_reason + "\n\n", 'error_content')
                        self._hover_text.insert(tk.END, "📋 完整內容:\n", 'full_title')
                        # 為完整內容中的錯誤行添加背景色
                        formatted_content = self._format_content_with_error_highlighting(content)
                        self._hover_text.insert(tk.END, formatted_content, 'normal_content')
                    else:
                        self._hover_text.insert('1.0', content)
                else:
                    self._hover_text.insert('1.0', content)
                
                self._hover_text.config(font=('Consolas', self.font_size))
                
                # 使用改善後的視窗定位邏輯
                self._position_hover_popup(self._hover_popup, x, y, 700, 400)
                
                # 重新應用語法高亮
                self._apply_syntax_highlighting(self._hover_text, content)
                return
            except Exception:
                try:
                    self._hover_popup.destroy()
                except Exception:
                    pass
                self._hover_popup = None
        # 建立新浮窗
        self._hover_popup = tk.Toplevel(self.tree)
        self._hover_popup.overrideredirect(True)
        self._hover_popup.attributes('-topmost', True)
        
        # 使用改善後的視窗定位邏輯
        self._position_hover_popup(self._hover_popup, x, y, 700, 400)
        
        frame = tk.Frame(self._hover_popup, bd=1, relief=tk.SOLID)
        frame.pack(fill=tk.BOTH, expand=1)
        text = tk.Text(frame, wrap=tk.NONE, font=('Consolas', self.font_size))
        
        # 設定文字標籤樣式
        text.tag_configure('error_title', foreground='red', font=('Consolas', self.font_size, 'bold'), background='#FFFF99')
        text.tag_configure('error_content', foreground='darkred', font=('Consolas', self.font_size, 'bold'), background='#FFFF99')
        text.tag_configure('full_title', foreground='blue', font=('Consolas', self.font_size, 'bold'), background='#FFFF99')
        text.tag_configure('normal_content', foreground='black')
        
        # 垂直滾動條 - 做大一點，靠近文字區
        vs = tk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview, width=20)
        vs.grid(row=0, column=1, sticky='ns', padx=(5, 0))
        
        # 水平滾動條 - 做大一點
        hs = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=text.xview, width=20)
        hs.grid(row=1, column=0, sticky='ew', pady=(5, 0))
        
        text.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        text.grid(row=0, column=0, sticky='nsew')
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # 檢查是否為FAIL項目，如果是則優先顯示錯誤原因
        if self._is_fail_content(content):
            error_reason = self._extract_error_reason_from_content(content)
            if error_reason:
                # 顯示錯誤原因標題
                text.insert('1.0', "🔴 錯誤原因:\n", 'error_title')
                text.insert(tk.END, error_reason + "\n\n", 'error_content')
                text.insert(tk.END, "📋 完整內容:\n", 'full_title')
                text.insert(tk.END, content, 'normal_content')
            else:
                text.insert('1.0', content)
        else:
            text.insert('1.0', content)
        
        text.config(state=tk.NORMAL)
        # 應用語法高亮
        self._apply_syntax_highlighting(text, content)
        self._hover_popup.bind('<Leave>', lambda e: self._hide_hover_popup())
        self._hover_text = text
    
    def _position_hover_popup(self, popup_window, mouse_x, mouse_y, window_width, window_height):
        """定位彈出視窗，避免與其他視窗重疊"""
        try:
            # 獲取螢幕尺寸
            screen_width = popup_window.winfo_screenwidth()
            screen_height = popup_window.winfo_screenheight()
            
            # 計算初始位置（滑鼠位置）
            initial_x = mouse_x
            initial_y = mouse_y
            
            # 檢查是否會超出螢幕邊界
            if initial_x + window_width > screen_width:
                initial_x = screen_width - window_width - 10
            
            if initial_y + window_height > screen_height:
                initial_y = screen_height - window_height - 10
            
            # 確保不會超出左邊界和上邊界
            initial_x = max(10, initial_x)
            initial_y = max(10, initial_y)
            
            # 檢查是否會與詳細視窗重疊
            if hasattr(self, '_detail_window') and self._detail_window and self._detail_window.winfo_exists():
                detail_x = self._detail_window.winfo_x()
                detail_y = self._detail_window.winfo_y()
                detail_width = self._detail_window.winfo_width()
                detail_height = self._detail_window.winfo_height()
                
                # 如果會重疊，調整位置
                if not (initial_x + window_width <= detail_x or 
                       detail_x + detail_width <= initial_x or
                       initial_y + window_height <= detail_y or 
                       detail_y + detail_height <= initial_y):
                    
                    # 嘗試放在詳細視窗的右側
                    if detail_x + detail_width + window_width <= screen_width:
                        initial_x = detail_x + detail_width + 10
                        initial_y = detail_y
                    # 如果右側空間不夠，放在下方
                    elif detail_y + detail_height + window_height <= screen_height:
                        initial_x = detail_x
                        initial_y = detail_y + detail_height + 10
                    # 如果下方空間也不夠，放在左側
                    elif detail_x - window_width >= 10:
                        initial_x = detail_x - window_width - 10
                        initial_y = detail_y
                    # 如果左側空間也不夠，放在上方
                    elif detail_y - window_height >= 10:
                        initial_x = detail_x
                        initial_y = detail_y - window_height - 10
            
            # 設定視窗位置
            popup_window.geometry(f"{window_width}x{window_height}+{initial_x}+{initial_y}")
            
        except Exception as e:
            print(f"定位彈出視窗失敗: {e}")
            # 使用預設位置
            popup_window.geometry(f"{window_width}x{window_height}+{mouse_x}+{mouse_y}")
    
    def insert_phase_header(self, phase_name):
        """插入 Phase 大章節分隔行 (高能見度)"""
        columns_count = len(self.tree['columns'])
        # 僅在第一欄顯示章節名稱，其餘留空
        clean_name = phase_name.strip()
        values = [clean_name] + [""] * (columns_count - 1)
        
        # 設定標籤和顏色 - 依要求移除亮綠色背景，改為黑色加粗
        self.tree.tag_configure('phase_header', 
                             foreground='black', 
                             font=('Arial', self.font_size, 'bold'))
        
        item_id = self.tree.insert('', 'end', values=tuple(values), tags=('phase_header',))
        return item_id

    def _hide_hover_popup(self):
        if self._hover_popup and self._hover_popup.winfo_exists():
            try:
                self._hover_popup.destroy()
            except Exception:
                pass
        self._hover_popup = None
        self._hover_row = None

    def insert_pass_item(self, values, step_number, full_response="", has_retry=False, parent=""):
        """插入PASS項目 (可指定父層節點)"""
        # 在Step Name前加上編號
        enhanced_values = list(values)
        step_name = f"{step_number}. {enhanced_values[0]}"
        
        # 只有當真正有RETRY時才添加標記，但用黑色文字
        if has_retry:
            step_name += " [RETRY但PASS]"
        
        enhanced_values[0] = step_name
        enhanced_values[2] = enhanced_values[2] + " [+點擊展開]"
        
        # 插入到指定的父節點下
        item_id = self.tree.insert(parent, 'end', values=enhanced_values)
        
        # 設定標籤和顏色 - PASS項目文字全部為黑色，包括RETRY
        command_value = str(enhanced_values[1]) if len(enhanced_values) > 1 else ""
        
        # 檢查是否有"未找到指令"，如果有則確保顯示為黑色
        if "未找到指令" in command_value:
            # "未找到指令"的情況顯示為黑色
            self.tree.item(item_id, tags=('pass_normal',))
            self.tree.tag_configure('pass_normal', foreground='black')
        elif has_retry:
            # RETRY項目也顯示為黑色（不再是紅色）
            self.tree.item(item_id, tags=('pass_retry',))
            self.tree.tag_configure('pass_retry', foreground='black')
        else:
            # 正常PASS項目顯示為黑色
            self.tree.item(item_id, tags=('pass',))
            self.tree.tag_configure('pass', foreground='black')
        
        # 儲存完整回應內容到字典中
        if full_response:
            self.full_content_storage[item_id] = full_response
        
        # 存儲測試項資料到 all_items_data 中
        item_data = {
            'item_id': item_id,
            'step_name': step_name,
            'command': command_value,
            'response': enhanced_values[2] if len(enhanced_values) > 2 else "",
            'result': enhanced_values[3] if len(enhanced_values) > 3 else "",
            'full_response': full_response,
            'has_retry': has_retry,
            'type': 'pass'
        }
        self.all_items_data.append(item_data)
        
        return item_id
    
    def insert_fail_item(self, values, full_response="", is_main_fail=True):
        """插入FAIL項目"""
        # 處理錯誤回應內容
        enhanced_values = list(values)
        enhanced_values[2] = enhanced_values[2] + " [+點擊展開]"
        
        item_id = self.tree.insert('', 'end', values=enhanced_values)
        
        # 設定標籤和顏色 - 預設全部為黑色，只有真正的錯誤才顯示紅色
        command_value = str(enhanced_values[1]) if len(enhanced_values) > 1 else ""
        error_value = str(enhanced_values[4]) if len(enhanced_values) > 4 else ""
        
        # 檢查是否為真正的錯誤（有具體錯誤訊息且不是"未找到指令"）
        is_real_error = False
        
        # 排除"未找到指令"的情況
        if "未找到指令" not in command_value:
            # 檢查是否有具體的錯誤訊息
            if error_value and error_value != "未知錯誤" and error_value != "無錯誤":
                # 檢查是否包含錯誤關鍵字
                error_keywords = ['FAIL', 'ERROR', 'NACK', 'TIMEOUT', '失敗', '錯誤', '超時', '異常']
                if any(keyword in error_value.upper() for keyword in error_keywords):
                    is_real_error = True
        
        if is_real_error:
            # 真正的錯誤項目顯示紅色
            self.tree.item(item_id, tags=('fail_main_red',))
            self.tree.tag_configure('fail_main_red', foreground='red', font=('Arial', 10, 'bold'))
        else:
            # 其他FAIL項目顯示黑色（包括"未找到指令"）
            self.tree.item(item_id, tags=('fail_main_black',))
            self.tree.tag_configure('fail_main_black', foreground='black', font=('Arial', 10, 'bold'))
        
        # 儲存完整回應內容到字典中
        if full_response:
            self.full_content_storage[item_id] = full_response
        
        # 存儲測試項資料到 all_items_data 中
        item_data = {
            'item_id': item_id,
            'step_name': enhanced_values[0],
            'command': command_value,
            'response': enhanced_values[2] if len(enhanced_values) > 2 else "",
            'result': enhanced_values[3] if len(enhanced_values) > 3 else "",
            'error': error_value,
            'full_response': full_response,
            'is_main_fail': is_main_fail,
            'type': 'fail'
        }
        self.all_items_data.append(item_data)
        
        return item_id
    
    def clear(self):
        """清空內容"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.full_content_storage.clear()  # 清空存儲字典
        self.all_items_data.clear()  # 清空所有測試項資料
    
    def _show_detail_dialog(self, content, current_item_id=None):
        """顯示詳細內容對話框（測項指令內容）"""
        try:
            # 檢查是否已經有詳細視窗存在
            if hasattr(self, '_detail_window') and self._detail_window and self._detail_window.winfo_exists():
                # 如果視窗存在，重用現有視窗
                detail_window = self._detail_window
                # 清空現有內容
                for widget in detail_window.winfo_children():
                    if isinstance(widget, tk.Label) and widget.cget('bg') == '#0B1D39':
                        # 這是標題標籤，保留
                        continue
                    widget.destroy()
                
                # 重新創建內容
                self._create_detail_window_content(detail_window, content, current_item_id)
                
                # 將視窗帶到前台
                detail_window.lift()
                detail_window.focus_force()
                return
            else:
                # 創建新視窗
                detail_window = tk.Toplevel()
                self._detail_window = detail_window  # 保存視窗引用
                
                # 創建視窗內容
                self._create_detail_window_content(detail_window, content, current_item_id)
            
        except Exception as e:
            print(f"顯示詳細內容對話框失敗: {e}")
    
    def _create_detail_window_content(self, detail_window, content, current_item_id):
        """創建詳細視窗的內容"""
        try:
            # 解析步驟名稱
            try:
                summary, step_label = self._build_cmd_resp_summary_and_label(content)
            except Exception:
                summary, step_label = (None, None)
            title = "測項指令內容" if not step_label else f"{step_label} +測項指令內容"
            detail_window.title(title)
            
            # 視窗背景改回白色（僅標題深藍）
            try:
                detail_window.configure(bg="#FFFFFF")
            except Exception:
                pass
                
            # 先設定最小尺寸，然後根據內容自動調整
            detail_window.geometry("800x700")  # 增加預設高度
            detail_window.minsize(700, 550)   # 增加最小尺寸，確保按鈕可見
            detail_window.maxsize(1200, 900)  # 設定最大尺寸
            
            # 讓視窗居中顯示，並確保不重疊
            detail_window.transient(detail_window.master)
            detail_window.grab_set()
            
            # 標題（深藍底白字）
            title_label = tk.Label(detail_window, text=title, 
                                   font=('Arial', 14, 'bold'), fg='#FFFFFF', bg="#0B1D39")
            title_label.pack(fill=tk.X, pady=(0, 0))
            
            # 文字框架（白底）
            text_frame = tk.Frame(detail_window, bg="#FFFFFF")
            text_frame.pack(fill=tk.BOTH, expand=1, padx=8, pady=8)
            
            # 文字框（白底黑字）
            text_widget = tk.Text(text_frame, wrap=tk.NONE, font=('Consolas', self.font_size), bg='white', fg='black', highlightthickness=0, borderwidth=0)
            text_widget.grid(row=0, column=0, sticky='nsew')
            
            # 垂直滾動條 - 做大一點，靠近文字區
            v_scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview, width=20)
            v_scrollbar.grid(row=0, column=1, sticky='ns')
            
            # 水平滾動條 - 做大一點
            h_scrollbar = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=text_widget.xview, width=20)
            h_scrollbar.grid(row=1, column=0, sticky='ew')
            
            # 設定框架的網格權重
            text_frame.grid_rowconfigure(0, weight=1)
            text_frame.grid_columnconfigure(0, weight=1)
            
            text_widget.config(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # 插入內容（前置加入整理）
            merged = str(content)
            try:
                summary = self._build_cmd_resp_summary(str(content))
                if summary.strip():
                    separator = "************************我是分隔線**************************************"
                    merged = summary + f"\n\n{separator}\n\n" + str(content)
            except Exception:
                pass
            if merged:
                text_widget.insert('1.0', merged)
                # 設定語法高亮（針對原始內容部分）
                self._apply_syntax_highlighting(text_widget, str(content))
            else:
                text_widget.insert('1.0', "沒有詳細內容可顯示")
            
            # 允許選取但不允許編輯
            text_widget.config(state=tk.NORMAL)
            
            # 按鈕框架（白底）- 緊湊佈局
            btn_frame = tk.Frame(detail_window, bg="#FFFFFF", height=60)  # 減少高度
            btn_frame.pack(pady=12, fill=tk.X, padx=10)
            btn_frame.pack_propagate(False)  # 防止框架被壓縮
            
            # 找到當前項目在 all_items_data 中的索引
            current_index = -1
            if current_item_id and self.all_items_data:
                for i, item_data in enumerate(self.all_items_data):
                    if item_data['item_id'] == current_item_id:
                        current_index = i
                        break
            
            # 上一頁按鈕（添加hover效果）
            prev_btn = tk.Button(btn_frame, text="上一頁", 
                                 command=lambda: self._show_previous_item(detail_window, text_widget, current_index),
                                 relief=tk.RAISED, bd=1, bg='#E8E8E8', fg='#333333',
                                 font=('Arial', 9, 'bold'), padx=10, pady=3)
            prev_btn.pack(side=tk.LEFT, padx=4, pady=6)
            
            # 下一頁按鈕（添加hover效果）
            next_btn = tk.Button(btn_frame, text="下一頁", 
                                 command=lambda: self._show_next_item(detail_window, text_widget, current_index),
                                 relief=tk.RAISED, bd=1, bg='#E8E8E8', fg='#333333',
                                 font=('Arial', 9, 'bold'), padx=10, pady=3)
            next_btn.pack(side=tk.LEFT, padx=4, pady=6)
            
                        # 複製按鈕（添加hover效果）
            copy_btn = tk.Button(btn_frame, text="複製內容", 
                                 command=lambda: self._copy_to_clipboard(text_widget.get('1.0', tk.END)),
                                 relief=tk.RAISED, bd=1, bg='#E8E8E8', fg='#333333',
                                 font=('Arial', 9, 'bold'), padx=10, pady=3)
            copy_btn.pack(side=tk.LEFT, padx=4, pady=6)
            
            # 搜尋標籤
            search_label = tk.Label(btn_frame, text="🔍", bg="#FFFFFF", font=('Arial', 9))
            search_label.pack(side=tk.LEFT, padx=(8, 2))
            
            # 搜尋輸入框
            search_entry = tk.Entry(btn_frame, width=25, font=('Arial', 9))
            search_entry.pack(side=tk.LEFT, padx=2)
            
            # 綁定輸入框內容變化，即時搜尋
            search_entry.bind('<KeyRelease>', lambda event: self._highlight_search_results(text_widget, search_entry.get()))
            
            # --- 使用者自義定高亮關鍵字介面 ---
            def add_to_user_keywords():
                new_kw = search_entry.get().strip()
                if not new_kw: return
                
                # 獲取目前列表
                kw_str = self.settings.get('user_highlight_keywords', 'SPEC_FAIL, spec_issue:')
                kw_list = [k.strip() for k in kw_str.split(',') if k.strip()]
                
                if new_kw not in kw_list:
                    kw_list.append(new_kw)
                    new_kw_str = ', '.join(kw_list)
                    self.settings['user_highlight_keywords'] = new_kw_str
                    
                    # 儲存設定
                    from ..settings_loader import save_settings
                    save_settings(self.settings)
                    
                    # 重新套用高亮
                    self._apply_syntax_highlighting(text_widget, text_widget.get('1.0', tk.END))
                    messagebox.showinfo("高亮設定", f"已將 '{new_kw}' 加到高亮關鍵字！")
            
            # 建立小按鈕
            plus_btn = tk.Button(btn_frame, text="+ 高亮", 
                                command=add_to_user_keywords,
                                relief=tk.RAISED, bd=1, bg='#FFF176', fg='#333333',
                                font=('Arial', 8, 'bold'), padx=5)
            plus_btn.pack(side=tk.LEFT, padx=2)
            

            
            # 設定按鈕hover效果
            self._setup_button_hover_effects(prev_btn, next_btn)
            self._setup_button_hover_effects(copy_btn, plus_btn)
            
            # 更新導航按鈕狀態
            self._update_navigation_buttons_in_window(detail_window, current_index)
            
            # 等待所有UI元素完全建立後再進行視窗定位和尺寸調整
            detail_window.after(100, lambda: self._finalize_window_setup(detail_window, text_widget))
            
        except Exception as e:
            print(f"創建詳細視窗內容失敗: {e}")
    
    def _show_search_dialog_in_detail(self, detail_window, text_widget):
        """在詳細視窗中顯示搜尋對話框"""
        try:
            # 如果已經有搜尋框架，先關閉它
            if hasattr(self, '_detail_search_frame') and self._detail_search_frame:
                self._detail_search_frame.destroy()
            
            # 創建搜尋框架 - 直接放在按鈕框架之前
            search_frame = tk.Frame(detail_window, bg='#f0f0f0', relief=tk.RAISED, bd=1)
            search_frame.pack(fill=tk.X, padx=8, pady=3)
            
            # 儲存搜尋框架引用
            self._detail_search_frame = search_frame
            
            # 搜尋標籤
            search_label = tk.Label(search_frame, text="🔍 搜尋:", bg='#f0f0f0', font=('Arial', 9, 'bold'))
            search_label.pack(side=tk.LEFT, padx=(8, 3))
            
            # 搜尋輸入框
            search_entry = tk.Entry(search_frame, width=30, font=('Arial', 9))
            search_entry.pack(side=tk.LEFT, padx=3)
            search_entry.focus_set()
            
            # 搜尋按鈕
            search_btn = tk.Button(search_frame, text="搜尋", 
                                   command=lambda: self._find_in_detail_text(text_widget, search_entry.get()),
                                   bg='#4CAF50', fg='white', font=('Arial', 8, 'bold'),
                                   padx=6, pady=1, relief=tk.FLAT, bd=1)
            search_btn.pack(side=tk.LEFT, padx=3)
            
            # 下一個按鈕
            next_btn = tk.Button(search_frame, text="下一個", 
                                 command=lambda: self._find_next_in_detail(text_widget, search_entry.get()),
                                 bg='#2196F3', fg='white', font=('Arial', 8, 'bold'),
                                 padx=6, pady=1, relief=tk.FLAT, bd=1)
            next_btn.pack(side=tk.LEFT, padx=3)
            
            # 上一個按鈕
            prev_btn = tk.Button(search_frame, text="上一個", 
                                 command=lambda: self._find_prev_in_detail(text_widget, search_entry.get()),
                                 bg='#2196F3', fg='white', font=('Arial', 8, 'bold'),
                                 padx=6, pady=1, relief=tk.FLAT, bd=1)
            prev_btn.pack(side=tk.LEFT, padx=3)
            
            # 關閉按鈕
            close_btn = tk.Button(search_frame, text="關閉", 
                                  command=lambda: self._close_detail_search(search_frame),
                                  bg='#f44336', fg='white', font=('Arial', 8, 'bold'),
                                  padx=6, pady=1, relief=tk.FLAT, bd=1)
            close_btn.pack(side=tk.LEFT, padx=3)
            
            # 綁定Enter鍵到搜尋
            search_entry.bind('<Return>', lambda e: self._find_in_detail_text(text_widget, search_entry.get()))
            
            # 綁定Escape鍵到關閉
            search_entry.bind('<Escape>', lambda e: self._close_detail_search(search_frame))
            
            print("搜尋對話框創建成功！")
            
        except Exception as e:
            print(f"創建詳細視窗搜尋對話框失敗: {e}")
            import traceback
            traceback.print_exc()
    
    def _finalize_window_setup(self, detail_window, text_widget):
        """完成視窗設定：定位、尺寸調整等"""
        try:
            # 確保視窗完全建立
            detail_window.update_idletasks()
            detail_window.update()
            
            # 計算視窗位置，避免重疊
            self._position_window_avoiding_overlap(detail_window)
            
            # 自動調整視窗大小以適應內容
            self._auto_resize_window(detail_window, text_widget)
            
            # 再次確保視窗在最上層
            detail_window.lift()
            detail_window.focus_set()
            
        except Exception as e:
            print(f"完成視窗設定失敗: {e}")
    
    def _position_window_avoiding_overlap(self, detail_window):
        """計算視窗位置，避免與其他視窗重疊"""
        try:
            # 等待視窗完全建立後再獲取尺寸
            detail_window.update_idletasks()
            detail_window.update()
            
            # 獲取螢幕尺寸
            screen_width = detail_window.winfo_screenwidth()
            screen_height = detail_window.winfo_screenheight()
            
            # 獲取視窗尺寸（確保視窗已完全建立）
            window_width = detail_window.winfo_width()
            window_height = detail_window.winfo_height()
            
            # 如果視窗尺寸為0或太小，使用預設值
            if window_width <= 100:
                window_width = 800
            if window_height <= 100:
                window_height = 600
            
            # 獲取所有現有的詳細視窗
            existing_windows = self._get_existing_detail_windows(detail_window)
            
            # 計算最佳位置，避免重疊
            best_position = self._calculate_best_window_position(
                window_width, window_height, screen_width, screen_height, existing_windows
            )
            
            # 設定視窗位置
            detail_window.geometry(f"{window_width}x{window_height}+{best_position[0]}+{best_position[1]}")
            
            # 確保視窗在最上層
            detail_window.lift()
            detail_window.attributes('-topmost', True)
            detail_window.attributes('-topmost', False)
            
            # 記錄此視窗位置，供後續視窗參考
            self._record_window_position(detail_window, best_position[0], best_position[1], window_width, window_height)
            
        except Exception as e:
            print(f"計算視窗位置失敗: {e}")
            # 如果計算失敗，使用預設居中位置
            try:
                screen_width = detail_window.winfo_screenwidth()
                screen_height = detail_window.winfo_screenheight()
                window_width = 800
                window_height = 600
                new_x = (screen_width - window_width) // 2
                new_y = (screen_height - window_height) // 2
                detail_window.geometry(f"{window_width}x{window_height}+{new_x}+{new_y}")
            except Exception:
                pass
    
    def _get_existing_detail_windows(self, current_window):
        """獲取所有現有的詳細視窗（排除當前視窗）"""
        existing_windows = []
        try:
            # 檢查是否有其他詳細視窗存在
            if hasattr(self, '_detail_window') and self._detail_window:
                if (self._detail_window != current_window and 
                    self._detail_window.winfo_exists() and 
                    self._detail_window.winfo_viewable()):
                    
                    try:
                        x = self._detail_window.winfo_x()
                        y = self._detail_window.winfo_y()
                        width = self._detail_window.winfo_width()
                        height = self._detail_window.winfo_height()
                        
                        # 確保視窗尺寸有效
                        if width > 0 and height > 0:
                            existing_windows.append({
                                'x': x, 'y': y, 'width': width, 'height': height
                            })
                    except Exception:
                        pass
            
            # 檢查是否有記錄的視窗位置
            if hasattr(self, '_window_positions'):
                for pos_info in self._window_positions:
                    if pos_info['window'] != current_window and pos_info['window'].winfo_exists():
                        existing_windows.append({
                            'x': pos_info['x'],
                            'y': pos_info['y'],
                            'width': pos_info['width'],
                            'height': pos_info['height']
                        })
                        
        except Exception as e:
            print(f"獲取現有視窗失敗: {e}")
        
        return existing_windows
    
    def _calculate_best_window_position(self, window_width, window_height, screen_width, screen_height, existing_windows):
        """計算最佳視窗位置，避免重疊"""
        try:
            # 如果沒有其他視窗，居中顯示
            if not existing_windows:
                return ((screen_width - window_width) // 2, (screen_height - window_height) // 2)
            
            # 嘗試多個位置，找到最佳的不重疊位置
            candidate_positions = []
            
            # 1. 嘗試放在第一個視窗的右側
            if existing_windows:
                first_window = existing_windows[0]
                right_x = first_window['x'] + first_window['width'] + 20
                if right_x + window_width <= screen_width:
                    candidate_positions.append((right_x, first_window['y']))
            
            # 2. 嘗試放在第一個視窗的下方
            if existing_windows:
                first_window = existing_windows[0]
                bottom_y = first_window['y'] + first_window['height'] + 20
                if bottom_y + window_height <= screen_height:
                    candidate_positions.append((first_window['x'], bottom_y))
            
            # 3. 嘗試放在第一個視窗的左側
            if existing_windows:
                first_window = existing_windows[0]
                left_x = first_window['x'] - window_width - 20
                if left_x >= 0:
                    candidate_positions.append((left_x, first_window['y']))
            
            # 4. 嘗試放在第一個視窗的上方
            if existing_windows:
                first_window = existing_windows[0]
                top_y = first_window['y'] - window_height - 20
                if top_y >= 0:
                    candidate_positions.append((first_window['x'], top_y))
            
            # 5. 嘗試螢幕的四個角落
            corner_positions = [
                (20, 20),  # 左上角
                (screen_width - window_width - 20, 20),  # 右上角
                (20, screen_height - window_height - 20),  # 左下角
                (screen_width - window_width - 20, screen_height - window_height - 20)  # 右下角
            ]
            
            for corner_pos in corner_positions:
                if (corner_pos[0] >= 0 and corner_pos[0] + window_width <= screen_width and
                    corner_pos[1] >= 0 and corner_pos[1] + window_height <= screen_height):
                    candidate_positions.append(corner_pos)
            
            # 6. 居中位置作為後備
            center_pos = ((screen_width - window_width) // 2, (screen_height - window_height) // 2)
            candidate_positions.append(center_pos)
            
            # 評估每個候選位置，選擇重疊最少的位置
            best_position = center_pos
            min_overlap = float('inf')
            
            for pos in candidate_positions:
                overlap_score = self._calculate_overlap_score(pos[0], pos[1], window_width, window_height, existing_windows)
                if overlap_score < min_overlap:
                    min_overlap = overlap_score
                    best_position = pos
            
            # 確保位置在螢幕範圍內
            best_x = max(0, min(best_position[0], screen_width - window_width))
            best_y = max(0, min(best_position[1], screen_height - window_height))
            
            return (best_x, best_y)
            
        except Exception as e:
            print(f"計算最佳視窗位置失敗: {e}")
            # 返回居中位置作為後備
            return ((screen_width - window_width) // 2, (screen_height - window_height) // 2)
    
    def _calculate_overlap_score(self, x, y, width, height, existing_windows):
        """計算視窗與現有視窗的重疊分數（分數越低越好）"""
        try:
            total_overlap = 0
            for existing in existing_windows:
                # 檢查兩個矩形是否重疊
                if not (x + width <= existing['x'] or 
                       existing['x'] + existing['width'] <= x or
                       y + height <= existing['y'] or 
                       existing['y'] + existing['height'] <= y):
                    
                    # 計算重疊面積
                    overlap_width = min(x + width, existing['x'] + existing['width']) - max(x, existing['x'])
                    overlap_height = min(y + height, existing['y'] + existing['height']) - max(y, existing['y'])
                    overlap_area = max(0, overlap_width) * max(0, overlap_height)
                    
                    # 重疊面積越大，分數越高（越差）
                    total_overlap += overlap_area
            
            # 額外懲罰：距離螢幕邊緣太近
            edge_penalty = 0
            if x < 50 or y < 50 or x + width > screen_width - 50 or y + height > screen_height - 50:
                edge_penalty = 1000
            
            return total_overlap + edge_penalty
            
        except Exception as e:
            print(f"計算重疊分數失敗: {e}")
            return float('inf')
    
    def _record_window_position(self, window, x, y, width, height):
        """記錄視窗位置，供後續視窗參考"""
        try:
            if not hasattr(self, '_window_positions'):
                self._window_positions = []
            
            # 移除舊的記錄
            self._window_positions = [pos for pos in self._window_positions if pos['window'] != window]
            
            # 添加新記錄
            self._window_positions.append({
                'window': window,
                'x': x,
                'y': y,
                'width': width,
                'height': height
            })
            
            # 限制記錄數量，避免記憶體洩漏
            if len(self._window_positions) > 10:
                self._window_positions = self._window_positions[-10:]
                
        except Exception as e:
            print(f"記錄視窗位置失敗: {e}")
    
    def _setup_button_hover_effects(self, prev_btn, next_btn):
        """為導航按鈕設置hover效果"""
        def on_enter(event):
            event.widget.config(bg='#4CAF50', fg='white')  # 綠色背景，白色文字
        
        def on_leave(event):
            event.widget.config(bg='#E8E8E8', fg='#333333')  # 恢復原始顏色
        
        # 綁定hover事件
        prev_btn.bind('<Enter>', on_enter)
        prev_btn.bind('<Leave>', on_leave)
        next_btn.bind('<Enter>', on_enter)
        next_btn.bind('<Leave>', on_leave)
    
    def _auto_resize_window(self, detail_window, text_widget):
        """根據文字內容自動調整視窗大小，確保導航按鈕始終可見"""
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
            
            # 計算文字區域的寬度和高度（確保按鈕可見）
            text_width = min(max_line_length * char_width + 80, 800)   # 減少邊距，最大800
            text_height = min(total_lines * char_height + 150, 600)    # 減少邊距，最大600
            
            # 設定視窗大小（確保按鈕框架完全可見）
            window_width = max(600, text_width + 40)   # 減少額外寬度
            window_height = max(500, text_height + 120)  # 增加額外高度，確保按鈕框架完全可見
            
            # 限制最大尺寸（更嚴格，避免視窗過大）
            window_width = min(window_width, 900)   # 從1200減少到900
            window_height = min(window_height, 800)  # 從700增加到800，確保按鈕可見
            
            # 獲取當前視窗位置
            current_x = detail_window.winfo_x()
            current_y = detail_window.winfo_y()
            
            # 更新視窗大小（保持當前位置）
            detail_window.geometry(f"{window_width}x{window_height}+{current_x}+{current_y}")
            
            # 檢查調整後是否會與其他視窗重疊
            if self._check_window_overlap(detail_window, window_width, window_height):
                # 如果會重疊，重新計算位置
                detail_window.update_idletasks()
                self._position_window_avoiding_overlap(detail_window)
            
        except Exception as e:
            print(f"自動調整視窗大小失敗: {e}")
    
    def _check_window_overlap(self, detail_window, window_width, window_height):
        """檢查視窗是否會與其他視窗重疊"""
        try:
            current_x = detail_window.winfo_x()
            current_y = detail_window.winfo_y()
            
            # 獲取所有現有的詳細視窗
            existing_windows = self._get_existing_detail_windows(detail_window)
            
            for existing in existing_windows:
                # 檢查兩個矩形是否重疊
                if not (current_x + window_width <= existing['x'] or 
                       existing['x'] + existing['width'] <= current_x or
                       current_y + window_height <= existing['y'] or 
                       existing['y'] + existing['height'] <= current_y):
                    return True  # 會重疊
            
            return False  # 不會重疊
            
        except Exception as e:
            print(f"檢查視窗重疊失敗: {e}")
            return False
    
    def _update_title_label(self, detail_window, new_title):
        """更新標題標籤"""
        try:
            # 找到標題標籤並更新
            for widget in detail_window.winfo_children():
                if isinstance(widget, tk.Label) and widget.cget('bg') == '#0B1D39':
                    widget.config(text=new_title)
                    break
        except Exception as e:
            print(f"更新標題標籤失敗: {e}")
 
    def _build_cmd_resp_summary(self, content: str) -> str:
        """從內容中擷取所有 > 與其後續的 < 行，條列「指令1. 指令2. …」"""
        try:
            summary, _ = self._build_cmd_resp_summary_and_label(content)
            return summary
        except Exception:
            return "[指令/回應整理]\n(產生摘要時發生例外)"

    def _build_cmd_resp_summary_and_label(self, content: str):
        """回傳 (summary_text, step_label) 供標題使用"""
        try:
            import re
            groups = []
            current = None
            step_label = None
            for raw in str(content).splitlines():
                line = re.sub(r'^\s*\d+\.\s*', '', raw)
                if step_label is None and 'Do @STEP' in line:
                    try:
                        pos = line.index('Do @STEP')
                        step_label = line[pos:].strip()
                    except Exception:
                        step_label = line.strip()
                m_cmd = re.search(r'>\s*(.+)$', line)
                m_resp = re.search(r'<\s*(.*)$', line)
                if m_cmd:
                    if current:
                        groups.append(current)
                    current = {'cmd': m_cmd.group(1), 'resps': []}
                    continue
                if m_resp:
                    if not current:
                        current = {'cmd': '', 'resps': []}
                    current['resps'].append(m_resp.group(1))
            if current:
                groups.append(current)
            count = len(groups)
            header = "[指令/回應整理]" if step_label is None else f"{step_label}    [指令/回應整理 {count}筆]"
            out_lines = [header] if step_label else [f"[指令/回應整理 {count}筆]"]
            if not groups:
                out_lines.append("(未偵測到 >/< 指令或回應)")
                return ("\n".join(out_lines), step_label)
            for idx, g in enumerate(groups, 1):
                out_lines.append(f"指令{idx}.")
                out_lines.append(f"> {g.get('cmd','')}")
                for r in g.get('resps', []):
                    out_lines.append(f"< {r}")
                out_lines.append("")
            return ("\n".join(out_lines).rstrip(), step_label)
        except Exception:
            return ("[指令/回應整理]\n(產生摘要時發生例外)", None)
    
    def _show_previous_item(self, detail_window, text_widget, current_index):
        """顯示上一個測試項"""
        if current_index > 0 and self.all_items_data:
            prev_index = current_index - 1
            prev_item_data = self.all_items_data[prev_index]
            content = prev_item_data.get('full_response', '沒有詳細內容可顯示')
            
            # 更新文字內容
            text_widget.config(state=tk.NORMAL)
            text_widget.delete('1.0', tk.END)
            text_widget.insert('1.0', str(content))
            self._apply_syntax_highlighting(text_widget, str(content))
            text_widget.config(state=tk.NORMAL)
            
            # 更新標題
            new_title = f"測項指令內容 - {prev_item_data['step_name']}"
            detail_window.title(new_title)
            
            # 更新標題標籤
            self._update_title_label(detail_window, new_title)
            
            # 更新按鈕狀態
            self._update_navigation_buttons_in_window(detail_window, prev_index)
    
    def _show_next_item(self, detail_window, text_widget, current_index):
        """顯示下一個測試項"""
        if self.all_items_data and current_index < len(self.all_items_data) - 1:
            # 計算下一個索引
            next_index = current_index + 1
            next_item_data = self.all_items_data[next_index]
            content = next_item_data.get('full_response', '沒有詳細內容可顯示')
            
            # 更新文字內容
            text_widget.config(state=tk.NORMAL)
            text_widget.delete('1.0', tk.END)
            text_widget.insert('1.0', str(content))
            self._apply_syntax_highlighting(text_widget, str(content))
            text_widget.config(state=tk.NORMAL)
            
            # 更新標題
            new_title = f"測項指令內容 - {next_item_data['step_name']}"
            detail_window.title(new_title)
            
            # 更新標題標籤
            self._update_title_label(detail_window, new_title)
            
            # 更新按鈕狀態
            self._update_navigation_buttons_in_window(detail_window, next_index)
    
    def _update_navigation_buttons(self, prev_btn, next_btn, current_index):
        """更新導航按鈕狀態"""
        if prev_btn and next_btn:
            # 更新上一頁按鈕狀態
            if current_index <= 0:
                prev_btn.config(state=tk.DISABLED)
            else:
                prev_btn.config(state=tk.NORMAL)
            
            # 更新下一頁按鈕狀態
            if current_index >= len(self.all_items_data) - 1:
                next_btn.config(state=tk.DISABLED)
            else:
                next_btn.config(state=tk.NORMAL)
    
    def _update_navigation_buttons_in_window(self, detail_window, current_index):
        """更新視窗中的導航按鈕狀態"""
        prev_btn = None
        next_btn = None
        text_widget = None
        
        # 找到文字框和按鈕
        for widget in detail_window.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Text):
                        text_widget = child
                    elif isinstance(child, tk.Button):
                        if child.cget('text') == '上一頁':
                            prev_btn = child
                        elif child.cget('text') == '下一頁':
                            next_btn = child
        
        # 更新按鈕狀態和命令
        if prev_btn and next_btn and text_widget:
            # 更新上一頁按鈕狀態
            if current_index <= 0:
                prev_btn.config(state=tk.DISABLED)
            else:
                prev_btn.config(state=tk.NORMAL)
            
            # 更新下一頁按鈕狀態 - 允許進行到最後一個項目
            if current_index >= len(self.all_items_data) - 1:
                next_btn.config(state=tk.DISABLED)
            else:
                next_btn.config(state=tk.NORMAL)
                
            # 更新按鈕的命令，使用正確的參數和閉包
            prev_btn.config(command=lambda idx=current_index: self._show_previous_item(detail_window, text_widget, idx))
            next_btn.config(command=lambda idx=current_index: self._show_next_item(detail_window, text_widget, idx))
    
    def _apply_syntax_highlighting(self, text_widget, content):
        """對詳細內容應用語法高亮"""
        try:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                line_start = f"{i+1}.0"
                line_end = f"{i+1}.end"
                
                # UART指令 - 藍色
                if '(UART) >' in line or '> ' in line:
                    text_widget.tag_add('cmd', line_start, line_end)
                    text_widget.tag_configure('cmd', foreground='blue', font=('Consolas', self.font_size, 'bold'))
                
                # UART回應 - 紫色
                elif '(UART) <' in line or '< ' in line:
                    text_widget.tag_add('resp', line_start, line_end)
                    text_widget.tag_configure('resp', foreground='purple')
                
                # 錯誤行 - 紅色
                elif any(keyword in line.upper() for keyword in ['FAIL', 'ERROR', 'NACK']):
                    text_widget.tag_add('error', line_start, line_end)
                    text_widget.tag_configure('error', foreground='red', font=('Consolas', self.font_size, 'bold'))
                
                # Step行 - 綠色
                elif 'Do @STEP' in line or '@STEP' in line:
                    text_widget.tag_add('step', line_start, line_end)
                    text_widget.tag_configure('step', foreground='green', font=('Consolas', self.font_size, 'bold'))
                
                # PASS - 綠色
                elif 'PASS' in line.upper():
                    text_widget.tag_add('pass', line_start, line_end)
                    text_widget.tag_configure('pass', foreground='green', font=('Consolas', self.font_size, 'bold'))
                
                # 其他內容 - 黑色（預設）
                else:
                    text_widget.tag_add('normal', line_start, line_end)
                    text_widget.tag_configure('normal', foreground='black')

            # --- 使用者自定義高亮關鍵字 ---
            kw_str = self.settings.get('user_highlight_keywords', 'SPEC_FAIL, spec_issue:')
            user_kws = [k.strip() for k in kw_str.split(',') if k.strip()]
            
            if user_kws:
                # 定義高亮標籤底色 (淺黃帶加強邊框或是淡粉色)
                text_widget.tag_configure('user_keyword_line', background='#FFFF00', foreground='black', font=('Consolas', self.font_size, 'bold'))
                
                for kw in user_kws:
                    start_pos = '1.0'
                    while True:
                        pos = text_widget.search(kw, start_pos, tk.END, nocase=True)
                        if not pos: break
                        
                        # 高亮整行
                        line_num = pos.split('.')[0]
                        line_start_idx = f"{line_num}.0"
                        line_end_idx = f"{line_num}.end"
                        text_widget.tag_add('user_keyword_line', line_start_idx, line_end_idx)
                        
                        start_pos = f"{line_num}.end + 1c"
        except Exception as e:
            print(f"語法高亮應用失敗: {e}")
    
    def _is_fail_content(self, content):
        """檢查內容是否為FAIL項目"""
        if not content:
            return False
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in [
            'is fail', 'is failed', 'fail', 'error', 'wrong', 
            'segmentation fault', 'core dumped', 'executes fail',
            "doesn't match", 'timeout', 'exception'
        ])
    
    def _extract_error_reason_from_content(self, content):
        """從內容中提取錯誤原因"""
        if not content:
            return ""
        
        lines = content.split('\n')
        
        # 優先找到包含 "is Fail" 的行
        for line in lines:
            if "is Fail" in line:
                # 處理類似 "VSCH026-043:Chec Frimware version is Fail ! <ErrorCode: BSFR18>" 的格式
                if ':' in line and "is Fail" in line:
                    # 擷取冒號後的部分
                    after_colon = line.split(":", 1)[1].strip()
                    # 找到 "is Fail" 的位置
                    if "is Fail" in after_colon:
                        fail_pos = after_colon.find("is Fail")
                        # 擷取到 "is Fail" 結束的部分，去掉後面的 <ErrorCode: xxx> 和時間戳記
                        test_name_with_fail = after_colon[:fail_pos + 7].strip()  # 7 = len("is Fail")
                        
                        # 移除時間戳記（如 "2025/08/07 08:53:36 [1]" 格式）
                        if '[' in test_name_with_fail and ']' in test_name_with_fail:
                            bracket_start = test_name_with_fail.find('[')
                            bracket_end = test_name_with_fail.find(']')
                            if bracket_start != -1 and bracket_end != -1:
                                # 檢查括號前是否有時間戳記格式
                                before_bracket = test_name_with_fail[:bracket_start].strip()
                                if '/' in before_bracket and ':' in before_bracket:
                                    # 移除時間戳記部分
                                    test_name_with_fail = test_name_with_fail[bracket_end + 1:].strip()
                        
                        return test_name_with_fail
                elif "is Fail" in line:
                    # 如果沒有冒號但有 "is Fail"，直接擷取到 "is Fail" 結束
                    fail_pos = line.find("is Fail")
                    if fail_pos != -1:
                        # 找到 <ErrorCode: 的位置
                        error_code_pos = line.find("<ErrorCode:")
                        if error_code_pos != -1:
                            return line[:error_code_pos].strip()
                        else:
                            return line[:fail_pos + 7].strip()
        
        # 如果沒有找到 "is Fail"，嘗試找到其他錯誤資訊
        for line in lines:
            # 尋找包含 "All Test Aborted" 的行
            if "All Test Aborted" in line:
                return line
        
        # 尋找其他嚴重錯誤
        for line in lines:
            line_lower = line.lower()
            if any(critical_error in line_lower for critical_error in [
                'segmentation fault', 'core dumped', 'executes fail', 
                "doesn't match", 'timeout', 'exception'
            ]):
                return line
        
        return ""
    
    def _format_content_with_error_highlighting(self, content):
        """為內容中的錯誤行添加背景色標記"""
        if not content:
            return content
        
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line_lower = line.lower()
            # 檢查是否包含錯誤關鍵字
            if self._is_error_line(line) or 'is fail' in line_lower or 'is failed' in line_lower:
                # 為錯誤行添加背景色標記
                formatted_lines.append(f"🔴 {line}")
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _is_error_line(self, line):
        """統一的錯誤行識別邏輯"""
        if not line:
            return False
        
        line_lower = line.lower()
        # 統一的錯誤關鍵字列表
        error_keywords = [
            'segmentation fault', 'core dumped', 'executes fail', 
            "doesn't match", 'timeout', 'exception', 'wrong',
            'fail', 'error', 'nack'
        ]
        
        return any(keyword in line_lower for keyword in error_keywords)
    
    def _copy_to_clipboard(self, content):
        """複製內容到剪貼板"""
        try:
            import tkinter as tk
            root = tk._default_root
            root.clipboard_clear()
            root.clipboard_append(str(content))
            print("內容已複製到剪貼板")
        except Exception as e:
            print(f"複製失敗: {e}")
    

    
    def _find_in_detail_text(self, text_widget, search_text):
        """在詳細文字中搜尋文字"""
        try:
            if not search_text.strip():
                return
            
            # 清除之前的搜尋標記
            text_widget.tag_remove('search_highlight', '1.0', tk.END)
            
            # 搜尋文字
            start_pos = '1.0'
            found_positions = []
            
            while True:
                pos = text_widget.search(search_text, start_pos, tk.END, nocase=True)
                if not pos:
                    break
                
                end_pos = f"{pos}+{len(search_text)}c"
                found_positions.append((pos, end_pos))
                start_pos = end_pos
            
            if found_positions:
                # 高亮所有搜尋結果
                for start, end in found_positions:
                    text_widget.tag_add('search_highlight', start, end)
                
                # 設定高亮樣式
                text_widget.tag_configure('search_highlight', background='yellow', foreground='black')
                
                # 跳轉到第一個結果
                text_widget.see(found_positions[0][0])
                text_widget.mark_set(tk.INSERT, found_positions[0][0])
                
                # 保存搜尋狀態
                self._detail_search_positions = found_positions
                self._detail_search_current_index = 0
                
                print(f"找到 {len(found_positions)} 個搜尋結果")
            else:
                print("未找到搜尋結果")
                
        except Exception as e:
            print(f"搜尋失敗: {e}")
    
    def _find_next_in_detail(self, text_widget, search_text):
        """在詳細文字中搜尋下一個"""
        try:
            if not hasattr(self, '_detail_search_positions') or not self._detail_search_positions:
                self._find_in_detail_text(text_widget, search_text)
                return
            
            if self._detail_search_current_index < len(self._detail_search_positions) - 1:
                self._detail_search_current_index += 1
            else:
                self._detail_search_current_index = 0
            
            pos = self._detail_search_positions[self._detail_search_current_index]
            text_widget.see(pos[0])
            text_widget.mark_set(tk.INSERT, pos[0])
            
        except Exception as e:
            print(f"搜尋下一個失敗: {e}")
    
    def _find_prev_in_detail(self, text_widget, search_text):
        """在詳細文字中搜尋上一個"""
        try:
            if not hasattr(self, '_detail_search_positions') or not self._detail_search_positions:
                self._find_in_detail_text(text_widget, search_text)
                return
            
            if self._detail_search_current_index > 0:
                self._detail_search_current_index -= 1
            else:
                self._detail_search_current_index = len(self._detail_search_positions) - 1
            
            pos = self._detail_search_positions[self._detail_search_current_index]
            text_widget.see(pos[0])
            text_widget.mark_set(tk.INSERT, pos[0])
            
        except Exception as e:
            print(f"搜尋上一個失敗: {e}")
    
    def _close_detail_search(self, search_frame):
        """關閉詳細視窗的搜尋功能"""
        try:
            # 清除搜尋高亮
            if hasattr(self, '_detail_search_frame') and self._detail_search_frame:
                # 找到文字元件
                for widget in self._detail_search_frame.master.winfo_children():
                    if isinstance(widget, tk.Frame):
                        for child in widget.winfo_children():
                            if isinstance(child, tk.Text):
                                child.tag_remove('search_highlight', '1.0', tk.END)
                                break
                        break
            
            # 移除搜尋框架
            search_frame.destroy()
            self._detail_search_frame = None
            
            # 清除搜尋狀態
            if hasattr(self, '_detail_search_positions'):
                delattr(self, '_detail_search_positions')
            if hasattr(self, '_detail_search_current_index'):
                delattr(self, '_detail_search_current_index')
                
        except Exception as e:
            print(f"關閉搜尋失敗: {e}")
    
    def _close_search_in_main(self, btn_frame, text_widget):
        """關閉主按鈕區域中的搜尋元件"""
        try:
            # 找到並移除搜尋相關的元件
            for widget in btn_frame.winfo_children():
                if isinstance(widget, (tk.Label, tk.Entry)) or (isinstance(widget, tk.Button) and widget.cget('text') == '✕'):
                    widget.destroy()
            
            # 重新設定搜尋按鈕的點擊事件，讓它可以重新顯示搜尋元件
            for widget in btn_frame.winfo_children():
                if isinstance(widget, tk.Button) and widget.cget('text') == '隱藏搜尋':
                    widget.config(command=lambda: self._show_search_in_main(btn_frame, text_widget))
                    widget.config(text="搜尋")
                    break
                    
        except Exception as e:
            print(f"關閉主搜尋元件失敗: {e}")
    
    def _show_search_in_main(self, btn_frame, text_widget):
        """在主按鈕區域顯示搜尋元件"""
        try:
            # 搜尋標籤
            search_label = tk.Label(btn_frame, text="🔍", bg="#FFFFFF", font=('Arial', 9))
            search_label.pack(side=tk.LEFT, padx=(8, 2))
            
            # 搜尋輸入框
            search_entry = tk.Entry(btn_frame, width=25, font=('Arial', 9))
            search_entry.pack(side=tk.LEFT, padx=2)
            search_entry.focus_set()
            
            # 關閉搜尋按鈕
            close_search_btn = tk.Button(btn_frame, text="✕", 
                                         command=lambda: self._close_search_in_main(btn_frame, text_widget),
                                         bg='#f44336', fg='white', font=('Arial', 8, 'bold'),
                                         padx=6, pady=1, relief=tk.FLAT, bd=1)
            close_search_btn.pack(side=tk.LEFT, padx=2)
            
            # 綁定Enter鍵跳轉到下一個搜尋結果
            search_entry.bind('<Return>', lambda event: self._jump_to_next_search_result(text_widget, search_entry.get()))
            
            # 綁定輸入框內容變化，即時搜尋
            search_entry.bind('<KeyRelease>', lambda event: self._highlight_search_results(text_widget, search_entry.get()))
            
            # 關閉按鈕（關閉整個彈出視窗）
            close_btn = tk.Button(btn_frame, text="✕", 
                                 command=lambda: detail_window.destroy(),
                                 bg='#f44336', fg='white', font=('Arial', 8, 'bold'),
                                 padx=6, pady=1, relief=tk.FLAT, bd=1)
            close_btn.pack(side=tk.LEFT, padx=2)
            # 關閉按鈕（關閉整個彈出視窗）
            close_btn = tk.Button(btn_frame, text="✕", 
                                 command=lambda: detail_window.destroy(),
                                 bg='#f44336', fg='white', font=('Arial', 8, 'bold'),
                                 padx=6, pady=1, relief=tk.FLAT, bd=1)
            close_btn.pack(side=tk.LEFT, padx=2)
            # 更新搜尋按鈕的點擊事件，讓它可以關閉搜尋元件
            for widget in btn_frame.winfo_children():
                if isinstance(widget, tk.Button) and widget.cget('text') == '搜尋':
                    widget.config(command=lambda: self._close_search_in_main(btn_frame, text_widget))
                    widget.config(text="隱藏搜尋")
                    break
                    
        except Exception as e:
            print(f"顯示主搜尋元件失敗: {e}")
    
    def _highlight_search_results(self, text_widget, search_text):
        """高亮顯示搜尋結果"""
        try:
            if not search_text.strip():
                # 如果搜尋文字為空，清除所有高亮
                text_widget.tag_remove('search_highlight', '1.0', tk.END)
                return
            
            # 清除之前的高亮
            text_widget.tag_remove('search_highlight', '1.0', tk.END)
            
            # 設定搜尋高亮標籤樣式
            text_widget.tag_configure('search_highlight', background='#FFFF00', foreground='#000000')
            
            # 搜尋並高亮所有匹配的文字
            start_pos = '1.0'
            count = 0
            positions = []  # 儲存所有搜尋結果的位置
            
            while True:
                # 搜尋下一個匹配
                pos = text_widget.search(search_text, start_pos, tk.END, nocase=True)
                if not pos:
                    break
                
                # 計算結束位置
                end_pos = f"{pos}+{len(search_text)}c"
                
                # 應用高亮標籤
                text_widget.tag_add('search_highlight', pos, end_pos)
                
                # 儲存位置
                positions.append(pos)
                
                # 移動到下一位置
                start_pos = end_pos
                count += 1
            
            # 顯示搜尋結果數量
            if count > 0:
                print(f"找到 {count} 個搜尋結果")
                
                # 儲存搜尋結果位置到實例變數
                self._search_positions = positions
                
                # 如果沒有當前搜尋位置，從第一個開始
                if not hasattr(self, '_current_search_index'):
                    self._current_search_index = 0
                
                # 確保索引在有效範圍內
                if self._current_search_index >= len(positions):
                    self._current_search_index = 0
                
                # 跳轉到當前搜尋結果
                current_pos = positions[self._current_search_index]
                text_widget.see(current_pos)
                
                # 設定游標到當前搜尋結果
                text_widget.mark_set(tk.INSERT, current_pos)
                
                # 更新搜尋索引，為下次Enter鍵做準備
                self._current_search_index = (self._current_search_index + 1) % count
                
            else:
                print(f"未找到 '{search_text}' 的搜尋結果")
                # 重置搜尋索引和位置
                if hasattr(self, '_current_search_index'):
                    delattr(self, '_current_search_index')
                if hasattr(self, '_search_positions'):
                    delattr(self, '_search_positions')
                
        except Exception as e:
            print(f"高亮搜尋結果失敗: {e}")
    
    def _jump_to_next_search_result(self, text_widget, search_text):
        """跳轉到下一個搜尋結果"""
        try:
            if not search_text.strip():
                return
            
            # 如果沒有搜尋結果位置，先執行搜尋
            if not hasattr(self, '_search_positions') or not self._search_positions:
                self._highlight_search_results(text_widget, search_text)
                return
            
            # 如果沒有當前搜尋索引，從第一個開始
            if not hasattr(self, '_current_search_index'):
                self._current_search_index = 0
            
            # 確保索引在有效範圍內
            if self._current_search_index >= len(self._search_positions):
                self._current_search_index = 0
            
            # 跳轉到當前搜尋結果
            current_pos = self._search_positions[self._current_search_index]
            text_widget.see(current_pos)
            
            # 設定游標到當前搜尋結果
            text_widget.mark_set(tk.INSERT, current_pos)
            
            # 更新搜尋索引，為下次Enter鍵做準備
            self._current_search_index = (self._current_search_index + 1) % len(self._search_positions)
            
            print(f"跳轉到第 {self._current_search_index} 個搜尋結果")
            
        except Exception as e:
            print(f"跳轉搜尋結果失敗: {e}")

# 其他類別保持不變...
