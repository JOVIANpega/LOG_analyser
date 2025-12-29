# 修復更新報告 v2 (與 V2.1.0 重大更新)

## ✅ 已完成的修復 (2025-12-24 之前)

### 1. Excel 生成返回值錯誤 ✓
*   **問題**：`not enough values to unpack (expected 3, got 2)`
*   **原因**：`export_pass_fail_workbooks` 只返回 2 個值，但 `analysis_engine.py` 期望 3 個值。
*   **修復**：修改 `app/excel_writer.py` 的 `export_pass_fail_workbooks` 方法，現在返回 3 個值：`(pass_path, fail_path, fail_path_new)`。

### 2. 添加資料夾選擇除錯日誌 ✓
*   **修復**：在 `app/file_handlers.py` 的 `_select_folder_unified` 方法中添加詳細的 DEBUG 日誌，追蹤檔案數量、路徑、類型與處理流程。

---

## 🚀 V2.1.0 增強型導覽與 UI 優化 (2025-12-29)

### ⚡ 全域「快捷導覽」面板 (左側控制列)
*   **集中管理**：將導覽按鈕 (TOP, END, PgUp, PgDn) 統一整合至 GUI 最左側面板，位於「查看操作說明」按鈕下方。
*   **標籤感知**：導覽按鈕會自動根據目前所在的視窗 (FAIL、PASS 或 原始 LOG) 切換捲動對象。

### ⌨️ 鍵盤翻頁優化 (Page-by-Page)
*   **方向鍵強連通**：方向鍵 `↑` / `↓` 現在對應「翻頁」行為 (一鍵翻動整個截面內容)，滿足快速瀏覽需求。
*   **智慧標籤跳轉**：新增 `Alt` + `PageUp` / `PageDown` 組合鍵，可瞬間在測項章節 (`@STEP`) 之間跳轉。

### 🟡 視覺效果同步 (反黃高亮跟隨)
*   **列表同步**：修復鍵盤移動時反黃背景不跟隨的問題。現在選取條與高亮背景會同步移動。
*   **LOG 文本同步**：在原始 LOG 與 FAIL 詳情視窗中，游標移動到哪，黃色高亮就跟到哪。

### 📂 UI 细节調整
*   **選單字體連動**：修正「選擇 LOG 來源」下拉選單字體過小的問題，現在會隨 UI 設定自動縮放。
*   **搜尋預設值**：將搜尋關鍵字預設值設為 `doesn't`。
*   **導航提醒**：在左側面板導覽功能上新增 Tooltip 提示，告知使用者鍵盤快捷鍵的操作方法。

---

## 🛠 修改檔案清單 (V2.1.0)
1.  `app/main_app_full.py`: 核心按鈕與鍵盤綁定邏輯實作。
2.  `app/ui/enhanced_text.py`: 文字視窗反黃高亮跟隨邏輯。
3.  `app/ui/enhanced_treeview.py`: 列表高亮與鍵盤連動。
4.  `app/ui_builder.py`: 導覽按鈕版面配置調整。
5.  `app/enhanced_left_panel.py`: 左側面板新增導覽區域與字體縮放選單。
6.  `docs/USER_GUIDE.html`: 操作手冊更新至 V2.1.0。

---

## 🧪 測試建議
*   **測試一**：在「原始 LOG」嘗試按鍵盤上下鍵，確認是否能大面積翻頁。
*   **測試二**：在標修中按 `Alt` + `PageDn`，確認是否跳轉到下一個 `@STEP`。
*   **測試三**：調整 UI 字體大小，確認「選擇來源」的選單文字是否跟著變大。
