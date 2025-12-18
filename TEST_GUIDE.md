# 測試指南：多檔 LOG 選擇問題診斷

## 🎯 問題描述

**症狀：** 手動選擇多個 LOG 檔案後，不會生成 Excel

**已確認可以工作的場景：**
- ✅ 解壓縮 → 生成 Excel OK
- ✅ 掃描資料夾 → 生成 Excel OK
- ❌ 手動選擇 2 個以上 LOG 檔案 → 不會生成 Excel

---

## 🔍 診斷步驟

### 步驟 1: 選擇多個 LOG 檔案

1. 運行應用程式：`python main.py`
2. 點擊「📄 選擇檔案 (Log/壓縮檔)」按鈕
3. 選擇 2 個或更多 `.log` 檔案
4. 點擊「開啟」

### 步驟 2: 觀察控制台輸出

應該會看到以下 DEBUG 訊息：

```
[DEBUG] _select_files_unified: 選擇了 X 個檔案
[DEBUG] - 包含壓縮檔: False
[DEBUG] - 檔案列表: ['file1.log', 'file2.log', ...]
[DEBUG] - 處理多個 LOG 檔案
[DEBUG] - 設定 current_mode = 'multi'
[DEBUG] - 設定 current_log_path = X 個檔案
[DEBUG] - 調用 _analyze_enhanced_log()
[DEBUG] _analyze_enhanced_log 被調用
[DEBUG] - current_mode: multi
[DEBUG] - current_log_path 類型: <class 'list'>
[DEBUG] - current_log_path 包含 X 個檔案
[DEBUG] - 顯示進度: X 個檔案
[DEBUG] - 調用 _analyze_enhanced_multiple_files()
[DEBUG] 準備匯出 Excel
[DEBUG] - 找到檔案數: X
[DEBUG] - PASS logs: X
[DEBUG] - FAIL logs: X
[DEBUG] - cancel_flag: False
[DEBUG] - 輸出目錄 (檔案模式): ...
[DEBUG] - 開始調用 export_pass_fail_workbooks...
[DEBUG] - Excel 生成成功！
[DEBUG]   - PASS 檔案: ...
[DEBUG]   - FAIL 檔案: ...
[DEBUG] 分析完成，關閉進度條
```

---

## 📊 可能的問題和診斷

### 情況 1: 沒有看到 `[DEBUG] _analyze_enhanced_log 被調用`

**原因：** `_analyze_enhanced_log()` 沒有被調用

**可能的問題：**
- `_select_files_unified` 中的調用失敗
- 有異常被捕獲但沒有顯示

**解決方法：**
- 檢查是否有錯誤訊息
- 確認 `self._analyze_enhanced_log` 方法存在

### 情況 2: 看到 `_analyze_enhanced_log 被調用` 但沒有 `調用 _analyze_enhanced_multiple_files()`

**原因：** `current_mode` 不是 `'multi'`

**可能的問題：**
- `current_mode` 被意外修改
- 條件判斷錯誤

**解決方法：**
- 檢查 `current_mode` 的值
- 確認邏輯分支

### 情況 3: 看到 `調用 _analyze_enhanced_multiple_files()` 但沒有 `準備匯出 Excel`

**原因：** 多檔分析過程中出現錯誤

**可能的問題：**
- 檔案解析失敗
- `target_files` 為空
- 有異常被捕獲

**解決方法：**
- 檢查是否有 `[ERROR]` 訊息
- 查看完整的錯誤堆疊

### 情況 4: 看到 `準備匯出 Excel` 但 `cancel_flag: True`

**原因：** 分析被取消

**可能的問題：**
- 用戶點擊了取消按鈕
- `cancel_flag` 被意外設定

**解決方法：**
- 不要點擊取消
- 檢查 `cancel_flag` 的設定邏輯

### 情況 5: 看到 `開始調用 export_pass_fail_workbooks...` 但沒有成功訊息

**原因：** Excel 生成過程中出現錯誤

**可能的問題：**
- `excel_writer` 方法內部錯誤
- 檔案權限問題
- 磁碟空間不足

**解決方法：**
- 檢查錯誤訊息
- 確認輸出目錄可寫

---

## 🛠️ 已添加的 DEBUG 日誌

### 檔案 1: `app/file_handlers.py`

**位置：** `_select_files_unified` 方法 (Line 66-100)

**日誌內容：**
- 選擇的檔案數量
- 是否包含壓縮檔
- 檔案列表
- 處理流程（單一/多個 LOG/壓縮檔）
- 設定的變數值

### 檔案 2: `app/analysis_engine.py`

**位置：** `_analyze_enhanced_log` 方法 (Line 16-62)

**日誌內容：**
- 方法被調用
- `current_mode` 的值
- `current_log_path` 的類型和內容
- 顯示的進度訊息
- 調用的子方法

**位置：** `_analyze_enhanced_multiple_files_thread` 方法 (Line 386-450)

**日誌內容：**
- 找到的檔案數量
- PASS/FAIL logs 數量
- `cancel_flag` 狀態
- 輸出目錄
- Excel 生成結果

---

## 📝 測試報告模板

請在測試後提供以下資訊：

```
### 測試環境
- 選擇的檔案數量：
- 檔案類型：
- 檔案所在目錄：

### 控制台輸出
（請複製完整的 DEBUG 訊息）

### 觀察到的行為
- 進度條是否顯示？
- 顯示的訊息是什麼？
- 是否有錯誤對話框？
- Excel 是否生成？

### 問題出現在哪個步驟？
（根據上面的「可能的問題和診斷」）
```

---

## 🚀 下一步

1. **運行測試**
   - 選擇 2-3 個 LOG 檔案
   - 觀察控制台輸出
   - 記錄所有 DEBUG 訊息

2. **提供資訊**
   - 完整的控制台輸出
   - 觀察到的行為
   - 任何錯誤訊息

3. **根據診斷結果修復**
   - 我會根據 DEBUG 訊息精確定位問題
   - 進行針對性修復

---

準備好測試了嗎？請運行應用程式並告訴我完整的控制台輸出！
