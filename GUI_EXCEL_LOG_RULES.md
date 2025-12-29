# GUI 和 Excel LOG 显示规则文档

## 📋 版本信息
- **文档版本**: v2.0 (重大简化更新)
- **创建日期**: 2025-12-26
- **最后更新**: 2025-12-26 17:56
- **维护人员**: Antigravity AI

---

## 🎯 核心原则

**黄金法则**: GUI 和 Excel 的视觉呈现和逻辑行为必须 100% 一致！

**简化原则 (v2.0 新增)**:
- ❌ **移除复杂视觉元素**（斑马纹背景）
- ✅ **突出关键信息**（错误行红色高亮）
- ✅ **清晰的视觉层次**（doesn't match 整段红色）

每次修改任何与日志显示相关的代码时，必须：
1. ✅ 检查本文档的所有规则
2. ✅ 同时验证 GUI 和 Excel 的输出
3. ✅ 运行完整测试确保一致性

---

## 📌 错误原因提取规则

### Bottom-up 优先级（从日志最后往上找）

无论是 GUI 还是 Excel，错误原因提取必须严格遵循以下优先级：

```python
# 优先级 1: DOESN'T MATCH （最高优先级）
for line in reversed(log_lines):
    if "doesn't match" in line.lower():
        return line  # 立即返回，不再继续搜索

# 优先级 2: is Fail
for line in reversed(log_lines):
    if "is Fail" in line:
        return extract_and_clean(line)

# 优先级 3: All Test Aborted
for line in reversed(log_lines):
    if "All Test Aborted" in line.lower():
        return line

# 优先级 4: 其他关键错误
critical_keywords = [
    'Status:False', 'executes fail', 'segmentation fault',
    'core dumped', 'timeout', 'exception', 'FAIL', 'ERROR'
]
for keyword in critical_keywords:
    for line in reversed(log_lines):
        if keyword.lower() in line.lower():
            return line

# Fallback: 使用第一个 fail_item 的 error 字段
return fail_items[0].get('error', '未知错误')
```

### 实现位置检查清单

- [ ] **GUI - FAIL 测项显示**: `app/result_display.py` → `_extract_main_fail_reason_from_items()`
- [ ] **GUI - 原始LOG显示**: `app/result_display.py` → `_insert_formatted_fail_content()` 
- [ ] **Excel - FAIL_LIST**: `app/excel/excel_fail_list_builder.py` → Line 84-95
- [ ] **Excel - Summary**: `app/excel/excel_summary_builder.py` (如有)
- [ ] **Excel - Sheet Builder**: `app/excel/sheet_builder.py` → Line 26-70

---

## 🎨 视觉呈现规则 (v2.0 简化版)

### 🔴 核心变更 (v2.0)

1. ❌ **移除斑马纹背景** - 所有日志行默认白色背景
2. ✅ **doesn't match 整段红色** - 从指令到测试结束全部红色高亮
3. ✅ **单行错误红色** - FAIL/ERROR/NACK/TIMEOUT 单行红色背景
4. ❌ **移除圆饼图** - FAIL_LIST 不再显示统计图表

### 1. 背景颜色规则

| 条件 | 背景色 | 说明 |
|------|--------|------|
| 默认 | `white` (白色) | 所有正常日志 |
| doesn't match 区块 | `#FFE1E1` (粉红) | 从指令到错误结束的整段 |
| FAIL/ERROR 单行 | `#FFE1E1` (粉红) | 仅该错误行 |
| Criteria 判定失败 | `#FFE1E1` (粉红) | 数值超出范围的行 |

**doesn't match 区块范围计算**:
```python
# 起点：往上找最近的指令 ('>') 或测项 ('Do @STEP')
for i in range(error_idx, max(-1, error_idx - 50), -1):
    if '>' in line or 'Do @STEP' in line:
        block_start = i
        break

# 终点：往下延伸到测试完成或下一个测项
for i in range(error_idx + 1, min(len(lines), error_idx + 10)):
    if 'Test Completed' in line or 'Do @STEP' in line:
        block_end = i - 1
        break
```

### 2. 错误预览框（Error Preview Box）

**位置**: 
- **GUI**: "原始LOG" 标签页顶部 (已实现)
- **Excel**: 每个 FAIL 日志 sheet 的顶部（Row 3-N）

**样式**:
```
┌─────────────────────────────────────────────────┐
│ [ 发现错误点 ] (点击跳转至 Log 正确位置)          │  ← 超链接，颜色 #FF0000
├─────────────────────────────────────────────────┤
│   >> 2025/12/26 16:07:17 [1]>Send Test cmd     │  ← 粉红背景 #FFE1E1
│   >> D:\path\>" doesn't match @SPEC_PASS        │  ← 深红字体 #C00000，粗体
│   >> Status:False... Error:PASS                 │
└─────────────────────────────────────────────────┘
```

### 3. Phase 章节标题（Chapter Headers）

**样式**:
- **背景色**: `#2E7D32` (深绿)
- **文字颜色**: `#FFFFFF` (白色)
- **字体**: Consolas, 12pt, Bold
- **对齐**: 居中
- **格式**: ` --   [ PHASE X TEST = Step Name ] `

### 4. 关键字颜色标注

| 关键字 | 文字颜色 | 背景色 | 加粗 | 应用范围 |
|--------|---------|--------|------|---------|
| `doesn't match` | `#ff0000` 红色 | `#FFE1E1` 粉红 | ✅ | **整段区块** |
| `is Fail` | `#ff0000` 红色 | `#FFE1E1` 粉红 | ✅ | 单行 |
| `FAIL` | `#ff0000` 红色 | `#FFE1E1` 粉红 | ✅ | 单行 |
| `ERROR` | `#ff0000` 红色 | `#FFE1E1` 粉红 | ✅ | 单行 |
| `NACK` | `#ff0000` 红色 | `#FFE1E1` 粉红 | ✅ | 单行 |
| `TIMEOUT` | `#ff0000` 红色 | `#FFE1E1` 粉红 | ✅ | 单行 |
| `PASS` | `#28a745` 绿色 | 无 | ✅ | 单行 |
| 指令 (`>`) | `#007bff` 蓝色 | 无 | ✅ | 单行 |
| 回应 (`<`) | `#6f42c1` 紫色 | 无 | ❌ | 单行 |
| `Do @STEP` | `#007bff` 蓝色 (FAIL) <br> `#28a745` 绿色 (PASS) | 无 | ✅ | 单行 |

**⚠️ 特殊规则**: 在 doesn't match 区块内，所有文字默认为红色，忽略其他颜色规则

### 5. Criteria 数值判定

**格式**: `= value (min, max)`

**规则**:
```python
if min <= value <= max:
    color = '#28a745'  # 绿色 PASS
    bold = False
else:
    color = '#ff0000'  # 红色 FAIL
    bold = True
    background = '#FFE1E1'  # 粉红背景
```

---

## 🔗 超链接规则

### FAIL_LIST → 详细日志

**触发元素**: ISN 列（例如 `0306250012`）

**超链接格式**: `#'SheetName'!A{error_row}`

**样式**:
- 颜色: `#0563C1` (蓝色)
- 下划线: 单线
- 加粗: ✅

**目标定位**: 
- 使用与 FAIL Reason 相同的 bottom-up 优先级查找错误行
- 直接跳转到该行（非预览框）

### Summary → 详细日志

**触发元素**: "查看详细 LOG" 链接

**超链接格式**: `#'SheetName'!A1`

**样式**: 深蓝背景 (#000080)，白字，16pt

---

## 📂 文件架构与职责

### GUI 核心文件

| 文件 | 职责 | 关键方法 |
|-----|------|---------|
| `app/log_parser.py` | 日志解析与标注生成 | `_generate_ui_annotations()` |
| `app/ui/enhanced_text.py` | GUI 文本渲染 | `_insert_with_annotations()` |
| `app/result_display.py` | 结果显示与错误提取 | `_extract_main_fail_reason_from_items()` <br> `_insert_formatted_fail_content()` |

### Excel 核心文件

| 文件 | 职责 | 关键方法 |
|-----|------|---------|
| `app/excel/sheet_builder.py` | 详细日志写入与标注应用 | `write_raw_log_with_annotations()` |
| `app/excel/excel_fail_list_builder.py` | FAIL_LIST 构建 | `build_fail_list_sheet()` |
| `app/excel/excel_summary_builder.py` | Summary 构建 | `create_summary_sheet()` |
| `app/excel/excel_writer.py` | Excel 主协调器 | `_build_fail_workbook()` |

---

## ✅ 一致性检查清单

每次修改后，必须验证以下项目：

### 视觉一致性
- [ ] GUI 和 Excel 的斑马纹背景颜色相同
- [ ] GUI 和 Excel 的错误区块背景颜色相同
- [ ] GUI 和 Excel 的 Phase 章节标题样式相同
- [ ] GUI 和 Excel 的关键字颜色标注相同
- [ ] GUI 和 Excel 的加粗规则相同

### 逻辑一致性
- [ ] GUI 和 Excel 使用相同的 bottom-up 优先级提取错误原因
- [ ] GUI 和 Excel 的错误区块范围计算逻辑相同
- [ ] GUI 和 Excel 的斑马纹切换逻辑相同
- [ ] GUI 和 Excel 的 Criteria 判定逻辑相同

### 功能完整性
- [x] GUI "原始LOG" 标签页显示错误预览框
- [x] GUI "FAIL 测项" 标签页显示正确的错误原因
- [x] Excel FAIL_LIST ISN 列超链接工作正常
- [ ] Excel 错误预览框显示正确
- [ ] Excel Summary 显示正确的 FAIL Reason

---

## 🔧 常见修改场景

### 场景1: 新增错误关键字

**必须修改的位置**:
1. `app/result_display.py` → `_extract_main_fail_reason_from_items()` 函数
2. `app/excel/sheet_builder.py` → `write_raw_log_with_annotations()` 函数
3. 本文档的"错误原因提取规则"章节

**测试步骤**:
1. 准备包含新关键字的测试日志
2. 验证 GUI FAIL 测项显示
3. 验证 Excel FAIL_LIST 显示
4. 验证超链接跳转位置

### 场景2: 修改颜色方案

**必须修改的位置**:
1. `app/log_parser.py` → `_generate_ui_annotations()` 的颜色常量
2. `app/excel/sheet_builder.py` → `color_map` 字典
3. `app/ui/enhanced_text.py` → `setup_tags()` 方法
4. 本文档的"视觉呈现规则"章节

**测试步骤**:
1. 打开 GUI 和 Excel，对比颜色
2. 使用颜色选择器验证 hex 值
3. 截图归档到测试报告

### 场景3: 调整错误区块范围

**必须修改的位置**:
1. `app/log_parser.py` → `_generate_ui_annotations()` 的错误检测逻辑
2. `app/excel/sheet_builder.py` → 错误预览框生成逻辑
3. `app/result_display.py` → `_insert_formatted_fail_content()` 的错误预览生成

**测试步骤**:
1. 使用不同类型的错误日志测试
2. 验证起始和结束位置正确
3. 确保不会包含无关内容

---

## 🐛 已知问题与限制

### 当前限制
1. **单次错误**: 每个 FAIL 日志只显示一个主要错误（最后一个 bottom-up 找到的）
2. **预览长度**: 错误预览框最多显示 20 行（可配置）
3. **超链接范围**: Excel 超链接只能在同一工作簿内跳转

### 未来改进方向
- [ ] 支持多错误并列显示
- [ ] 错误分类与聚合统计
- [ ] 可配置的颜色主题
- [ ] 导出为 PDF 时保持样式

---

## 📝 修改日志

| 日期 | 修改内容 | 修改人 | 影响范围 |
|------|---------|--------|---------|
| 2025-12-26 | 创建初始规则文档 | Antigravity AI | 全局规则定义 |
| 2025-12-26 | 统一 bottom-up 优先级逻辑 | Antigravity AI | GUI + Excel 错误提取 |
| 2025-12-26 | 添加 FAIL_LIST ISN 超链接 | Antigravity AI | Excel FAIL_LIST |
| 2025-12-29 | 新增全域導覽按鈕與鍵盤翻頁規則 (v2.1) | Antigravity AI | GUI 導覽控制 |

---

## ⌨️ 導覽與鍵盤操作規則 (v2.1)

為確保大數據日誌處理的極速體驗，導覽行為必須符合以下規範：

### 1. 全域導覽按鈕 (Global Navigation)
*   **按鈕位置**: 整合於左側面板 (Navigation Area)。
*   **行為邏輯**: 
    1. 偵測目前焦點所在的 Tab (FAIL, PASS, Raw Log)。
    2. 調用該分頁對應的 `EnhancedText` 或 `EnhancedTreeview` 捲動方法。
    3. 必須包含: **Top**, **Page Up**, **Page Down**, **End**。

### 2. 鍵盤快捷鍵標準
*   **翻頁 (Paging)**: 方向鍵 `↑` / `↓` 必須映射至 `page_up` / `page_down` (一次捲動一整個視窗)。
*   **章節跳轉 (Chapter Jump)**: `Alt + PageUp` / `Alt + PageDown` 必須在含有 `@STEP` 的行之間跳轉。
*   **頂/末端跳轉**: `Ctrl + Home` / `Ctrl + End` (標準行為)。

### 3. 視覺一致性
*   **黃色高亮跟隨**: 在 `EnhancedText` 中，當游標透過鍵盤或滑鼠移動時，`current_line_highlight` (背景色 #FFF2CC) 必須即時更新至該行。
*   **Treeview 選取同步**: 鍵盤上下移動選取項時，必須觸發 `hover` 標籤與細節預覽跟隨。

---

**文档结束** | 请在每次修改前仔细阅读相关章节，确保符合规范！
