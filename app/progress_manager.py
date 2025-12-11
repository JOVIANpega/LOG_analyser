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
        self._progress_label = None
        self._progress_bar = None
        self._time_label = None
        self._start_time = None
        self._cancel_flag = False
        
    @property
    def is_cancelled(self):
        return self._cancel_flag
        
    def show_progress(self, title: str, message: str = ""):
        """顯示進度視窗"""
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
            lbl = tk.Label(frame, text=message or title, anchor='w', justify='left', font=('Arial', 10))
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
            self._start_time = None
            self._cancel_flag = False
            
        except Exception as e:
            print(f"顯示進度窗失敗: {e}")

    def update_progress(self, text: str):
        """更新進度文字"""
        try:
            if self._progress_win and self._progress_win.winfo_exists():
                self._progress_label.config(text=text)
                self._progress_win.update_idletasks()
        except Exception:
            pass

    def close_progress(self):
        """關閉進度視窗"""
        try:
            if self._progress_win and self._progress_win.winfo_exists():
                self._progress_win.destroy()
        except Exception:
            pass
        self._progress_win = None
        self._cancel_flag = False

    def set_determinate(self, maximum: int):
        """將進度條切換為可顯示百分比的 determinate 模式"""
        try:
            if not (self._progress_win and self._progress_win.winfo_exists()):
                return
            try:
                self._progress_bar.stop()
            except Exception:
                pass
            self._progress_bar.configure(mode='determinate', maximum=max(1, int(maximum)))
            self._progress_bar['value'] = 0
            self._start_time = time.time()  # 記錄開始時間
        except Exception as e:
            print(f"設定 determinate 進度失敗: {e}")

    def set_value(self, current: int, total: int):
        """更新進度值和預估時間"""
        try:
            if not (self._progress_win and self._progress_win.winfo_exists()):
                return
            
            total = max(1, int(total))
            current = min(max(0, int(current)), total)
            self._progress_bar['value'] = current
            
            percent = int(current * 100 / total)
            self._progress_label.config(text=f"正在分析... {percent}%")
            
            # 計算剩餘時間
            if self._start_time and current > 0:
                elapsed_time = time.time() - self._start_time
                if current < total:
                    avg_time_per_item = elapsed_time / current
                    remaining_items = total - current
                    estimated_remaining = avg_time_per_item * remaining_items
                    
                    if estimated_remaining < 60:
                        time_text = f"預估剩餘時間: {int(estimated_remaining)} 秒"
                    else:
                        minutes = int(estimated_remaining // 60)
                        seconds = int(estimated_remaining % 60)
                        time_text = f"預估剩餘時間: {minutes} 分 {seconds} 秒"
                else:
                    time_text = "即將完成..."
                
                if self._time_label:
                    self._time_label.config(text=time_text)
            
            self._progress_win.update_idletasks()
        except Exception:
            pass

    def set_indeterminate(self, text: str = ""):
        """切換回 indeterminate 模式"""
        try:
            if not (self._progress_win and self._progress_win.winfo_exists()):
                return
            self._progress_bar.configure(mode='indeterminate')
            self._progress_bar.start(12)
            if text:
                self.update_progress(text)
        except Exception:
            pass
