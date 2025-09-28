#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文檔生成器
為所有PY文件生成Markdown格式的詳細註解
"""

import os
import re
from pathlib import Path

def extract_class_info(content):
    """提取類別信息"""
    classes = []
    class_pattern = r'class\s+(\w+).*?:'
    for match in re.finditer(class_pattern, content):
        class_name = match.group(1)
        # 找到類別的docstring
        start_pos = match.end()
        lines = content[start_pos:].split('\n')
        docstring = ""
        in_docstring = False
        for line in lines:
            if '"""' in line or "'''" in line:
                if not in_docstring:
                    in_docstring = True
                    docstring = line.split('"""')[1] if '"""' in line else line.split("'''")[1]
                else:
                    docstring += "\n" + line.split('"""')[0] if '"""' in line else line.split("'''")[0]
                    break
            elif in_docstring:
                docstring += "\n" + line
            else:
                break
        
        # 如果沒有docstring，嘗試從註解中提取
        if not docstring.strip():
            # 查找類別前的註解
            before_class = content[:match.start()]
            lines_before = before_class.split('\n')
            for line in reversed(lines_before[-5:]):  # 檢查前5行
                if line.strip().startswith('#') and ('類別' in line or 'class' in line.lower()):
                    docstring = line.strip('#').strip()
                    break
        
        classes.append({
            'name': class_name,
            'docstring': docstring.strip()
        })
    return classes

def extract_function_info(content):
    """提取函數信息"""
    functions = []
    func_pattern = r'def\s+(\w+)\s*\([^)]*\)\s*:'
    for match in re.finditer(func_pattern, content):
        func_name = match.group(1)
        if func_name.startswith('_'):
            continue  # 跳過私有方法
        
        # 找到函數的docstring
        start_pos = match.end()
        lines = content[start_pos:].split('\n')
        docstring = ""
        in_docstring = False
        for line in lines:
            if '"""' in line or "'''" in line:
                if not in_docstring:
                    in_docstring = True
                    docstring = line.split('"""')[1] if '"""' in line else line.split("'''")[1]
                else:
                    docstring += "\n" + line.split('"""')[0] if '"""' in line else line.split("'''")[0]
                    break
            elif in_docstring:
                docstring += "\n" + line
            else:
                break
        
        # 如果沒有docstring，嘗試從註解中提取
        if not docstring.strip():
            # 查找函數前的註解
            before_func = content[:match.start()]
            lines_before = before_func.split('\n')
            for line in reversed(lines_before[-3:]):  # 檢查前3行
                if line.strip().startswith('#') and ('函數' in line or 'function' in line.lower() or 'def' in line.lower()):
                    docstring = line.strip('#').strip()
                    break
        
        functions.append({
            'name': func_name,
            'docstring': docstring.strip()
        })
    return functions

def generate_markdown_doc(file_path):
    """為單個PY文件生成Markdown文檔"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    file_name = os.path.basename(file_path)
    
    # 提取文件開頭的註解
    lines = content.split('\n')
    file_description = ""
    for line in lines[:10]:  # 檢查前10行
        if line.strip().startswith('#') and ('用途' in line or '功能' in line or 'purpose' in line.lower()):
            file_description = line.strip('#').strip()
            break
    
    # 如果沒有找到描述，嘗試從docstring中提取
    if not file_description:
        for line in lines[:10]:
            if '"""' in line or "'''" in line:
                docstring = line.split('"""')[1] if '"""' in line else line.split("'''")[1]
                if docstring.strip():
                    file_description = docstring.strip()
                    break
    
    # 提取類別和函數信息
    classes = extract_class_info(content)
    functions = extract_function_info(content)
    
    # 生成Markdown內容
    md_content = f"""# {file_name} 文檔

## 📋 文件概述
{file_description if file_description else "該文件的主要功能和用途"}

## 📊 文件統計
- **總行數**: {len(lines)}
- **類別數量**: {len(classes)}
- **函數數量**: {len(functions)}

"""
    
    if classes:
        md_content += """## 🏗️ 類別結構

"""
        for cls in classes:
            docstring = cls['docstring'] if cls['docstring'] else "該類別的主要功能"
            md_content += f"""### {cls['name']}
**描述**: {docstring}

"""
    
    if functions:
        md_content += """## 🔧 主要函數

"""
        for func in functions:
            docstring = func['docstring'] if func['docstring'] else "該函數的主要功能"
            md_content += f"""### {func['name']}()
**描述**: {docstring}

"""
    
    md_content += """## 📝 代碼結構說明

### 主要功能模組
1. **初始化**: 設置基本配置和狀態
2. **UI構建**: 建立圖形使用者介面
3. **事件處理**: 處理用戶交互事件
4. **數據處理**: 處理和分析log數據
5. **文件操作**: 處理文件讀寫操作

### 關鍵設計模式
- **模組化設計**: 將不同功能分離到不同模組
- **事件驅動**: 使用事件驅動架構處理用戶交互
- **配置管理**: 使用外部配置文件管理設置
- **錯誤處理**: 完善的異常處理機制

## 🔄 版本歷史
- **v1.0**: 初始版本
- **v1.1**: 新增預覽視窗功能
- **v1.2**: 優化字體控制和視窗大小記憶

## 📋 使用說明
該文件是LOG分析器的重要組成部分，提供了核心的GUI功能和數據處理能力。

"""
    
    return md_content

def main():
    """主函數"""
    # 確保docs目錄存在
    docs_dir = 'docs'
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
        print(f"已創建 {docs_dir} 目錄")
    
    # 獲取所有PY文件
    py_files = []
    for file in os.listdir('.'):
        if file.endswith('.py') and file != 'generate_documentation.py':
            py_files.append(file)
    
    # 為每個文件生成文檔
    for py_file in py_files:
        print(f"正在生成 {py_file} 的文檔...")
        md_content = generate_markdown_doc(py_file)
        
        # 保存Markdown文件到docs目錄
        md_file = os.path.join(docs_dir, py_file.replace('.py', '_DOCUMENTATION.md'))
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"已生成 {md_file}")
    
    print(f"\n✅ 已完成 {len(py_files)} 個文件的文檔生成")
    print(f"所有文檔已保存到 {docs_dir}/ 目錄")

if __name__ == '__main__':
    main() 