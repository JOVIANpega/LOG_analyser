# -*- coding: utf-8 -*-
"""
Search Handler Module
Handles search functionality within the application (Mixin)
"""

import tkinter as tk
import traceback

class SearchHandlerMixin:
    """Mixin for handling search operations in the Log Analyzer"""
    
    def _on_search_change(self, event):
        """搜尋內容改變時的即時搜尋"""
        try:
            # 如果輸入超過2個字元就開始搜尋
            search_text = self.search_var.get().strip()
            if len(search_text) >= 2:
                self._search_next()
            elif len(search_text) == 0:
                self._clear_search()
        except Exception as e:
            print(f"搜尋改變事件錯誤: {e}")
            traceback.print_exc()
    
    def _on_search_enter(self, event=None):
        """按下Enter鍵時執行搜尋"""
        try:
            search_text = self.search_var.get().strip()
            if search_text:
                self._add_to_search_history(search_text)
            self._search_next()
        except Exception as e:
            print(f"Enter搜尋事件錯誤: {e}")
            traceback.print_exc()
    
    def _search_next(self):
        """搜尋下一個匹配項目"""
        try:
            search_text = self.search_var.get().strip()
            if not search_text:
                return
            
            # 檢查當前選中的標籤頁
            current_tab = self.notebook.select()
            
            # 獲取當前選中的標籤頁索引
            current_tab_index = self.notebook.index(current_tab)
            
            if current_tab_index == 2:  # 原始LOG標籤頁
                # 在原始LOG標籤頁中搜尋
                if hasattr(self, 'log_text_enhanced') and hasattr(self.log_text_enhanced, 'text'):
                    self._search_next_in_text(self.log_text_enhanced.text, search_text)
                elif hasattr(self, 'raw_text'):
                    self._search_next_in_text(self.raw_text, search_text)
                else:
                    print("未找到原始LOG Text元件")
            else:
                # 在其他標籤頁中搜尋
                self._perform_search()
                
        except Exception as e:
            print(f"搜尋下一個時發生錯誤: {e}")
            traceback.print_exc()
    
    def _search_prev(self):
        """搜尋上一個匹配項目"""
        try:
            search_text = self.search_var.get().strip()
            if not search_text:
                return
            
            # 檢查當前選中的標籤頁
            current_tab = self.notebook.select()
            
            # 獲取當前選中的標籤頁索引
            current_tab_index = self.notebook.index(current_tab)
            
            if current_tab_index == 2:  # 原始LOG標籤頁
                # 在原始LOG標籤頁中搜尋
                if hasattr(self, 'log_text_enhanced') and hasattr(self.log_text_enhanced, 'text'):
                    self._search_prev_in_text(self.log_text_enhanced.text, search_text)
                elif hasattr(self, 'raw_text'):
                    self._search_prev_in_text(self.raw_text, search_text)
                else:
                    print("未找到原始LOG Text元件")
            else:
                # 在其他標籤頁中搜尋
                self._perform_search()
                
        except Exception as e:
            print(f"搜尋上一個時發生錯誤: {e}")
            traceback.print_exc()
            
    def _on_search_next_click(self):
        """點擊下一個按鈕"""
        search_text = self.search_var.get().strip()
        if search_text:
            self._add_to_search_history(search_text)
        self._search_next()

    def _on_search_prev_click(self):
        """點擊上一個按鈕"""
        search_text = self.search_var.get().strip()
        if search_text:
            self._add_to_search_history(search_text)
        self._search_prev()
    
    def _search_next_in_text(self, text_widget, search_text):
        """在Text元件中搜尋下一個"""
        try:
            # 檢查Text元件是否有內容
            content = text_widget.get('1.0', tk.END)
            
            if len(content) <= 1:  # 只有換行符
                self._update_search_count(0)
                return
            
            # 先清除之前的選取
            text_widget.tag_remove(tk.SEL, '1.0', tk.END)
            text_widget.tag_remove('search_highlight', '1.0', tk.END)
            
            # 設定搜尋高亮樣式
            text_widget.tag_configure('search_highlight', background='#FFFF00', foreground='#000000')
            
            # 計算總匹配數量
            count = 0
            pos = '1.0'
            while True:
                pos = text_widget.search(search_text, pos, tk.END, nocase=True)
                if not pos:
                    break
                count += 1
                end_pos = f"{pos}+{len(search_text)}c"
                text_widget.tag_add('search_highlight', pos, end_pos)
                pos = end_pos
            
            # 更新搜尋計數
            self._update_search_count(count)
            
            # 從當前游標位置開始搜尋
            pos = text_widget.search(search_text, tk.INSERT, tk.END, nocase=True)
            if pos:
                # 找到匹配項目
                end_pos = f"{pos}+{len(search_text)}c"
                text_widget.mark_set(tk.INSERT, end_pos)
                text_widget.see(pos)
                text_widget.tag_add(tk.SEL, pos, end_pos)
            else:
                # 從頭開始搜尋
                pos = text_widget.search(search_text, '1.0', tk.END, nocase=True)
                if pos:
                    end_pos = f"{pos}+{len(search_text)}c"
                    text_widget.mark_set(tk.INSERT, end_pos)
                    text_widget.see(pos)
                    text_widget.tag_add(tk.SEL, pos, end_pos)
                    
        except Exception as e:
            print(f"搜尋下一個時發生錯誤: {e}")
            traceback.print_exc()
    
    def _search_prev_in_text(self, text_widget, search_text):
        """在Text元件中搜尋上一個"""
        try:
            # 檢查Text元件是否有內容
            content = text_widget.get('1.0', tk.END)
            
            if len(content) <= 1:  # 只有換行符
                self._update_search_count(0)
                return
            
            # 先清除之前的選取
            text_widget.tag_remove(tk.SEL, '1.0', tk.END)
            text_widget.tag_remove('search_highlight', '1.0', tk.END)
            
            # 設定搜尋高亮樣式
            text_widget.tag_configure('search_highlight', background='#FFFF00', foreground='#000000')
            
            # 計算總匹配數量
            count = 0
            pos = '1.0'
            while True:
                pos = text_widget.search(search_text, pos, tk.END, nocase=True)
                if not pos:
                    break
                count += 1
                end_pos = f"{pos}+{len(search_text)}c"
                text_widget.tag_add('search_highlight', pos, end_pos)
                pos = end_pos
            
            # 更新搜尋計數
            self._update_search_count(count)
            
            # 從當前游標位置向前搜尋
            current_pos = text_widget.index(tk.INSERT)
            
            # 從當前位置向前搜尋（不包含當前位置）
            if current_pos != '1.0':
                prev_pos = text_widget.index(f"{current_pos}-1c")
                pos = text_widget.search(search_text, '1.0', prev_pos, nocase=True, backwards=True)
            else:
                # 如果已經在開頭，從末尾開始搜尋
                pos = text_widget.search(search_text, tk.END, '1.0', nocase=True, backwards=True)
            
            if pos:
                # 找到匹配項目
                end_pos = f"{pos}+{len(search_text)}c"
                text_widget.mark_set(tk.INSERT, pos)
                text_widget.see(pos)
                text_widget.tag_add(tk.SEL, pos, end_pos)
            else:
                #如果只找到一個，或者沒有找到
                pass
                    
        except Exception as e:
            print(f"搜尋上一個時發生錯誤: {e}")
            traceback.print_exc()
    
    def _perform_search(self):
        """執行搜尋功能"""
        try:
            search_text = self.search_var.get().strip()
            
            if not search_text:
                self._clear_search()
                return
            
            # 使用 lowercase 版本進行後續 Treeview 匹配 (保持原有邏輯)
            search_text_lower = search_text.lower()
            
            # 檢查當前選中的標籤頁
            current_tab = self.notebook.select()
            
            # 根據當前標籤頁決定搜尋範圍
            # 獲取當前選中的標籤頁索引
            current_tab_index = self.notebook.index(current_tab)
            
            # 根據索引判斷標籤頁類型
            if current_tab_index == 0:  # PASS標籤頁
                if hasattr(self, 'pass_tree_enhanced'):
                    self._search_in_tree(self.pass_tree_enhanced, search_text)
                else:
                    print("未找到PASS tree")
            elif current_tab_index == 1:  # FAIL標籤頁
                if hasattr(self, 'fail_tree_enhanced'):
                    self._search_in_tree(self.fail_tree_enhanced, search_text)
                else:
                    print("未找到FAIL tree")
            elif current_tab_index == 2:  # 原始LOG標籤頁
                if hasattr(self, 'log_text_enhanced') and hasattr(self.log_text_enhanced, 'text'):
                    self._search_in_text(self.log_text_enhanced.text, search_text)
                elif hasattr(self, 'raw_text'):
                    self._search_in_text(self.raw_text, search_text)
            else:
                if hasattr(self, 'log_text_enhanced') and hasattr(self.log_text_enhanced, 'text'):
                    self._search_in_text(self.log_text_enhanced.text, search_text)
                elif hasattr(self, 'raw_text'):
                    self._search_in_text(self.raw_text, search_text)
                
        except Exception as e:
            print(f"搜尋時發生錯誤: {e}")
            traceback.print_exc()
    
    def _search_in_tree(self, tree_enhanced, search_text):
        """在TreeView中搜尋"""
        try:
            tree = tree_enhanced.tree
            # 清除之前的選取
            tree.selection_remove(tree.selection())
            
            # 搜尋匹配的項目
            matches = []
            for item in tree.get_children():
                values = tree.item(item, 'values')
                # 檢查所有欄位是否包含搜尋文字
                for value in values:
                    if search_text in str(value).lower():
                        matches.append(item)
                        break
            
            # 更新搜尋計數
            self._update_search_count(len(matches))
            
            if matches:
                # 選取第一個匹配項目並滾動到該位置
                tree.selection_set(matches[0])
                tree.focus(matches[0])
                tree.see(matches[0])
                
                # 高亮顯示所有匹配項目
                for match in matches:
                    tree.selection_add(match)
                
        except Exception as e:
            print(f"TreeView搜尋時發生錯誤: {e}")
    
    def _search_in_text(self, text_widget, search_text):
        """在Text元件中搜尋 - 使用內建搜尋功能"""
        try:
            # 檢查Text元件是否有內容
            content = text_widget.get('1.0', tk.END)
            
            if len(content) <= 1:  # 只有換行符
                self._update_search_count(0)
                return
            
            # 先清除之前的搜尋
            text_widget.tag_remove(tk.SEL, '1.0', tk.END)
            text_widget.tag_remove('search_highlight', '1.0', tk.END)
            
            # 設定搜尋高亮樣式
            text_widget.tag_configure('search_highlight', background='#FFFF00', foreground='#000000')
            
            # 計算總匹配數量
            count = 0
            pos = '1.0'
            while True:
                pos = text_widget.search(search_text, pos, tk.END, nocase=True)
                if not pos:
                    break
                count += 1
                end_pos = f"{pos}+{len(search_text)}c"
                text_widget.tag_add('search_highlight', pos, end_pos)
                pos = end_pos
            
            # 更新搜尋計數
            self._update_search_count(count)
            
            if count > 0:
                # 找到第一個匹配項目並滾動到該位置
                first_pos = text_widget.search(search_text, '1.0', tk.END, nocase=True)
                if first_pos:
                    end_pos = f"{first_pos}+{len(search_text)}c"
                    text_widget.mark_set(tk.INSERT, end_pos)
                    text_widget.see(first_pos)
                    text_widget.tag_add(tk.SEL, first_pos, end_pos)
                
        except Exception as e:
            print(f"Text搜尋時發生錯誤: {e}")
            traceback.print_exc()

    def _clear_search(self):
        """清除搜尋結果"""
        try:
            # 清除搜尋框
            if hasattr(self, 'search_var'):
                self.search_var.set("")
            
            # 清除PASS樹狀檢視的選取
            if hasattr(self, 'pass_tree_enhanced'):
                self.pass_tree_enhanced.tree.selection_remove(self.pass_tree_enhanced.tree.selection())
            
            # 清除FAIL樹狀檢視的選取
            if hasattr(self, 'fail_tree_enhanced'):
                self.fail_tree_enhanced.tree.selection_remove(self.fail_tree_enhanced.tree.selection())
            
            # 清除原始LOG的選取和高亮
            if hasattr(self, 'log_text_enhanced') and hasattr(self.log_text_enhanced, 'text'):
                self.log_text_enhanced.text.tag_remove(tk.SEL, '1.0', tk.END)
                self.log_text_enhanced.text.tag_remove('search_highlight', '1.0', tk.END)
                # 重置游標到開頭
                self.log_text_enhanced.text.mark_set(tk.INSERT, '1.0')
            elif hasattr(self, 'raw_text'):
                self.raw_text.tag_remove(tk.SEL, '1.0', tk.END)
                self.raw_text.tag_remove('search_highlight', '1.0', tk.END)
                # 重置游標到開頭
                self.raw_text.mark_set(tk.INSERT, '1.0')
            
            # 清除搜尋計數
            if hasattr(self, 'search_count_label'):
                self.search_count_label.config(text="")
            
            print("已清除搜尋結果")
            
        except Exception as e:
            print(f"清除搜尋時發生錯誤: {e}")
    
    def _update_search_count(self, count):
        """更新搜尋結果計數"""
        try:
            if hasattr(self, 'search_count_label'):
                if count > 0:
                    self.search_count_label.config(text=f"搜尋結果：共 {count} 筆", foreground='#2196F3')
                else:
                    self.search_count_label.config(text="搜尋結果：未找到匹配項目", foreground='#F44336')
        except Exception as e:
            print(f"更新搜尋計數時發生錯誤: {e}")

    def _search_fail_keywords(self):
        """自動搜尋所有設定的 FAIL 關鍵字"""
        try:
            if not hasattr(self, 'log_parser') or not self.log_parser.fail_keywords:
                # 嘗試從 config 讀取
                fail_kw_str = self.config_manager.get('user_fail_keywords', 'FAIL, ERROR')
                keywords = [k.strip() for k in fail_kw_str.split(',') if k.strip()]
            else:
                keywords = self.log_parser.fail_keywords
                
            if not keywords:
                return
            
            # 組合正則表達式，例如 (FAIL|ERROR|spec_issue)
            import re
            pattern = "|".join([re.escape(k) for k in keywords])
            
            # 將搜尋文字框內容設為關鍵字清單，方便使用者知道搜了什麼
            last_kw = keywords[-1] if keywords else ""
            self.search_var.set(last_kw) 
            
            # 遍歷 Text 元件執行正則搜尋
            target_text = None
            if hasattr(self, 'log_text_enhanced') and hasattr(self.log_text_enhanced, 'text'):
                target_text = self.log_text_enhanced.text
            elif hasattr(self, 'raw_text'):
                target_text = self.raw_text
            
            if target_text:
                # 先清除之前的高亮
                target_text.tag_remove(tk.SEL, '1.0', tk.END)
                target_text.tag_remove('search_highlight', '1.0', tk.END)
                
                # 正則搜尋並高亮所有
                count = 0
                pos = '1.0'
                while True:
                    pos = target_text.search(pattern, pos, tk.END, nocase=True, regexp=True)
                    if not pos:
                        break
                    count += 1
                    # 這裡比較難獲取具體匹配到的那個關鍵字長度，
                    # 但因為我們用了 re.escape，可以大致預估，或者再次搜尋具體匹配項
                    # 簡化處理：我們重新在該位置匹配一次 re 以獲得長度
                    match_obj = re.search(pattern, target_text.get(pos, f"{pos} lineend"), re.IGNORECASE)
                    match_len = len(match_obj.group(0)) if match_obj else 1
                    
                    end_pos = f"{pos}+{match_len}c"
                    target_text.tag_add('search_highlight', pos, end_pos)
                    
                    # 如果是第一個，就跳轉過去
                    if count == 1:
                        target_text.see(pos)
                        target_text.mark_set(tk.INSERT, pos)
                        target_text.tag_add(tk.SEL, pos, end_pos)
                        
                    pos = end_pos
                
                self._update_search_count(count)
            else:
                # 如果不在 Text 標籤，則執行普通搜尋
                self._perform_search()
                
        except Exception as e:
            print(f"搜關鍵字按鈕錯誤: {e}")
            traceback.print_exc()

    def _add_to_search_history(self, keyword):
        """將關鍵字加入歷史記錄 (最多 5 筆，MRU 順序)"""
        try:
            if not keyword: return
            
            # 獲取目前歷史記錄
            history = self.settings.get('search_history', ["doesn't match"])
            
            # 如果已經在裡面，先移除 (為了移到最上面)
            if keyword in history:
                history.remove(keyword)
            
            # 加到最前面
            history.insert(0, keyword)
            
            # 只保留前 5 筆
            self.settings['search_history'] = history[:5]
            
            # 更新 Combobox 值
            if hasattr(self, 'search_combo'):
                self.search_combo['values'] = self.settings['search_history']
            
            # 保存設定
            from .settings_loader import save_settings
            save_settings(self.settings)
            
        except Exception as e:
            print(f"更新搜尋歷史失敗: {e}")
