import json
import os

def get_version():
    try:
        # 優先尋找與執行檔同層的 settings.json (適用於打包後的 root 目錄)
        if getattr(sys, 'frozen', False):
            # 打包模式：EXE 所在的目錄
            exe_dir = os.path.dirname(sys.executable)
            settings_path = os.path.join(exe_dir, 'settings.json')
            
            # 如果 root 沒找到，再試試內嵌的 _internal 目錄
            if not os.path.exists(settings_path):
                base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
                settings_path = os.path.join(base_path, 'settings.json')
        else:
            # 開發模式：專案根目錄
            settings_path = os.path.join(os.path.dirname(__file__), '..', 'settings.json')
            
        if os.path.exists(settings_path):
            with open(settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('version', 'V2.5.1')
    except:
        pass
    return "V2.5.1"

VERSION = get_version()
