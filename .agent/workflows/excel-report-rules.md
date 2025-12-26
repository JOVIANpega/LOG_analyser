---
description: Excel 報表生成與錯誤解析規則
---

# Excel 報表生成與錯誤解析規則 (Workflow)

此工作流記錄了解析 LOG 系統中關於 Excel 報表生成與錯誤抓取的關鍵邏輯，以確保後續維護與功能擴充的一致性。

## 1. 錯誤抓取與優先級 (Error Prioritization)
當分析 FAIL Log 時，系統必須決定哪一個錯誤是「最主要的原因」並顯示在 `FAIL_LIST` 中：
- **掃描方向**：採取 **Bottom-up (由下往上)** 搜尋。最後出現的錯誤通常是導致測試終止的真實原因。
- **關鍵字優先級**：
  1. `doesn't match` (最高優先級)
  2. `is Fail`
  3. `FAIL` / `FAILED`
  4. `ERROR`
  5. `Status:False`
  6. `timeout`
- **解析器配置**：`LogParser` 必須包含這些關鍵字於 `fail_keywords` 中，否則區塊將被跳過。

## 2. FAIL_LIST 彙總規則 (Summary Sheet)
- **去重原則**：每份 Log 檔案在 `FAIL_LIST` 中 **僅佔據一行 (Row)**。
- **主要錯誤**：該行必須對應到整份 Log 中優先級最高且最後出現的 `last_fail`。
- **欄位資訊**：包含 ISN, Station, FAIL Item, FAIL Reason, Count。

## 3. 詳細 Log 工作表設計 (Detailed Sheets)
- **頂端預覽盒 (Preview Box)**：
  - 在分頁頂端顯示紅色背景的「錯誤區塊」預覽。
  - 預覽內容必須包含從「指令下發 (>)」到「報錯產生」的完整上下文。
  - 提供直接跳轉至 Log 正確行號的超連結。
- **視覺風格 (Premium Style)**：
  - **Phase 分隔線**：深綠色背景 (#2E7D32)，白色加粗文字。
  - **測項底色交替**：淡藍色 (#E8F4FD) 與淡紫色 (#F0E8FF) 背景交替。
  - **導航連結**：`[回到 Summary]` 需使用 16pt 加粗、深藍色背景 (#000080)、白字。

## 4. Excel 穩定性與相容性
- **公式轉義**：所有以 `=` 開頭的 Log 行，寫入 Excel 前必須補上單引號 `'`（例如 `'====`），防止 Excel 誤判為無效公式導致檔案損毀。
- **分頁命名**：移除名稱中的點號 `.` 並改為底線 `_`，長度限制在 31 字元內。
- **存檔保護**：若目標檔案已開啟，自動添加時間戳（如 `_163930`）進行避讓。

// turbo-all
