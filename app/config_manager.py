# -*- coding: utf-8 -*-
"""
Config Manager Module
Handles application configuration, settings, and encryption checks
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox
from .settings_loader import load_settings, save_settings

class ConfigManager:
    """Configuration Manager for Log Analyzer App"""
    
    def __init__(self, root):
        self.root = root
        self.settings = load_settings()
        
    def check_encryption(self):
        """檢查加密檔案"""
        try:
            # 獲取EXE所在目錄
            if getattr(sys, 'frozen', False):
                # 如果是打包的EXE
                exe_dir = os.path.dirname(sys.executable)
            else:
                # 如果是Python腳本
                exe_dir = os.path.dirname(os.path.abspath(__file__))
                # 處理在app目錄下運行的情況，向上找一層
                if os.path.basename(exe_dir) == 'app':
                    exe_dir = os.path.dirname(exe_dir)
            
            # 檢查SIGN.txt檔案
            sign_file = os.path.join(exe_dir, "SIGN.txt")
            
            if not os.path.exists(sign_file):
                self._show_encryption_error()
                return False
            
            # 讀取檔案內容
            with open(sign_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # 檢查是否包含jovian字串
            if 'jovian' not in content.lower():
                self._show_encryption_error()
                return False
            
            print("加密檔案驗證成功")
            return True
            
        except Exception as e:
            print(f"檢查加密檔案時發生錯誤: {e}")
            self._show_encryption_error()
            return False
    
    def _show_encryption_error(self):
        """顯示加密錯誤訊息"""
        messagebox.showerror("加密驗證失敗", "請提供運作工具的加密檔案")
        self.root.destroy()
        sys.exit(1)
        
    def load_window_geometry(self):
        """載入並套用視窗幾何設定"""
        window_width = self.settings.get('window_width', 1400)
        window_height = self.settings.get('window_height', 900)
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.state('zoomed')  # Windows 最大化
        
    def save_window_geometry(self):
        """保存視窗幾何設定"""
        try:
            # 保存視窗大小
            if self.root.state() != 'zoomed':
                self.settings['window_width'] = self.root.winfo_width()
                self.settings['window_height'] = self.root.winfo_height()
            
            save_settings(self.settings)
        except Exception as e:
            print(f"保存視窗設定失敗: {e}")
            
    def get(self, key, default=None):
        """獲取設定值"""
        return self.settings.get(key, default)
        
    def set(self, key, value):
        """設定值並保存"""
        self.settings[key] = value
        save_settings(self.settings)
        
    def save(self):
        """手動觸發保存"""
        save_settings(self.settings)
