# -*- coding: utf-8 -*-
"""
File Handler Mixin
Handles all file selection, compression, and extraction operations
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import tempfile
import shutil


class FileHandlerMixin:
    """Mixin class for file handling operations"""
    
    def _get_default_directory(self):
        """獲取預設目錄 - EXE或PY檔案所在目錄"""
        import sys
        try:
            # 如果是EXE檔案，使用sys.executable
            if getattr(sys, 'frozen', False):
                # 打包成EXE的情況
                default_dir = os.path.dirname(sys.executable)
            else:
                # 直接執行PY檔案的情況
                default_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 如果目錄不存在，使用當前工作目錄
            if not os.path.exists(default_dir):
                default_dir = os.getcwd()
            
            return default_dir
        except Exception:
            # 如果出現任何錯誤，使用當前工作目錄
            return os.getcwd()
    
    def _select_file(self):
        """選擇單一檔案"""
        # 優先使用上次選擇的路徑，如果沒有則使用預設路徑
        if self.settings.get('last_log_path') and os.path.exists(self.settings.get('last_log_path')):
            default_dir = os.path.dirname(self.settings.get('last_log_path'))
        else:
            default_dir = self._get_default_directory()
        
        file_path = filedialog.askopenfilename(
            title="選擇Log檔案", 
            filetypes=[("Log檔案", "*.log"), ("所有檔案", "*.*")],
            initialdir=default_dir
        )
        if file_path:
            # 先清除現有結果，避免誤導
            self._clear_enhanced_results()
            
            # 直接開始分析
            self.root.after(100, lambda: self._start_analysis_after_preview(file_path))
            
    def _start_analysis_after_preview(self, file_path):
        """檔案預覽確認後執行的分析流程"""
        self.current_mode = 'single'
        self.current_log_path = file_path
        filename = os.path.basename(file_path)
        self.file_info_label.config(text=f"已選擇：{filename}", fg='green')
        
        # 儲存選擇的路徑到設定
        self.settings['last_log_path'] = file_path
        self._save_settings_silent()
        
        # 自動開始分析（enhanced）
        self._analyze_enhanced_log()
    
    def _select_folder(self):
        """選擇資料夾"""
        # 優先使用上次選擇的路徑，如果沒有則使用預設路徑
        if self.settings.get('last_folder_path') and os.path.exists(self.settings.get('last_folder_path')):
            default_dir = self.settings.get('last_folder_path')
        else:
            default_dir = self._get_default_directory()
        
        # 先讓使用者看到所有內容物（僅視覺，實際只處理 .log）
        folder_path = filedialog.askdirectory(
            title="選擇Log資料夾",
            initialdir=default_dir
        )
        if folder_path:
            # 先清除現有結果，避免誤導
            self._clear_enhanced_results()
            
            self.current_mode = 'multi'
            self.current_log_path = folder_path
            
            foldername = os.path.basename(folder_path)
            self.file_info_label.config(text=f"已選擇資料夾：{foldername}", fg='blue')
            
            # 儲存選擇的路徑到設定
            self.settings['last_folder_path'] = folder_path
            self._save_settings_silent()
            
            # 自動開始分析（enhanced）
            self._analyze_enhanced_log()
    
    def _select_compressed_file(self):
        """選擇並處理壓縮檔案（支援多選）"""
        # 獲取預設目錄
        if self.settings.get('last_compressed_path') and os.path.exists(self.settings.get('last_compressed_path')):
            default_dir = os.path.dirname(self.settings.get('last_compressed_path'))
        else:
            default_dir = self._get_default_directory()
        
        file_paths = filedialog.askopenfilenames(
            title="選擇壓縮檔案（可多選）", 
            filetypes=[
                ("壓縮檔案", "*.zip;*.7z;*.rar"),
                ("ZIP檔案", "*.zip"),
                ("7Z檔案", "*.7z"), 
                ("RAR檔案", "*.rar"),
                ("所有檔案", "*.*")
            ],
            initialdir=default_dir
        )
        
        if file_paths:
            # 先清除現有結果
            self._clear_enhanced_results()
            
            if len(file_paths) == 1:
                # 單一檔案：直接處理（不顯示預覽視窗）
                self.root.after(100, lambda: self._process_single_compressed_file(file_paths[0]))

            else:
                # 多個檔案：顯示選擇視窗
                self._show_compressed_selection_window(file_paths)
    
    def _process_single_compressed_file(self, file_path):
        """處理單一壓縮檔案"""
        # 背景處理壓縮檔案
        self._show_progress("正在處理壓縮檔", os.path.basename(file_path))
        def _bg():
            try:
                if self._cancel_flag:
                    return
                self._process_compressed_file(file_path)
            finally:
                self.root.after(0, self._close_progress)
        threading.Thread(target=_bg, daemon=True).start()

    def _select_compressed_files(self):
        """整合的壓縮檔選擇功能（支援單一檔案、多個檔案或資料夾）"""
        # 提供選擇方式
        choice = messagebox.askyesnocancel(
            "壓縮檔處理方式", 
            "請選擇壓縮檔處理方式：\\n\\n" +
            "是(Y) - 選擇壓縮檔案（支援多選）\\n" +
            "否(N) - 選擇壓縮檔資料夾（自動搜尋所有壓縮檔）\\n" +
            "取消 - 取消操作\\n\\n" +
            "注意：選擇資料夾時會自動搜尋 .zip/.7z/.rar 檔案"
        )
        
        if choice is True:
            # 選擇壓縮檔案（支援多選）
            self._select_compressed_file()
        elif choice is False:
            # 選擇壓縮檔資料夾
            self._select_compressed_folder()
        # choice is None 表示取消

    def _select_compressed_folder(self):
        """選擇並處理含多個壓縮檔的資料夾（支援多層與內嵌壓縮）"""
        # 取得預設目錄
        if self.settings.get('last_compressed_folder') and os.path.exists(self.settings.get('last_compressed_folder')):
            default_dir = self.settings.get('last_compressed_folder')
        else:
            default_dir = self._get_default_directory()
        
        folder_path = filedialog.askdirectory(title="選擇壓縮檔資料夾", initialdir=default_dir)
        if not folder_path:
            return
        
        # 先清除現有結果
        self._clear_enhanced_results()
        
        # 讓使用者挑選要處理的壓縮檔
        archives = []
        for root, dirs, files in os.walk(folder_path):
            for fn in files:
                if self._is_archive_file(fn):
                    archives.append(os.path.join(root, fn))
        
        if not archives:
            # 提供更詳細的提示和選項
            result = messagebox.askyesno(
                "未找到壓縮檔案", 
                f"在選擇的資料夾中未找到支援的壓縮檔案 (.zip/.7z/.rar)\\n\\n" +
                f"資料夾路徑: {folder_path}\\n\\n" +
                "可能的原因：\\n" +
                "• 資料夾中沒有壓縮檔案\\n" +
                "• 壓縮檔案在其他子資料夾中\\n" +
                "• 壓縮檔案格式不支援\\n\\n" +
                "是否要重新選擇資料夾？"
            )
            if result:
                # 重新選擇資料夾
                self._select_compressed_folder()
            else:
                # 提供其他選項
                choice2 = messagebox.askyesno(
                    "其他選項", 
                    "是否要改為直接選擇壓縮檔案？"
                )
                if choice2:
                    self._select_compressed_file()
            return
        
        self._show_archive_preview(archives)
        selected_archives = self._choose_archives_dialog(archives)
        if not selected_archives:
            return

        # 背景處理整個壓縮資料夾
        self._show_progress("正在處理壓縮資料夾 (多選)", folder_path)
        def _bg():
            temp_dir = None
            try:
                if self._cancel_flag:
                    return
                # 建立總暫存目錄
                temp_dir = tempfile.mkdtemp(prefix="log_archives_")
                extracted_root = os.path.join(temp_dir, "extracted")
                os.makedirs(extracted_root, exist_ok=True)
                
                # 逐一解壓到各自子目錄（顯示百分比）
                total = len(selected_archives)
                self.root.after(0, lambda: self._progress_set_determinate(total))
                for idx, apath in enumerate(selected_archives, 1):
                    if self._cancel_flag:
                        # 取消時清理暫存目錄
                        try:
                            shutil.rmtree(temp_dir, ignore_errors=True)
                        except Exception:
                            pass
                        return
                    base = os.path.splitext(os.path.basename(apath))[0]
                    target = os.path.join(extracted_root, f"{idx:03d}_{base}")
                    os.makedirs(target, exist_ok=True)
                    try:
                        self._update_progress(f"解壓中 {idx}/{total}: {os.path.basename(apath)}")
                        self._extract_archive(apath, target)
                        self._extract_all_archives(target, max_depth=5)
                    except Exception as e:
                        print(f"解壓失敗（略過）：{apath} -> {e}")
                        continue
                    # 更新進度百分比
                    self.root.after(0, lambda i=idx, n=total: self._progress_set_value(i, n))
                
                # 搜尋所有 .log
                log_files = self._find_log_files(extracted_root)
                if not log_files:
                    self.root.after(0, lambda: messagebox.showwarning("警告", "壓縮資料夾展開後未找到 .log 檔案"))
                    return
                
                def _apply_result():
                    if len(log_files) == 1:
                        self.current_mode = 'single'
                        self.current_log_path = log_files[0]
                        filename = os.path.basename(log_files[0])
                        self.file_info_label.config(text=f"已選擇：{filename} (來自壓縮資料夾)", fg='orange')
                    else:
                        self.current_mode = 'multi'
                        self.current_log_path = extracted_root
                        self.file_info_label.config(text=f"已選擇：{len(log_files)} 個LOG檔案 (來自壓縮資料夾)", fg='orange')
                    self.settings['last_compressed_folder'] = folder_path
                    self._save_settings_silent()
                    self._analyze_enhanced_log()
                self.temp_cleanup_path = temp_dir
                self.root.after(0, _apply_result)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("錯誤", f"處理壓縮資料夾時發生錯誤：\\n{e}"))
                if temp_dir and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
            finally:
                self.root.after(0, self._close_progress)
        threading.Thread(target=_bg, daemon=True).start()

    def _show_archive_preview(self, archives: list):
        """在頂部資訊區顯示即將處理的壓縮檔清單（僅預覽）"""
        try:
            lines = ["將處理以下壓縮檔：", ""]
            max_show = 30
            for i, p in enumerate(sorted(archives)[:max_show], 1):
                lines.append(f"  • {os.path.basename(p)}")
            if len(archives) > max_show:
                lines.append(f"... 其餘 {len(archives) - max_show} 個未列出")
            text = "\\n".join(lines)
            if hasattr(self, 'file_info_label'):
                self.file_info_label.config(text=text, justify='left', wraplength=420, fg='#333')
        except Exception as e:
            print(f"顯示壓縮檔預覽失敗: {e}")

    def _choose_archives_dialog(self, archives: list) -> list:
        """彈出多選對話框，讓使用者挑選要處理的壓縮檔。回傳選中的清單。"""
        try:
            win = tk.Toplevel(self.root)
            win.title("選擇要處理的壓縮檔")
            win.geometry("520x420")
            win.transient(self.root)
            win.grab_set()
            frm = tk.Frame(win)
            frm.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)
            lbl = tk.Label(frm, text="請勾選要處理的壓縮檔：")
            lbl.pack(anchor='w')
            lb_frame = tk.Frame(frm)
            lb_frame.pack(fill=tk.BOTH, expand=1)
            canvas = tk.Canvas(lb_frame)
            vsb = tk.Scrollbar(lb_frame, orient="vertical", command=canvas.yview)
            inner = tk.Frame(canvas)
            inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0,0), window=inner, anchor='nw')
            canvas.configure(yscrollcommand=vsb.set)
            canvas.pack(side="left", fill="both", expand=True)
            vsb.pack(side="right", fill="y")

            vars_ = []
            for p in sorted(archives):
                var = tk.BooleanVar(value=True)
                cb = tk.Checkbutton(inner, text=os.path.basename(p), variable=var, anchor='w', justify='left')
                cb.pack(fill=tk.X, anchor='w')
                vars_.append((var, p))

            btns = tk.Frame(frm)
            btns.pack(fill=tk.X, pady=8)
            selected = []
            def on_ok():
                nonlocal selected
                selected = [p for (v,p) in vars_ if v.get()]
                win.destroy()
            def on_cancel():
                selected.clear()
                win.destroy()
            tk.Button(btns, text="全選", command=lambda: [v.set(True) for v,_ in vars_]).pack(side=tk.LEFT)
            tk.Button(btns, text="全不選", command=lambda: [v.set(False) for v,_ in vars_]).pack(side=tk.LEFT, padx=6)
            tk.Button(btns, text="確定", command=on_ok).pack(side=tk.RIGHT)
            tk.Button(btns, text="取消", command=on_cancel).pack(side=tk.RIGHT, padx=6)
            win.wait_window()
            return selected
        except Exception as e:
            print(f"選擇壓縮檔對話框失敗: {e}")
            return archives

    def _process_compressed_file(self, compressed_path):
        """處理壓縮檔案"""
        try:
            # 建立暫存目錄
            temp_dir = tempfile.mkdtemp(prefix="log_analyzer_")
            
            # 檢查取消狀態
            if self._cancel_flag:
                shutil.rmtree(temp_dir, ignore_errors=True)
                return
            
            # 解壓縮
            file_ext = os.path.splitext(compressed_path)[1].lower()
            
            if file_ext == '.zip':
                self._extract_zip(compressed_path, temp_dir)
            elif file_ext == '.7z':
                self._extract_7z(compressed_path, temp_dir)
            elif file_ext == '.rar':
                self._extract_rar(compressed_path, temp_dir)
            else:
                messagebox.showerror("錯誤", "不支援的壓縮格式")
                shutil.rmtree(temp_dir, ignore_errors=True)
                return

            # 檢查取消狀態
            if self._cancel_flag:
                shutil.rmtree(temp_dir, ignore_errors=True)
                return

            # 遞迴展開內嵌壓縮檔
            try:
                self._extract_all_archives(temp_dir, max_depth=5)
            except Exception as sub_e:
                # 不阻斷主流程，僅提示
                print(f"遞迴解壓過程發生問題：{sub_e}")
            
            # 檢查取消狀態
            if self._cancel_flag:
                shutil.rmtree(temp_dir, ignore_errors=True)
                return
            
            # 搜尋 LOG 檔案
            log_files = self._find_log_files(temp_dir)
            
            if not log_files:
                messagebox.showwarning("警告", "壓縮檔中未找到 .log 檔案")
                return
            
            # 根據檔案數量決定處理模式
            if len(log_files) == 1:
                # 單檔模式
                self.current_mode = 'single'
                self.current_log_path = log_files[0]
                filename = os.path.basename(log_files[0])
                self.file_info_label.config(text=f"已選擇：{filename} (來自壓縮檔)", fg='orange')
            else:
                # 資料夾模式
                self.current_mode = 'multi'
                self.current_log_path = temp_dir
                self.file_info_label.config(text=f"已選擇：{len(log_files)} 個LOG檔案 (來自壓縮檔)", fg='orange')
            
            # 儲存選擇的路徑到設定
            self.settings['last_compressed_path'] = compressed_path
            self._save_settings_silent()
            
            # 開始分析 (必須回到主執行緒執行，因為會更新UI)
            self.root.after(0, self._analyze_enhanced_log)
            
            # 註冊清理函數（分析完成後清理暫存檔案）
            self.temp_cleanup_path = temp_dir
            
        except Exception as e:
            messagebox.showerror("錯誤", f"處理壓縮檔案時發生錯誤：\\n{str(e)}")
            # 清理暫存目錄
            if 'temp_dir' in locals() and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _extract_zip(self, zip_path, extract_to):
        """解壓縮 ZIP 檔案"""
        try:
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                total_files = len(file_list)
                
                # 設定進度條為確定模式
                self._safe_update_progress_mode('determinate')
                self._safe_update_progress_max(total_files)
                
                for idx, member in enumerate(file_list, 1):
                    # 檢查取消
                    if self._cancel_flag:
                        break
                        
                    # 更新進度
                    if idx % 5 == 0 or idx == total_files:  # 減少UI更新頻率避免卡頓
                        self._safe_update_progress(idx, total_files, f"解壓縮中 ({idx}/{total_files}): {member}")
                    
                    zip_ref.extract(member, extract_to)
        except Exception as e:
            error_msg = f"ZIP檔案解壓縮失敗: {str(e)}\\n\\n檔案: {zip_path}\\n\\n可能的原因:\\n"
            error_msg += "• 檔案損壞或格式不正確\\n"
            error_msg += "• 檔案被密碼保護\\n"
            error_msg += "• 檔案權限不足\\n"
            error_msg += "• ZIP格式不相容\\n\\n"
            error_msg += "建議:\\n"
            error_msg += "• 檢查檔案是否完整\\n"
            error_msg += "• 嘗試使用其他工具解壓\\n"
            error_msg += "• 檢查檔案是否被密碼保護"
            
            messagebox.showerror("ZIP解壓縮失敗", error_msg)
            raise

    def _extract_7z(self, sevenz_path, extract_to):
        """解壓縮 7Z 檔案（多種方式嘗試）"""
        try:
            import py7zr
            
            # 設定進度條為不確定模式（因為py7zr不支援細粒度回調）
            self._safe_update_progress_mode('indeterminate')
            self._safe_update_progress_text("正在解壓縮 7Z 檔案 (請稍候)...")
            
            # 方法1：標準解壓縮
            try:
                with py7zr.SevenZipFile(sevenz_path, mode='r') as archive:
                    archive.extractall(path=extract_to)
                return
            except Exception as e1:
                print(f"標準7Z解壓縮失敗: {e1}")
                
                # 方法2：嘗試不同的模式
                try:
                    with py7zr.SevenZipFile(sevenz_path, mode='r', password=None) as archive:
                        archive.extractall(path=extract_to)
                    return
                except Exception as e2:
                    print(f"無密碼7Z解壓縮失敗: {e2}")
                    
                    # 方法3：嘗試讀取檔案列表
                    try:
                        with py7zr.SevenZipFile(sevenz_path, mode='r') as archive:
                            file_list = archive.getnames()
                            print(f"7Z檔案包含 {len(file_list)} 個檔案")
                            # 如果檔案列表可以讀取，但解壓失敗，可能是權限問題
                            raise Exception(f"無法解壓縮7Z檔案，但檔案列表可讀取。可能的原因：權限不足或檔案損壞")
                    except Exception as e3:
                        print(f"7Z檔案列表讀取失敗: {e3}")
                        raise e1  # 拋出原始錯誤
                        
        except ImportError:
            messagebox.showerror("錯誤", "需要安裝 py7zr 套件來支援 7Z 格式\\n請執行：pip install py7zr")
            raise
        except Exception as e:
            error_msg = f"7Z檔案解壓縮失敗: {str(e)}\\n\\n檔案: {sevenz_path}\\n\\n可能的原因:\\n"
            error_msg += "• 檔案損壞或格式不正確\\n"
            error_msg += "• 檔案被密碼保護\\n"
            error_msg += "• 檔案權限不足\\n"
            error_msg += "• py7zr版本不相容\\n"
            error_msg += "• 檔案被加密\\n\\n"
            error_msg += "建議:\\n"
            error_msg += "• 檢查檔案是否完整\\n"
            error_msg += "• 嘗試使用7-Zip軟體手動解壓\\n"
            error_msg += "• 更新py7zr套件: pip install --upgrade py7zr\\n"
            error_msg += "• 檢查檔案是否被密碼保護"
            
            messagebox.showerror("7Z解壓縮失敗", error_msg)
            raise

    def _extract_rar(self, rar_path, extract_to):
        """解壓縮 RAR 檔案"""
        try:
            import rarfile
            
            # 設定進度條為不確定模式
            self._safe_update_progress_mode('indeterminate')
            self._safe_update_progress_text("正在解壓縮 RAR 檔案 (請稍候)...")
            
            with rarfile.RarFile(rar_path) as rar_ref:
                rar_ref.extractall(extract_to)
        except ImportError:
            messagebox.showerror("錯誤", "需要安裝 rarfile 套件來支援 RAR 格式\\n請執行：pip install rarfile")
            raise
        except Exception as e:
            error_msg = f"RAR檔案解壓縮失敗: {str(e)}\\n\\n檔案: {rar_path}\\n\\n可能的原因:\\n"
            error_msg += "• 檔案損壞或格式不正確\\n"
            error_msg += "• 檔案被密碼保護\\n"
            error_msg += "• 檔案權限不足\\n"
            error_msg += "• rarfile版本不相容\\n\\n"
            error_msg += "建議:\\n"
            error_msg += "• 檢查檔案是否完整\\n"
            error_msg += "• 嘗試使用其他工具解壓\\n"
            error_msg += "• 更新rarfile套件: pip install --upgrade rarfile"
            
            messagebox.showerror("RAR解壓縮失敗", error_msg)
            raise

    def _is_archive_file(self, filename):
        """判斷是否為支援的壓縮檔案"""
        lower = filename.lower()
        return lower.endswith('.zip') or lower.endswith('.7z') or lower.endswith('.rar')

    def _extract_archive(self, archive_path, extract_to):
        """根據副檔名解壓縮檔案到指定目錄"""
        ext = os.path.splitext(archive_path)[1].lower()
        if ext == '.zip':
            self._extract_zip(archive_path, extract_to)
        elif ext == '.7z':
            self._extract_7z(archive_path, extract_to)
        elif ext == '.rar':
            self._extract_rar(archive_path, extract_to)

    def _extract_all_archives(self, root_dir, max_depth=5):
        """遞迴展開 root_dir 底下所有內嵌壓縮檔（限制深度避免無限循環）"""
        processed = set()
        depth = 0
        while depth < max_depth:
            found_new = False
            for current_root, dirs, files in os.walk(root_dir):
                for fname in files:
                    if not self._is_archive_file(fname):
                        continue
                    full_path = os.path.join(current_root, fname)
                    if full_path in processed:
                        continue
                    # 為每個壓縮檔建立對應資料夾（同名去副檔名加 _extracted）
                    base, _ = os.path.splitext(fname)
                    target_dir = os.path.join(current_root, f"{base}_extracted")
                    try:
                        os.makedirs(target_dir, exist_ok=True)
                        self._extract_archive(full_path, target_dir)
                        processed.add(full_path)
                        found_new = True
                    except Exception as e:
                        print(f"展開內嵌壓縮檔失敗：{full_path} -> {e}")
                        # 繼續嘗試其他檔案
                        continue
            if not found_new:
                break
            depth += 1

    def _find_log_files(self, directory):
        """搜尋目錄中的 LOG 檔案"""
        log_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.log'):
                    log_files.append(os.path.join(root, file))
        return log_files
    
    def _cleanup_temp_files(self):
        """清理壓縮檔解壓縮的暫存檔案"""
        try:
            if hasattr(self, 'temp_cleanup_path') and self.temp_cleanup_path:
                if os.path.exists(self.temp_cleanup_path):
                    shutil.rmtree(self.temp_cleanup_path, ignore_errors=True)
                    print(f"已清理暫存目錄: {self.temp_cleanup_path}")
                self.temp_cleanup_path = None
        except Exception as e:
            print(f"清理暫存檔案時發生錯誤: {e}")

    def _cleanup_temp_files_async(self):
        """在背景執行暫存清理，避免關閉視窗時卡頓"""
        try:
            path = getattr(self, 'temp_cleanup_path', None)
            if not path or not os.path.exists(path):
                return
            def _bg():
                try:
                    self._cleanup_temp_files()
                except Exception as e:
                    print(f"背景清理失敗: {e}")
            threading.Thread(target=_bg, daemon=True).start()
        except Exception as e:
            print(f"啟動背景清理失敗: {e}")
    
    # Safe progress update methods (to be called from background threads)
    def _safe_update_progress_mode(self, mode):
        """安全地更新進度條模式"""
        try:
            if hasattr(self, '_progress_bar') and self._progress_bar:
                if mode == 'indeterminate':
                    self.root.after(0, lambda: self._progress_bar.configure(mode='indeterminate'))
                    self.root.after(0, lambda: self._progress_bar.start(12))
                elif mode == 'determinate':
                    self.root.after(0, lambda: self._progress_bar.stop())
                    self.root.after(0, lambda: self._progress_bar.configure(mode='determinate'))
        except Exception as e:
            print(f"更新進度條模式失敗: {e}")
    
    def _safe_update_progress_max(self, maximum):
        """安全地設定進度條最大值"""
        try:
            if hasattr(self, '_progress_bar') and self._progress_bar:
                self.root.after(0, lambda: self._progress_bar.configure(maximum=max(1, int(maximum))))
                self.root.after(0, lambda: setattr(self._progress_bar, 'value', 0))
        except Exception as e:
            print(f"設定進度條最大值失敗: {e}")
    
    def _safe_update_progress(self, current, total, text):
        """安全地更新進度"""
        try:
            if hasattr(self, '_progress_bar') and self._progress_bar:
                self.root.after(0, lambda: setattr(self._progress_bar, 'value', current))
            if hasattr(self, '_progress_label') and self._progress_label:
                self.root.after(0, lambda: self._progress_label.config(text=text))
        except Exception as e:
            print(f"更新進度失敗: {e}")
    
    def _safe_update_progress_text(self, text):
        """安全地更新進度文字"""
        try:
            if hasattr(self, '_progress_label') and self._progress_label:
                self.root.after(0, lambda: self._progress_label.config(text=text))
        except Exception as e:
            print(f"更新進度文字失敗: {e}")
