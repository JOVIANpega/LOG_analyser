# -*- coding: utf-8 -*-
import os

def generate_version_info(version):
    import re
    # 提取所有數字部分，忽略 V 或其他非數字字元
    v_parts = re.findall(r'\d+', version)
    v_tuple = tuple(v_parts)
    # Ensure 4 parts
    while len(v_tuple) < 4:
        v_tuple += ('0',)
    
    v_comma = ', '.join(v_tuple)
    v_str = '.'.join(v_tuple)
    
    content = f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({v_comma}),
    prodvers=({v_comma}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable('040904B0', [
        StringStruct('CompanyName', 'PEGA'),
        StringStruct('FileDescription', 'PEGA Log Analyzer'),
        StringStruct('FileVersion', '{v_str}'),
        StringStruct('InternalName', 'PEGA_Log_Analyzer'),
        StringStruct('LegalCopyright', 'Copyright (c) 2025 PEGA'),
        StringStruct('OriginalFilename', 'PEGA_Log_Analyzer.exe'),
        StringStruct('ProductName', 'PEGA Log Analyzer'),
        StringStruct('ProductVersion', '{v_str}')
      ])
    ]),
    VarFileInfo([
      VarStruct('Translation', [1033, 1200])
    ])
  ]
)"""
    
    os.makedirs('assets', exist_ok=True)
    with open('assets/version_info.txt', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    import sys
    ver = sys.argv[1] if len(sys.argv) > 1 else "1.9.1"
    generate_version_info(ver)
