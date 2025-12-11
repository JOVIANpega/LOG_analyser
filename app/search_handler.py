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
    
    def _on_search_enter(self, event):
        """按下Enter鍵時執行搜尋"""
        try:
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
            search_text = self.search_var.get().strip().lower()
            
            if not search_text:
                self._clear_search()
                return
            
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
                    self.search_count_label.config(text=f"找到 {count} 個匹配項目", fg='#2196F3')
                else:
                    self.search_count_label.config(text="未找到匹配項目", fg='#F44336')
        except Exception as e:
            print(f"更新搜尋計數時發生錯誤: {e}")
