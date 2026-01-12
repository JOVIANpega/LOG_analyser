import json
import os

def get_version():
    try:
        settings_path = os.path.join(os.path.dirname(__file__), '..', 'settings.json')
        if os.path.exists(settings_path):
            with open(settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('version', 'V2.15.0')
    except:
        pass
    return "V2.15.0"

VERSION = get_version()
