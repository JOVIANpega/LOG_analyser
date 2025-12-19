# ui_components.py
# 用途：提供GUI元件輔助函式，支援字體大小調整、分割視窗、Tab等
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
import os
import sys

class FontScaler:
    def __init__(self, root, min_size=10, max_size=15, default_size=11):
        self.root = root
        self.min_size = min_size
        self.max_size = max_size
        self.font_size = default_size
        self.widgets = []
        self.widget_styles = {}

    def _capture_widget_style(self, widget):
        try:
            current_font = widget.cget('font')
            if not current_font:
                return {'family': None, 'weight': 'normal', 'slant': 'roman'}
            f = tkfont.Font(font=current_font)
            return {
                'family': f.actual('family'),
                'weight': f.actual('weight'),
                'slant': f.actual('slant')
            }
        except Exception:
            return {'family': None, 'weight': 'normal', 'slant': 'roman'}

    def register(self, widget):
        self.widgets.append(widget)
        # 註冊當下樣式，供之後縮放時保留粗體/斜體等
        try:
            self.widget_styles[widget] = self._capture_widget_style(widget)
        except Exception:
            self.widget_styles[widget] = {'family': None, 'weight': 'normal', 'slant': 'roman'}

    def set_font_size(self, size):
        self.font_size = max(self.min_size, min(self.max_size, size))
        
        # 1. 更新所有註冊的傳統 tk 元件
        for w in self.widgets:
            try:
                style = self.widget_styles.get(w)
                if not style:
                    style = self._capture_widget_style(w)
                    self.widget_styles[w] = style
                family = style.get('family') or 'Arial'
                weight = style.get('weight') or 'normal'
                w.configure(font=(family, self.font_size, weight))
            except Exception:
                try:
                    w.configure(font=('Arial', self.font_size))
                except Exception:
                    pass
        
        # 2. 更新 ttk 全域樣式，確保所有 ttk 元件同步縮放
        try:
            style = ttk.Style()
            style.configure('.', font=('Arial', self.font_size))
            style.configure('TNotebook.Tab', font=('Arial', self.font_size))
            style.configure('TButton', font=('Arial', self.font_size))
            style.configure('TLabel', font=('Arial', self.font_size))
            style.configure('TEntry', font=('Arial', self.font_size))
            style.configure('TLabelframe.Label', font=('Arial', self.font_size, 'bold'))
        except Exception as e:
            print(f"更新 ttk 樣式失敗: {e}")

    def apply_to_treeview(self, tree):
        style = ttk.Style()
        style.configure("Treeview", font=('Arial', self.font_size))
        style.configure("Treeview.Heading", font=('Arial', self.font_size, 'bold'))

# 共同UI工具：設定元件字體為粗體並與FontScaler相容
def make_bold(widget):
    try:
        f = tkfont.Font(font=widget.cget('font')) if widget.cget('font') else tkfont.Font()
        f.configure(weight='bold')
        widget.configure(font=f)
    except Exception:
        try:
            widget.configure(font=(None, 11, 'bold'))
        except Exception:
            pass

# 共同UI工具：替 tk.Button 加入滑鼠懸停變色效果
# 若未指定 normal_bg/fg，會使用元件現有的顏色
def apply_button_hover(widget, hover_bg, hover_fg=None, normal_bg=None, normal_fg=None):
    try:
        base_bg = normal_bg if normal_bg is not None else widget.cget('bg')
        base_fg = normal_fg if normal_fg is not None else widget.cget('fg')

        def on_enter(_):
            try:
                widget.configure(bg=hover_bg)
                if hover_fg is not None:
                    widget.configure(fg=hover_fg)
            except Exception:
                pass

        def on_leave(_):
            try:
                widget.configure(bg=base_bg)
                widget.configure(fg=base_fg)
            except Exception:
                pass

        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    except Exception:
        pass

# 路徑輔助：支援 PyInstaller 打包後資源存取
def get_resource_path(relative_path: str) -> str:
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.abspath('.'))
        return os.path.join(base_path, relative_path)
    except Exception:
        return relative_path

# 路徑與輸出輔助：集中資料夾判斷與建立
def ensure_dir(path: str) -> str:
    """確保資料夾存在，若不存在則建立；回傳路徑本身"""
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        pass
    return path

def build_output_dir(base_dir: str, subfolder_name: str) -> str:
    """在指定基底資料夾下建立輸出子資料夾並回傳其路徑"""
    try:
        out_dir = os.path.join(base_dir, subfolder_name)
        ensure_dir(out_dir)
        return out_dir
    except Exception:
        return base_dir 