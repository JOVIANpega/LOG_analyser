# settings_loader.py
# 用途：管理GUI工具的本地設定（如字體大小、路徑記憶、視窗大小），支援讀取與寫入settings.json
import json
import os

SETTINGS_FILE = 'settings.json'
DEFAULT_SETTINGS = {
    'ui_font_size': 11,      # 介面文字大小（按鍵、標籤頁名稱等）
    'content_font_size': 11,  # 內容字體大小（標籤頁內容、預覽文字等）
    'last_log_path': '',      # 上次選擇的log路徑
    'last_folder_path': '',   # 上次選擇的資料夾路徑
    'window_width': 1400,     # 主視窗寬度
    'window_height': 900,     # 主視窗高度
    'pane_width': 250,        # 左側面板寬度
    'app_title': 'PEGA test log Aanlyser',  # 應用程式標題（可在設定頁修改並保存）
    'gui_header': 'ONLY FOR CENTIMANIA LOG' # 左側GUI大標題（可在設定頁修改並保存）
}

def load_settings():
    """讀取本地設定檔，若不存在則回傳預設值"""
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        return {**DEFAULT_SETTINGS, **settings}
    except Exception:
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """儲存設定到本地檔案"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f'設定儲存失敗: {e}') 