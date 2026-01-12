import tkinter as tk
from tkinter import messagebox
import os

def show_mixed_content_dialog(parent, archives, log_count, folder_path):
    """
    修正版：解決白底一片白問題。使用標準 tk 元件確保可見度。
    """
    import tkinter as tk
    from tkinter import ttk, messagebox
    
    # 獲取字體大小
    ui_font_size = 12
    if hasattr(parent, 'settings'):
        ui_font_size = parent.settings.get('ui_font_size', 12)
    
    # 🟢 改用標準 tk.Toplevel 以確保在所有環境下的渲染穩定性
    dialog = tk.Toplevel(parent)
    dialog.title("發現混合內容 - 請選擇操作")
    dialog.configure(bg='white')
    
    # 根據字體調整視窗大小 (增加更多寬裕空間)
    win_w = int(750 * (ui_font_size / 12))
    win_h = int(680 * (ui_font_size / 12))
    
    dialog.transient(parent)
    dialog.attributes("-topmost", True)  # 🟢 強制最上層
    dialog.grab_set()
    
    # 居中
    try:
        dialog.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        x = parent_x + (parent_w - win_w) // 2
        y = parent_y + (parent_h - win_h) // 2
        dialog.geometry(f"{win_w}x{win_h}+{x}+{y}")
    except:
        dialog.geometry(f"{win_w}x{win_h}")
    
    result = {'action': 'cancel', 'selected': []}
    
    # 🟢 主要容器使用標準 tk.Frame
    main_frame = tk.Frame(dialog, bg='white', padx=25, pady=25)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 標題區
    header = tk.Frame(main_frame, bg='white')
    header.pack(fill=tk.X, pady=(0, 15))
    
    msg = f"📂 資料夾：{os.path.basename(folder_path)}\n"
    msg += f"• 發現 {len(archives)} 個 壓縮檔案 (.zip/.7z/.rar)\n"
    msg += f"• 發現 {log_count} 個 Log 檔案"
    
    tk.Label(header, text=msg, font=('Microsoft JhengHei', ui_font_size, 'bold'), 
             bg='white', fg='#333', justify=tk.LEFT).pack(anchor='w')
    
    tk.Label(header, text="請檢視並勾選要處理的壓縮檔：", font=('Microsoft JhengHei', ui_font_size - 1),
             fg='#666', bg='white').pack(anchor='w', pady=(10, 0))
    
    # 🟢 按鈕區 (Pack at the bottom of main_frame FIRST)
    btn_frame = tk.Frame(main_frame, bg='white', pady=15)
    btn_frame.pack(side=tk.BOTTOM, fill=tk.X)
    
    # 列表區 (卡片式) - Pack after buttons to take remaining space
    list_frame = tk.Frame(main_frame, bg='white', relief=tk.SOLID, borderwidth=1)
    list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    canvas = tk.Canvas(list_frame, bg='white', highlightthickness=0)
    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg='white')
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # 填充列表
    vars_ = []
    for p in sorted(archives):
        var = tk.BooleanVar(value=True)
        display_name = os.path.basename(p)
        chk = tk.Checkbutton(scrollable_frame, text=f" 📦 {display_name}", variable=var, 
                                 bg='white', activebackground='white',
                                 font=('Microsoft JhengHei', ui_font_size - 1),
                                 anchor='w', cursor='hand2')
        chk.pack(fill=tk.X, padx=10, pady=3)
        vars_.append((var, p))
        
    # 左側：全選/全不選
    def check_all(val):
        for v, _ in vars_: v.set(val)
            
    left_btns = tk.Frame(btn_frame, bg='white')
    left_btns.pack(side=tk.LEFT)
    
    tk.Button(left_btns, text=" 全選 ", command=lambda: check_all(True), 
              bg='#f0f0f0', font=('Microsoft JhengHei', ui_font_size - 2)).pack(side=tk.LEFT, padx=2)
    tk.Button(left_btns, text=" 全不選 ", command=lambda: check_all(False), 
              bg='#f0f0f0', font=('Microsoft JhengHei', ui_font_size - 2)).pack(side=tk.LEFT, padx=2)
    
    # 右側：操作按鈕
    right_btns = tk.Frame(btn_frame, bg='white')
    right_btns.pack(side=tk.RIGHT)
    
    def on_archives():
        selected = [p for v, p in vars_ if v.get()]
        if not selected:
            messagebox.showwarning("提示", "請至少選擇一個壓縮檔案", parent=dialog)
            return
        result['action'] = 'process_archives'
        result['selected'] = selected
        dialog.destroy()
        
    def on_logs():
        if log_count == 0:
            messagebox.showinfo("提示", "此資料夾中沒有直接的 Log 檔案", parent=dialog)
            return
        result['action'] = 'process_logs'
        dialog.destroy()
        
    def on_cancel():
        result['action'] = 'cancel'
        dialog.destroy()
        
    # 🔵 處理壓縮檔按鈕 - 使用標準 tk 按鈕並設定顏色模擬 ttkbootstrap
    btn_proc_arc = tk.Button(right_btns, text=" 🚀 處理選中的壓縮檔 ", command=on_archives, 
                            bg='#2E7D32', fg='white', font=('Microsoft JhengHei', ui_font_size - 1, 'bold'),
                            padx=15, pady=8, cursor='hand2')
    btn_proc_arc.pack(side=tk.LEFT, padx=5)
    
    if log_count > 0:
        btn_proc_log = tk.Button(right_btns, text=" 📄 僅處理 LOG ", command=on_logs,
                                bg='#1565C0', fg='white', font=('Microsoft JhengHei', ui_font_size - 1),
                                padx=10, pady=8, cursor='hand2')
        btn_proc_log.pack(side=tk.LEFT, padx=5)
        
    tk.Button(right_btns, text=" 取 消 ", command=on_cancel, 
              bg='#757575', fg='white', font=('Microsoft JhengHei', ui_font_size - 1),
              padx=10, pady=8, cursor='hand2').pack(side=tk.LEFT, padx=5)
    
    dialog.protocol("WM_DELETE_WINDOW", on_cancel)
    dialog.wait_window()
    return result

def show_smart_select_dialog(parent, selected_files, folder_path):
    """
    智慧選擇確認對話框 - 修正版
    """
    import tkinter as tk
    
    ui_font_size = 12
    if hasattr(parent, 'settings'):
        ui_font_size = parent.settings.get('ui_font_size', 12)
        
    dialog = tk.Toplevel(parent)
    dialog.title("選擇操作")
    dialog.configure(bg='white')
    
    win_w = int(550 * (ui_font_size / 12))
    win_h = int(320 * (ui_font_size / 12))
    
    dialog.transient(parent)
    dialog.attributes("-topmost", True)  # 🟢 強制最上層
    dialog.grab_set()
    
    # 居中
    try:
        dialog.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        x = parent_x + (parent_w - win_w) // 2
        y = parent_y + (parent_h - win_h) // 2
        dialog.geometry(f"{win_w}x{win_h}+{x}+{y}")
    except:
        dialog.geometry(f"{win_w}x{win_h}")
    
    action = 'cancel'
    
    main_frame = tk.Frame(dialog, bg='white', padx=30, pady=30)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    tk.Label(main_frame, text="❓ 您已選取檔案，要執行哪種操作？", 
             font=('Microsoft JhengHei', ui_font_size, 'bold'), 
             bg='white', fg='#333').pack(pady=(0, 20))
    
    # 資訊卡片
    info_box = tk.Frame(main_frame, bg='#F8F9FA', padx=20, pady=15, relief=tk.SOLID, borderwidth=1)
    info_box.pack(fill=tk.X, pady=5)
    
    file_msg = f"已選取: {len(selected_files)} 個檔案"
    if len(selected_files) == 1:
        file_msg += f" ({os.path.basename(selected_files[0])})"
    tk.Label(info_box, text=f"📄 {file_msg}", font=('Microsoft JhengHei', ui_font_size - 1),
             fg='#555', bg='#F8F9FA').pack(anchor='w')
    
    folder_msg = f"所在資料夾: {os.path.basename(folder_path)}"
    tk.Label(info_box, text=f"📂 {folder_msg}", font=('Microsoft JhengHei', ui_font_size - 1),
             fg='#555', bg='#F8F9FA').pack(anchor='w', pady=(5, 0))
    
    # 按鈕
    btn_frame = tk.Frame(main_frame, bg='white', pady=25)
    btn_frame.pack(side=tk.BOTTOM, fill=tk.X)
    
    def on_files():
        nonlocal action
        action = 'files'
        dialog.destroy()
        
    def on_folder():
        nonlocal action
        action = 'folder'
        dialog.destroy()
    
    def on_close():
        dialog.destroy()

    tk.Button(btn_frame, text=" 僅處理選定檔案 ", command=on_files, 
             bg='#1565C0', fg='white', font=('Microsoft JhengHei', ui_font_size - 1, 'bold'),
             width=20, pady=10, cursor='hand2').pack(side=tk.LEFT, padx=10, expand=True)
             
    tk.Button(btn_frame, text=" 掃描整個資料夾 ", command=on_folder,
             bg='#2E7D32', fg='white', font=('Microsoft JhengHei', ui_font_size - 1, 'bold'),
             width=20, pady=10, cursor='hand2').pack(side=tk.LEFT, padx=10, expand=True)
    
    dialog.protocol("WM_DELETE_WINDOW", on_close)
    dialog.wait_window()
    return action

def show_image_results(parent, image_list, isn):
    """
    顯示圖片檢索結果對話框 (User Requested)
    """
    print(f"DEBUG: show_image_results called for ISN: {isn}")
    try:
        import tkinter as tk
        from tkinter import ttk
        import os
        import datetime
        
        # 🟢 建立「獨立」的視窗（不傳入 parent），使其在工作列有自己的按鈕，這能解決「縮小按鈕沒反應」的問題
        dialog = tk.Toplevel() 
        dialog.title(f"圖片檢索結果 - {isn}")
        dialog.configure(bg='white')
        
        ui_font_size = 12
        if hasattr(parent, 'settings'):
            ui_font_size = parent.settings.get('ui_font_size', 12)
            
        win_w = int(900 * (ui_font_size / 12))
        win_h = int(600 * (ui_font_size / 12))
        
        # 設置視窗屬性為「正常視窗」，確保縮小功能可用
        dialog.transient("") 
        dialog.attributes("-topmost", False)
        dialog.resizable(True, True)
        
        # 居中計算 (使用傳入的 parent 做參考點)
        try:
            dialog.update_idletasks()
            master = parent.root if hasattr(parent, 'root') else parent
            parent_x = master.winfo_rootx()
            parent_y = master.winfo_rooty()
            parent_w = master.winfo_width()
            parent_h = master.winfo_height()
            x = parent_x + (parent_w - win_w) // 2
            y = parent_y + (parent_h - win_h) // 2
            dialog.geometry(f"{win_w}x{win_h}+{x}+{y}")
        except:
            dialog.geometry(f"{win_w}x{win_h}")
            
        dialog.deiconify()
        # 🟢 重要：彻底移除 grab_set()，避免卡住
        
        print("DEBUG: Setting up window components...")
        main_frame = tk.Frame(dialog, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 標題
        header = tk.Label(main_frame, text=f"🔍 找到 {len(image_list)} 個與 ISN '{isn}' 相關的項目", 
                         font=('Microsoft JhengHei', ui_font_size, 'bold'), 
                         bg='white', fg='#1565C0')
        header.pack(anchor='w', pady=(0, 10))
        
        # 列表區
        list_frame = tk.Frame(main_frame, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("filename", "date", "size")
        # 🟢 使用 tree headings，第一欄放資料夾/ISN
        tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', selectmode='browse')
        
        tree.heading("#0", text=" 來源目錄 / ISN ")
        tree.heading("filename", text="檔案名稱")
        tree.heading("date", text="修改日期")
        tree.heading("size", text="大小")
        
        tree.column("#0", width=int(250 * (ui_font_size / 12)), anchor='w')
        tree.column("filename", width=int(300 * (ui_font_size / 12)), anchor='w')
        tree.column("date", width=int(150 * (ui_font_size / 12)), anchor='center')
        tree.column("size", width=int(80 * (ui_font_size / 12)), anchor='e')
        
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 🟢 路徑詳情區 (對接使用者要求：完整顯示、可折行)
        path_detail_frame = tk.LabelFrame(main_frame, text=" 完整來源路徑 (Full Path) ", 
                                         font=('Microsoft JhengHei', ui_font_size - 2),
                                         bg='white', fg='#555', pady=5)
        path_detail_frame.pack(fill=tk.X, pady=(10, 0))
        
        path_text = tk.Text(path_detail_frame, height=2, font=('Consolas', ui_font_size - 2),
                           bg='#F9F9F9', relief=tk.FLAT, padx=10, pady=5)
        path_text.pack(fill=tk.X)
        path_text.insert("1.0", "請點選下方項目以查看完整路徑...")
        path_text.config(state=tk.DISABLED)
        
        print(f"DEBUG: Categorizing and filling Treeview with {len(image_list)} items...")
        
        # 🟢 智慧分組：智慧識別 ISN 根目錄，將同一個搜尋標的可視為一組
        groups = {}
        for p in image_list:
            p_norm = os.path.normpath(p)
            
            # 找到包含 isn 的那一層目錄作為組名 (若無則用 dirname)
            # 例如: STATION_RECORD/0306250012+2025.../4cam/file.jpg -> Group: 0306250012...
            parts = p_norm.split(os.sep)
            grp_name = os.path.dirname(p_norm) # 預設預設分組
            
            # 從根部往回找第一個包含 isn 的資料夾
            isn_key = isn.split(',')[0].strip() # 取第一個 ISN 做關鍵字
            for i in range(len(parts)):
                if isn_key.lower() in parts[i].lower() and parts[i].lower() != "station_record":
                    grp_name = os.sep.join(parts[:i+1])
                    break
            
            if grp_name not in groups: groups[grp_name] = []
            groups[grp_name].append(p_norm)
            
        # 填充數據 (依字母排序目錄)
        for group_path in sorted(groups.keys()):
            files = groups[group_path]
            # 建立父節點 (顯示 ISN 資料夾名稱)
            display_name = os.path.basename(group_path)
            if not display_name: display_name = group_path
            
            folder_node = tree.insert("", tk.END, text=f"📂 {display_name}", open=True, values=("", "", ""))
            
            for p in sorted(files):
                try:
                    stats = os.stat(p)
                    dt = datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M')
                    size_kb = f"{stats.st_size / 1024:.1f} KB"
                    # 多顯示一級目錄以便區分 (如果檔名重複)
                    rel_p = os.path.relpath(p, group_path)
                    tree.insert(folder_node, tk.END, text="", values=(rel_p, dt, size_kb), tags=(p,))
                except:
                    tree.insert(folder_node, tk.END, text="", values=(os.path.basename(p), "Unknown", "Unknown"), tags=(p,))
                
        def update_path_detail(event):
            selected = tree.selection()
            if not selected: return
            item = tree.item(selected[0])
            tags = item.get('tags', [])
            
            path_text.config(state=tk.NORMAL)
            path_text.delete("1.0", tk.END)
            if tags:
                path_text.insert("1.0", os.path.normpath(tags[0]))
            else:
                # 節點選取：藉由 text 找回完整的 group_path
                current_text = item['text']
                for gp in groups.keys():
                    if f"📂 {os.path.basename(gp)}" == current_text:
                        path_text.insert("1.0", os.path.normpath(gp))
                        break
            path_text.config(state=tk.DISABLED)

        tree.bind("<<TreeviewSelect>>", update_path_detail)

        # 操作按鈕
        btn_frame = tk.Frame(main_frame, bg='white', pady=15)
        btn_frame.pack(fill=tk.X)
        
        def on_open_file():
            """更改為：開啟同一個目錄下的所有相關圖片 (增強穩定性)"""
            try:
                selected = tree.selection()
                if not selected:
                    messagebox.showinfo("提示", "請先選擇清單中的一個項目", parent=dialog)
                    return
                
                item_id = selected[0]
                item_data = tree.item(item_id)
                tags = item_data.get('tags', [])
                
                target_images = []
                # 判定所在資料夾節點
                folder_node = tree.parent(item_id) if tags else item_id
                
                if not folder_node:
                    # 如果沒有父節點，說明本身就在根部 (理論上在此分組模式不應發生)
                    if tags: target_images.append(tags[0])
                else:
                    children = tree.get_children(folder_node)
                    print(f"DEBUG: Found folder node {folder_node} with {len(children)} children")
                    for child in children:
                        child_tags = tree.item(child).get('tags', [])
                        if child_tags:
                            target_images.append(os.path.normpath(child_tags[0]))
                
                if not target_images:
                    messagebox.showwarning("提示", "找不到可開啟的相關圖片", parent=dialog)
                    return
                
                print(f"DEBUG: Preparing to open {len(target_images)} images: {target_images}")
                
                # 🟢 分組開啟數量提醒
                if len(target_images) > 1 :
                    # 如果超過一張，告知即將開啟的數量
                    msg = f"即將同時開啟同資料夾內的 {len(target_images)} 個影像檔案。\n確定要繼續？"
                    if len(target_images) > 10:
                        if not messagebox.askyesno("警告", msg, parent=dialog):
                            return
                
                import time
                for idx, img_path in enumerate(target_images):
                    if os.path.exists(img_path):
                        print(f"DEBUG: Opening ({idx+1}/{len(target_images)}): {img_path}")
                        os.startfile(img_path)
                        # 🟢 增加微小延遲 (0.2s)，防止 Windows 相片檢視器合併視窗或遺漏指令
                        if len(target_images) > 1:
                            time.sleep(0.2)
                    else:
                        print(f"DEBUG: File not found: {img_path}")
                        
            except Exception as e:
                import traceback
                traceback.print_exc()
                messagebox.showerror("錯誤", f"批次開啟失敗: {e}", parent=dialog)
                
        def on_open_folder():
            try:
                selected = tree.selection()
                if not selected:
                    messagebox.showinfo("提示", "請先選擇一個項目", parent=dialog)
                    return
                item_id = selected[0]
                item_data = tree.item(item_id)
                tags = item_data.get('tags', [])
                
                if tags:
                    file_path = os.path.normpath(tags[0])
                    # Windows 特有：開啟資料夾並選中檔案
                    import subprocess
                    subprocess.run(['explorer', '/select,', file_path])
                else:
                    # 選到資料夾節點
                    target_folder = ""
                    for fld in groups.keys():
                        if f"📂 {os.path.basename(fld)}" == item_data['text']:
                            target_folder = fld
                            break
                    if target_folder and os.path.exists(target_folder):
                        os.startfile(target_folder)
                    else:
                        messagebox.showerror("錯誤", "資料夾不存在", parent=dialog)
            except Exception as e:
                messagebox.showerror("錯誤", f"無法開啟資料夾: {e}", parent=dialog)
    
        # 使用 ttk.Button 以獲取更好的外觀與相容性
        style = ttk.Style()
        style.configure('Action.TButton', font=('Microsoft JhengHei', ui_font_size - 1, 'bold'))
        
        btn_open = ttk.Button(btn_frame, text=" 🖼️ 批次開啟同目錄圖片 ", command=on_open_file, style='Action.TButton')
        btn_open.pack(side=tk.LEFT, padx=5)
                 
        btn_fold = ttk.Button(btn_frame, text=" 📂 開啟資料夾 ", command=on_open_folder)
        btn_fold.pack(side=tk.LEFT, padx=5)
                 
        btn_close = ttk.Button(btn_frame, text=" 關閉 ", command=dialog.destroy)
        btn_close.pack(side=tk.RIGHT, padx=5)
                 
        # 雙擊單一圖片則維持：只開啟該張
        def on_double_click(event):
            selected = tree.selection()
            if not selected: return
            tags = tree.item(selected[0]).get('tags', [])
            if tags and os.path.exists(tags[0]):
                os.startfile(tags[0])
        
        tree.bind("<Double-1>", on_double_click)
        
        # 🟢 最後才進行 grab，確保所有元件已載入
        print("DEBUG: Window setup complete, grabbing focus...")
        dialog.grab_set()
        dialog.wait_window()
    except Exception as e:
        print(f"CRITICAL: show_image_results failed: {e}")
        import traceback
        traceback.print_exc()
        messagebox.showerror("UI錯誤", f"無法開啟結果視窗: {e}")
