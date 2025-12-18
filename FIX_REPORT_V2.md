# 修復更新報告 v2

## ✅ 已完成的修復

### 1. Excel 生成返回值錯誤 ✓

**問題：** `not enough values to unpack (expected 3, got 2)`

**原因：** `export_pass_fail_workbooks` 只返回 2 個值，但 `analysis_engine.py` 期望 3 個值

**修復：**
- 修改 `app/excel_writer.py` 的 `export_pass_fail_workbooks` 方法
- 現在返回 3 個值：`(pass_path, fail_path, fail_path_new)`
- `fail_path_new` 目前為 `None`，保留給未來的新版 FAIL 報告

### 2. 添加資料夾選擇除錯日誌 ✓

**修復：**
- 在 `app/file_handlers.py` 的 `_select_folder_unified` 方法中添加詳細的 DEBUG 日誌
- 可以追蹤：
  - 選擇了多少個檔案
  - 資料夾路徑
  - 檔案列表
  - 使用者選擇（files/folder）
  - 檔案類型（LOG/壓縮檔）
  - 處理流程

---

## 🧪 測試步驟

### 測試 1: 修復後的壓縮檔處理

1. **選擇單個壓縮檔**
   ```
   - 點擊「選擇檔案」按鈕
   - 選擇一個 .zip/.7z/.rar 檔案
   - 觀察控制台輸出
   - 確認是否正確解壓和生成 Excel
   ```

2. **選擇多個壓縮檔**
   ```
   - 點擊「選擇檔案」按鈕
   - 選擇多個壓縮檔
   - 觀察控制台輸出
   - 確認是否正確處理
   ```

### 測試 2: 資料夾選擇功能

1. **選擇包含 LOG 檔案的資料夾**
   ```
   - 點擊「選擇資料夾」按鈕
   - 在資料夾中選擇一個或多個 LOG 檔案
   - 觀察控制台輸出：
     [DEBUG] _select_folder_unified: 選擇了 X 個檔案
     [DEBUG] - 資料夾路徑: ...
     [DEBUG] - 檔案列表: [...]
     [DEBUG] - 使用者選擇: files/folder
   - 在彈出的對話框中選擇：
     * 「僅處理選定檔案」→ 應該處理選定的檔案
     * 「掃描整個資料夾」→ 應該掃描整個資料夾
   - 確認是否正確生成 Excel
   ```

2. **選擇包含壓縮檔的資料夾**
   ```
   - 點擊「選擇資料夾」按鈕
   - 在資料夾中選擇壓縮檔
   - 觀察控制台輸出
   - 確認處理流程
   ```

---

## 📊 預期的控制台輸出

### 成功的資料夾選擇（LOG 檔案）：

```
[DEBUG] _select_folder_unified: 選擇了 2 個檔案
[DEBUG] - 資料夾路徑: D:\Test\Logs
[DEBUG] - 檔案列表: ['test1.log', 'test2.log']
[DEBUG] - 使用者選擇: folder
[DEBUG] - 掃描整個資料夾: D:\Test\Logs
[DEBUG] 準備匯出 Excel
[DEBUG] - 找到檔案數: 5
[DEBUG] - PASS logs: 3
[DEBUG] - FAIL logs: 2
[DEBUG] - cancel_flag: False
[DEBUG] - 輸出目錄 (資料夾模式): D:\Test\Logs
[DEBUG] - 開始調用 export_pass_fail_workbooks...
[DEBUG] - Excel 生成成功！
[DEBUG]   - PASS 檔案: D:\Test\Logs\PASS匯總.xlsx
[DEBUG]   - FAIL 檔案: D:\Test\Logs\FAIL匯總.xlsx
[DEBUG] 分析完成，關閉進度條
```

### 成功的壓縮檔處理：

```
[DEBUG] _select_folder_unified: 選擇了 1 個檔案
[DEBUG] - 資料夾路徑: D:\Test\Archives
[DEBUG] - 檔案列表: ['test.zip']
[DEBUG] - 使用者選擇: files
[DEBUG] - 包含壓縮檔: True
[DEBUG] - 壓縮檔數量: 1
[DEBUG] - LOG 檔案數量: 0
[DEBUG] - 處理壓縮檔
[DEBUG] 準備匯出 Excel
...
```

---

## 🔍 已知問題和建議

### 問題 1: 選擇資料夾後沒有反應

**可能原因：**
1. 使用者在對話框中點擊了「取消」或關閉視窗
2. 對話框沒有正確返回選擇結果
3. `show_smart_select_dialog` 返回了 `'cancel'` 或其他值

**診斷方法：**
- 查看控制台輸出中的 `[DEBUG] - 使用者選擇: XXX`
- 如果沒有這行輸出，說明對話框沒有正確返回

**建議修復：**
- 在 `show_smart_select_dialog` 中添加 DEBUG 日誌
- 確保對話框正確處理所有情況

### 問題 2: 進度框沒有顯示「生成 Excel」

**可能原因：**
1. 分析過程中出現錯誤，沒有到達 Excel 生成步驟
2. `cancel_flag` 被意外設定為 True
3. 沒有找到任何檔案

**診斷方法：**
- 查看控制台輸出
- 檢查是否有 `[DEBUG] 準備匯出 Excel` 訊息
- 檢查 `cancel_flag` 的值

---

## 📝 修改摘要

| 檔案 | 修改內容 | 行數 |
|------|---------|------|
| `app/excel_writer.py` | 修復返回值問題，添加第三個返回值 | 288-315 |
| `app/file_handlers.py` | 添加資料夾選擇的 DEBUG 日誌 | 157-190 |

---

## 🚀 下一步

1. **立即測試**
   - 運行應用程式
   - 測試壓縮檔處理（應該不再出現 unpack 錯誤）
   - 測試資料夾選擇功能
   - 觀察控制台輸出

2. **如果仍有問題**
   - 提供控制台的完整輸出
   - 說明具體的操作步驟
   - 截圖錯誤訊息

3. **可能需要進一步修復的地方**
   - `show_smart_select_dialog` 的返回值處理
   - 對話框關閉時的行為
   - 取消操作的處理

---

準備好測試了嗎？請運行 `python main.py` 並告訴我結果！
