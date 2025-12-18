# -*- coding: utf-8 -*-
"""
Progress Manager Module
Handles progress window display and updates in a thread-safe manner
"""

import time
import tkinter as tk
from tkinter import ttk

class ProgressManager:
    """Progress Manager for Log Analyzer App"""
    
    def __init__(self, root):
        self.root = root
        self._progress_win = None
        self._progress_label = None # Popup label
        self._progress_bar = None   # Popup bar
        self._time_label = None
        
        # Embedded widgets
        self._status_label = None
        self._main_progress_bar = None
        self._status_light = None
        self._header_label = None # Left sidebar title label
        self._is_flashing = False
        
        self._start_time = None
        self._cancel_flag = False
        
    def set_widgets(self, status_label, progress_bar, status_light=None, header_label=None):
        """設定主視窗的狀態列與標題元件"""
        self._status_label = status_label
        self._main_progress_bar = progress_bar
        self._status_light = status_light
        self._header_label = header_label

    def _flash_loop(self):
        """閃爍迴圈"""
        if not self._is_flashing:
            return
            
        # 1. 狀態燈閃爍 (Green <-> DarkGreen)
        if self._status_light:
            try:
                curr = self._status_light.cget('fg')
                self._status_light.config(fg='#00FF00' if curr != '#00FF00' else '#006400')
            except: pass

        # 2. 標題標籤閃爍 (Green <-> Orange/Blue or simple Fade)
        # 使用者提到 GUI左上的 centermani LOG 閃爍
        if self._header_label:
            try:
                curr_bg = self._header_label.cget('bg')
                # 在原本的綠色 (#4CAF50) 與較亮的綠色 (#81C784) 之間切換
                next_bg = '#81C784' if curr_bg == '#4CAF50' else '#4CAF50'
                self._header_label.config(bg=next_bg)
                # 同步更新 parent frame bg 如果有的話，但通常 label 閃爍就夠了
            except: pass

        try:
            self.root.after(500, self._flash_loop)
        except Exception:
            self._is_flashing = False
            
    def _start_flashing(self):
        """開始閃爍"""
        if self._status_light and not self._is_flashing:
            self._is_flashing = True
            self._flash_loop()
            
    def _stop_flashing(self):
        """停止閃爍"""
        self._is_flashing = False
        if self._status_light:
            try:
                self._status_light.config(fg='gray')
            except: pass
        if self._header_label:
            try:
                self._header_label.config(bg='#4CAF50') # 恢復原始綠色
            except: pass

    @property
    def is_cancelled(self):
        return self._cancel_flag
        
    def show_progress(self, title: str, message: str = ""):
        """顯示進度 (優先使用狀態列)"""
        text = message or title
        self._cancel_flag = False
        self._start_time = time.time()
        
        self._start_flashing() # Start blinking logic
        
        # 如果有嵌入式元件，更新它們
        if self._status_label and self._main_progress_bar:
            self._status_label.config(text=text)
            self._main_progress_bar['value'] = 0
            self._main_progress_bar.configure(mode='indeterminate')
            self._main_progress_bar.start(10)
            self.root.update_idletasks()
            return

        # 否則使用彈窗 (舊有邏輯，保留作為備案)
        try:
            if self._progress_win and self._progress_win.winfo_exists():
                return
            
            win = tk.Toplevel(self.root)
            win.title(title)
            win.geometry("450x160")
            win.transient(self.root)
            win.grab_set()
            
            # 居中顯示
            win.update_idletasks()
            x = (win.winfo_screenwidth() // 2) - (450 // 2)
            y = (win.winfo_screenheight() // 2) - (160 // 2)
            win.geometry(f"450x160+{x}+{y}")
            
            frame = tk.Frame(win)
            frame.pack(fill=tk.BOTH, expand=1, padx=12, pady=12)
            
            # 主標籤
            lbl = tk.Label(frame, text=text, anchor='w', justify='left', font=('Arial', 10))
            lbl.pack(fill=tk.X)
            
            # 進度條
            bar = ttk.Progressbar(frame, mode='indeterminate')
            bar.pack(fill=tk.X, pady=10)
            bar.start(12)
            
            # 時間估算標籤
            time_label = tk.Label(frame, text="預估剩餘時間: 計算中...", font=('Arial', 9), fg='gray')
            time_label.pack(anchor='w')
            
            def on_cancel():
                self._cancel_flag = True
                lbl.config(text="正在取消，請稍候…")
            
            btn = tk.Button(frame, text="取消", command=on_cancel)
            btn.pack(pady=(4,0))
            
            # 綁定視窗關閉事件
            win.protocol("WM_DELETE_WINDOW", on_cancel)
            
            self._progress_win = win
            self._progress_label = lbl
            self._progress_bar = bar
            self._time_label = time_label
            
        except Exception as e:
            print(f"顯示進度窗失敗: {e}")

    def update_progress(self, text: str):
        """更新進度文字"""
        try:
            # 更新嵌入式狀態列
            if self._status_label:
                self._status_label.config(text=text)
                self.root.update_idletasks()
            
            # 更新彈窗
            if self._progress_win and self._progress_win.winfo_exists():
                self._progress_label.config(text=text)
                self._progress_win.update_idletasks()
        except Exception:
            pass

    def close_progress(self):
        """關閉進度顯示 (重置狀態列或關閉彈窗)"""
        self._stop_flashing() # Stop blinking
        try:
            # 重置嵌入式狀態列
            if self._status_label:
                self._status_label.config(text="就緒")
            if self._main_progress_bar:
                self._main_progress_bar.stop()
                self._main_progress_bar['value'] = 0
            
            # 關閉彈窗
            if self._progress_win and self._progress_win.winfo_exists():
                try:
                    self._progress_win.grab_release()  # 釋放輸入鎖定
                except:
                    pass
                self._progress_win.destroy()
        except Exception:
            pass
        self._progress_win = None
        self._cancel_flag = False

    def set_determinate(self, maximum: int):
        """將進度條切換為可顯示百分比的 determinate 模式"""
        try:
            self._start_time = time.time()  # 記錄開始時間
            maximum = max(1, int(maximum))
            
            # 嵌入式
            if self._main_progress_bar:
                self._main_progress_bar.stop()
                self._main_progress_bar.configure(mode='determinate', maximum=maximum)
                self._main_progress_bar['value'] = 0
            
            # 彈窗
            if self._progress_win and self._progress_win.winfo_exists():
                self._progress_bar.stop()
                self._progress_bar.configure(mode='determinate', maximum=maximum)
                self._progress_bar['value'] = 0
                
        except Exception as e:
            print(f"設定 determinate 進度失敗: {e}")

    def set_value(self, current: int, total: int):
        """更新進度值和預估時間"""
        try:
            total = max(1, int(total))
            current = min(max(0, int(current)), total)
            percent = int(current * 100 / total)
            
            progress_text = f"正在分析... {percent}% ({current}/{total})"
            
            # 計算剩餘時間
            time_text = ""
            if self._start_time and current > 0:
                elapsed_time = time.time() - self._start_time
                if current < total:
                    avg_time_per_item = elapsed_time / current
                    remaining_items = total - current
                    estimated_remaining = avg_time_per_item * remaining_items
                    
                    if estimated_remaining < 60:
                        time_text = f"預估剩餘: {int(estimated_remaining)} 秒"
                    else:
                        minutes = int(estimated_remaining // 60)
                        seconds = int(estimated_remaining % 60)
                        time_text = f"預估剩餘: {minutes} 分 {seconds} 秒"
                else:
                    time_text = "即將完成..."
            
            full_text = f"{progress_text} - {time_text}" if time_text else progress_text

            # 更新嵌入式
            if self._status_label and self._main_progress_bar:
                self._main_progress_bar['value'] = current
                self._status_label.config(text=full_text)
                self.root.update_idletasks()
            
            # 更新彈窗
            if self._progress_win and self._progress_win.winfo_exists():
                self._progress_bar['value'] = current
                self._progress_label.config(text=progress_text)
                if self._time_label:
                    self._time_label.config(text=time_text)
                self._progress_win.update_idletasks()
                
        except Exception:
            pass

    def set_indeterminate(self, text: str = ""):
        """切換回 indeterminate 模式"""
        try:
            # 嵌入式
            if self._status_label and self._main_progress_bar:
                self._main_progress_bar.configure(mode='indeterminate')
                self._main_progress_bar.start(10)
                if text:
                    self._status_label.config(text=text)
            
            # 彈窗
            if self._progress_win and self._progress_win.winfo_exists():
                self._progress_bar.configure(mode='indeterminate')
                self._progress_bar.start(12)
                if text:
                    self._progress_label.config(text=text)
                    
        except Exception:
            pass

    # Thread-safe wrapper methods for background threads
    def _safe_update_progress_text(self, text: str):
        """线程安全：更新进度文字"""
        try:
            self.root.after(0, lambda: self.update_progress(text))
        except Exception:
            pass
    
    def _safe_update_progress_mode(self, mode: str):
        """线程安全：切换进度条模式"""
        try:
            if mode == 'determinate':
                self.root.after(0, lambda: self.set_determinate(100))
            elif mode == 'indeterminate':
                self.root.after(0, lambda: self.set_indeterminate())
        except Exception:
            pass
    
    def _safe_update_progress_max(self, maximum: int):
        """线程安全：设置进度条最大值"""
        try:
            self.root.after(0, lambda: self.set_determinate(maximum))
        except Exception:
            pass
    
    def _safe_update_progress(self, current: int, total: int, text: str = ""):
        """线程安全：更新进度值"""
        try:
            self.root.after(0, lambda: self.set_value(current, total))
            if text:
                self.root.after(0, lambda: self.update_progress(text))
        except Exception:
            pass
