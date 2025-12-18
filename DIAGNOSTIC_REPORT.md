# 診斷報告：Excel 生成失敗 & GUI 視窗無法關閉

## 問題 1: Excel 生成失敗

### 根本原因分析

檢查 `app/analysis_engine.py` 第 386-407 行的 Excel 生成邏輯：

```python
# 4. 匯出 Excel
if not self._cancel_flag:  # ← 問題點 1: 如果 _cancel_flag 為 True，Excel 不會生成
    self._safe_update_progress_text("正在產生 Excel 報告...")
    try:
        # 決定輸出目錄
        if os.path.isdir(self.current_log_path):
            out_dir = self.current_log_path
        else:
            out_dir = os.path.dirname(target_files[0])
            
        pass_path, fail_path, fail_path_new = self.excel_writer.export_pass_fail_workbooks(
            out_dir, pass_logs, fail_logs
        )
        
        # 5. 顯示完成視窗
        self.root.after(0, lambda: self._show_open_folder_prompt(
            out_dir, total_files, len(pass_logs), len(fail_logs), pass_path, fail_path, fail_path_new
        ))
        
    except Exception as e:
        self.root.after(0, lambda: messagebox.showerror("匯出錯誤", f"產生 Excel 報告時發生錯誤: {e}"))
        traceback.print_exc()
```

### 可能的問題點

1. **`self._cancel_flag` 被意外設定為 True**
   - 檢查進度管理器是否錯誤設定了此旗標
   
2. **`self.excel_writer` 未初始化**
   - 需要檢查主應用程式是否正確初始化 ExcelWriter

3. **異常被靜默捕獲**
   - 錯誤訊息可能沒有正確顯示

4. **`target_files` 為空**
   - 如果沒有找到檔案，`target_files[0]` 會引發 IndexError

---

## 問題 2: GUI 視窗無法關閉

### 根本原因

使用 `grab_set()` 的視窗如果沒有正確調用 `grab_release()` 或 `destroy()`，會導致：
- 視窗無法關閉
- 主視窗被鎖定
- 應用程式無響應

### 受影響的檔案

檢查發現以下檔案使用了 `grab_set()`：

1. **app/dialogs.py** (2 處)
   - Line 20: `show_mixed_content_dialog`
   - Line 137: `show_smart_select_dialog`

2. **app/ui_builder.py** (2 處)
   - Line 298: `_show_text_viewer_window`
   - Line 364: `_show_open_folder_prompt`

3. **app/progress_manager.py** (1 處)
   - Line 96: `show_progress`

4. **app/file_handlers.py** (1 處)
   - Line 672: `_choose_archives_dialog`

5. **app/ui/enhanced_treeview.py** (1 處)
   - Line 591: 詳細視窗

### 問題模式

```python
# 錯誤模式
win = tk.Toplevel(self.root)
win.grab_set()  # 鎖定輸入
# ... 如果這裡發生異常，視窗永遠無法關閉

# 正確模式
win = tk.Toplevel(self.root)
win.grab_set()

def close_window():
    try:
        win.grab_release()  # 重要！釋放鎖定
    except:
        pass
    win.destroy()

win.protocol("WM_DELETE_WINDOW", close_window)
```

---

## 修復方案

### 方案 1: 修復 Excel 生成問題

需要添加詳細的除錯日誌：

```python
def _analyze_enhanced_multiple_files_thread(self):
    """背景執行的多檔分析邏輯"""
    try:
        target_files = []
        
        # ... 檔案收集邏輯 ...
        
        print(f"[DEBUG] 找到 {len(target_files)} 個檔案")
        print(f"[DEBUG] _cancel_flag = {self._cancel_flag}")
        
        # ... 分析邏輯 ...
        
        # 4. 匯出 Excel
        print(f"[DEBUG] 準備匯出 Excel, cancel_flag = {self._cancel_flag}")
        if not self._cancel_flag:
            self._safe_update_progress_text("正在產生 Excel 報告...")
            try:
                print(f"[DEBUG] PASS logs: {len(pass_logs)}, FAIL logs: {len(fail_logs)}")
                
                # 決定輸出目錄
                if os.path.isdir(self.current_log_path):
                    out_dir = self.current_log_path
                else:
                    if not target_files:
                        print("[ERROR] target_files 為空！")
                        raise ValueError("沒有找到任何檔案")
                    out_dir = os.path.dirname(target_files[0])
                
                print(f"[DEBUG] 輸出目錄: {out_dir}")
                print(f"[DEBUG] excel_writer 存在: {hasattr(self, 'excel_writer')}")
                
                pass_path, fail_path, fail_path_new = self.excel_writer.export_pass_fail_workbooks(
                    out_dir, pass_logs, fail_logs
                )
                
                print(f"[DEBUG] Excel 生成成功！")
                print(f"[DEBUG] PASS: {pass_path}")
                print(f"[DEBUG] FAIL: {fail_path}")
                
                # ... 顯示完成對話框 ...
```

### 方案 2: 修復視窗無法關閉問題

需要修改所有使用 `grab_set()` 的地方，確保正確釋放：

#### 2.1 修復 `progress_manager.py`

```python
def close_progress(self):
    """關閉進度顯示 (重置狀態列或關閉彈窗)"""
    self._stop_flashing()
    try:
        # 重置嵌入式狀態列
        if self._status_label:
            self._status_label.config(text="就緒")
        if self._main_progress_bar:
            self._main_progress_bar.stop()
            self._main_progress_bar['value'] = 0
        
        # 關閉彈窗
        if self._progress_win and self._progress_win.winfo_exists():
            try:
                self._progress_win.grab_release()  # ← 添加這行
            except:
                pass
            self._progress_win.destroy()
    except Exception:
        pass
    self._progress_win = None
    self._cancel_flag = False
```

#### 2.2 修復 `dialogs.py`

在 `show_mixed_content_dialog` 和 `show_smart_select_dialog` 中：

```python
def on_cancel():
    try:
        dialog.grab_release()  # ← 添加這行
    except:
        pass
    dialog.destroy()

# 綁定視窗關閉事件
dialog.protocol("WM_DELETE_WINDOW", on_cancel)
```

#### 2.3 修復 `ui_builder.py`

在 `_show_open_folder_prompt` 中：

```python
def on_cancel():
    try:
        win.grab_release()  # ← 添加這行
    except:
        pass
    win.destroy()

# 綁定視窗關閉事件
win.protocol("WM_DELETE_WINDOW", on_cancel)
```

---

## 測試步驟

### 測試 1: Excel 生成

1. 選擇多個 LOG 檔案
2. 觀察控制台輸出的 DEBUG 訊息
3. 確認 Excel 檔案是否生成
4. 檢查是否顯示完成對話框

### 測試 2: 視窗關閉

1. 打開各種對話框（檔案選擇、進度視窗、完成對話框）
2. 嘗試用 X 按鈕關閉
3. 嘗試用取消按鈕關閉
4. 確認主視窗不會被鎖定

---

## 優先級

1. **高優先級**: 修復進度視窗無法關閉（影響用戶體驗）
2. **高優先級**: 添加 Excel 生成的除錯日誌（找出根本原因）
3. **中優先級**: 修復所有對話框的 grab_release
4. **低優先級**: 優化錯誤處理和用戶提示

---

## 下一步行動

您希望我：
1. 直接修復這些問題？
2. 先運行應用程式測試並收集更多資訊？
3. 創建一個簡化的測試腳本來重現問題？
