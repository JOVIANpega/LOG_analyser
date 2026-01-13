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

def show_image_results(parent, image_list, isn, test_start_dt=None, test_end_dt=None):
    """
    顯示圖片檢索結果對話框 (增強版：具備智能時間比對與預覽功能)
    """
    print(f"DEBUG: show_image_results called for ISN: {isn}, Time: {test_start_dt} to {test_end_dt}")
    try:
        import tkinter as tk
        from tkinter import ttk
        import os
        import datetime
        from PIL import Image, ImageTk
        
        style = ttk.Style()
        
        def _create_tooltip_simple(widget, text):
            def on_enter(event):
                if hasattr(widget, 'tooltip'): widget.tooltip.destroy()
                tooltip = tk.Toplevel()
                tooltip.wm_overrideredirect(True)
                tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
                label = tk.Label(tooltip, text=text, background="lightyellow", relief="solid", borderwidth=1, font=("Microsoft JhengHei", 9))
                label.pack()
                widget.tooltip = tooltip
            def on_leave(event):
                if hasattr(widget, 'tooltip'):
                    widget.tooltip.destroy()
                    del widget.tooltip
            def on_motion(event):
                if hasattr(widget, 'tooltip'):
                    widget.tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Motion>", on_motion)
            if isinstance(widget, (tk.Button, ttk.Button)):
                widget.bind("<Button-1>", lambda e: on_leave(e), add="+")

        # 🟢 新增：防止重複開啟視窗 (Singleton Pattern)
        if hasattr(parent, 'image_result_dialog') and parent.image_result_dialog and parent.image_result_dialog.winfo_exists():
            # 已有視窗，將其帶到最前面並嘗試更新標題 (或直接 Focus)
            parent.image_result_dialog.lift()
            parent.image_result_dialog.focus_force()
            parent.image_result_dialog.title(f"圖片檢索結果 - {isn}")
            # 注意：這裡由於 UI 結構較複雜，建議簡單點直接 destroy 舊的開新的，
            # 但使用者要求「不要再開新的」，我們採取「關閉舊的再開新的」確保資料更新且只有一個視窗
            parent.image_result_dialog.destroy()

        dialog = tk.Toplevel() 
        parent.image_result_dialog = dialog # 紀錄引用
        dialog.title(f"圖片檢索結果 - {isn}")
        dialog.configure(bg='white')
        
        ui_font_size = 12
        if hasattr(parent, 'settings'):
            ui_font_size = parent.settings.get('ui_font_size', 12)
            
        win_w = int(1250 * (ui_font_size / 12)) # 稍微加寬以容納預覽區
        win_h = int(800 * (ui_font_size / 12))
        
        dialog.transient("") 
        dialog.attributes("-topmost", False)
        dialog.resizable(True, True)
        
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
        
        main_frame = tk.Frame(dialog, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 標題與過濾區
        header_frame = tk.Frame(main_frame, bg='white')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_text = f"🔍 找到 {len(image_list)} 個相關項目"
        if test_start_dt:
            title_text += f" (Log時間: {test_start_dt.strftime('%H:%M:%S')})"
            
        header = tk.Label(header_frame, text=title_text, 
                         font=('Microsoft JhengHei', ui_font_size, 'bold'), 
                         bg='white', fg='#1565C0')
        header.pack(side=tk.LEFT)
        
        filter_frame = tk.Frame(header_frame, bg='white')
        filter_frame.pack(side=tk.RIGHT)
        
        # 時差比對勾選
        only_near_1h_var = tk.BooleanVar(value=True if test_start_dt else False)
        only_near_24h_var = tk.BooleanVar(value=False)
        
        def on_toggle_1h():
            if only_near_1h_var.get():
                only_near_24h_var.set(False)
            populate_tree(filter_var.get())
            
        def on_toggle_24h():
            if only_near_24h_var.get():
                only_near_1h_var.set(False)
            populate_tree(filter_var.get())
            
        chk_near_1h = ttk.Checkbutton(filter_frame, text="僅顯示當次 (±1h)", variable=only_near_1h_var, 
                                     command=on_toggle_1h, style='Toolbutton' if 'Toolbutton' in style.theme_names() else '')
        chk_near_1h.pack(side=tk.LEFT, padx=5)
        
        chk_near_24h = ttk.Checkbutton(filter_frame, text="擴大顯示 (±24h)", variable=only_near_24h_var, 
                                      command=on_toggle_24h, style='Toolbutton' if 'Toolbutton' in style.theme_names() else '')
        chk_near_24h.pack(side=tk.LEFT, padx=5)
        
        # 如果完全沒時間資訊，還是讓它能點，只是過濾時沒反應，這樣 user 不會覺得視窗壞了
        # 但我們可以顯示一個說明
        if not test_start_dt:
            _create_tooltip_simple(chk_near_1h, "Log 中未發現時間資訊，無法精確過濾")
            _create_tooltip_simple(chk_near_24h, "Log 中未發現時間資訊，無法精確過濾")

        tk.Label(filter_frame, text="篩選:", font=('Microsoft JhengHei', ui_font_size - 1), bg='white').pack(side=tk.LEFT, padx=5)
        filter_var = tk.StringVar()
        filter_entry = ttk.Entry(filter_frame, textvariable=filter_var, width=15)
        filter_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        # 🟢 中間主要區域：左邊清單，右邊預覽
        content_paned = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, bg='#EEE', sashwidth=4, bd=0)
        content_paned.pack(fill=tk.BOTH, expand=True)
        
        list_frame = tk.Frame(content_paned, bg='white')
        content_paned.add(list_frame, width=int(win_w * 0.65))
        
        # 預覽區
        preview_frame = tk.LabelFrame(content_paned, text=" 🌅 圖片預覽 (Selected Preview) ", 
                                     bg='white', fg='#333', font=('Microsoft JhengHei', ui_font_size - 2))
        content_paned.add(preview_frame)
        
        preview_label = tk.Label(preview_frame, text="請選擇圖片查看預覽", bg='#F5F5F5', fg='#999')
        preview_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("filename", "date", "offset", "size")
        tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', selectmode='browse')
        
        tree.heading("#0", text=" 來源目錄 / 分組 ")
        tree.heading("filename", text="檔案名稱")
        tree.heading("date", text="修改日期")
        tree.heading("offset", text="時差")
        tree.heading("size", text="大小")
        
        tree.column("#0", width=int(350 * (ui_font_size / 12)), anchor='w')
        tree.column("filename", width=int(220 * (ui_font_size / 12)), anchor='w')
        tree.column("date", width=int(140 * (ui_font_size / 12)), anchor='center')
        tree.column("offset", width=int(80 * (ui_font_size / 12)), anchor='center')
        tree.column("size", width=int(80 * (ui_font_size / 12)), anchor='e')
        
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 設定標記樣式
        tree.tag_configure("BEST_MATCH", foreground="blue", font=('Microsoft JhengHei', ui_font_size - 1, 'bold'))
        tree.tag_configure("FOLDER_MATCH", background="#E3F2FD") # 淺藍背景

        path_detail_frame = tk.LabelFrame(main_frame, text=" 完整來源路徑 (Full Path) ", 
                                         font=('Microsoft JhengHei', ui_font_size - 2),
                                         bg='white', fg='#555', pady=5)
        path_detail_frame.pack(fill=tk.X, pady=(10, 0))
        
        path_text = tk.Text(path_detail_frame, height=1, font=('Consolas', ui_font_size - 2),
                           bg='#F9F9F9', relief=tk.FLAT, padx=10, pady=5)
        path_text.pack(fill=tk.X)
        path_text.insert("1.0", "請點選下方項目以查看完整路徑...")
        path_text.config(state=tk.DISABLED)

        full_groups = {} 
        isn_key = isn.split(',')[0].strip()

        def _format_size(bytes_val):
            if bytes_val >= 1024 * 1024:
                return f"{bytes_val / (1024 * 1024):.2f} MB"
            return f"{bytes_val / 1024:.1f} KB"

        def _calculate_offset(img_mtime, ref_start, ref_end):
            if not ref_start: return ""
            ref_dt = ref_end if ref_end else ref_start
            img_dt = datetime.datetime.fromtimestamp(img_mtime)
            diff = img_dt - ref_dt
            
            secs = diff.total_seconds()
            abs_secs = abs(secs)
            
            if abs_secs < 60: return f"{int(secs)}s"
            if abs_secs < 3600: return f"{int(secs/60)}m"
            return f"{int(secs/3600)}h"

        def _get_group_name(p_norm):
            parts = p_norm.split(os.sep)
            for i in range(len(parts)):
                if isn_key.lower() in parts[i].lower() and parts[i].lower() != "station_record":
                    if i == len(parts) - 1:
                        return os.path.dirname(p_norm)
                    return os.sep.join(parts[:i+1])
            return os.path.dirname(p_norm)

        for p in image_list:
            p_norm = os.path.normpath(p)
            grp_name = _get_group_name(p_norm)
            if grp_name not in full_groups: full_groups[grp_name] = []
            full_groups[grp_name].append(p_norm)

        def populate_tree(keyword=""):
            for item in tree.get_children():
                tree.delete(item)
            
            keyword = keyword.lower().strip()
            item_count = 0
            best_match_nodes = []
            
            sorted_groups = sorted(full_groups.keys())
            
            for group_path in sorted_groups:
                files = full_groups[group_path]
                filtered_files = []
                group_has_best_match = False
                
                for p in files:
                    # 1. 條件搜尋
                    if keyword and keyword not in p.lower(): continue
                    
                    # 2. 時間過濾 (±24小時)
                    is_best = False
                    if test_start_dt:
                        stats = os.stat(p)
                        mtime_dt = datetime.datetime.fromtimestamp(stats.st_mtime)
                        # 最佳匹配：落於 [Start - 1m, End + 10m]
                        margin_start = test_start_dt - datetime.timedelta(minutes=1)
                        margin_end = (test_end_dt if test_end_dt else test_start_dt) + datetime.timedelta(minutes=10)
                        if margin_start <= mtime_dt <= margin_end:
                            is_best = True
                            group_has_best_match = True
                        
                        # 硬過濾 (若勾選僅顯示當次)
                        if only_near_1h_var.get():
                            diff_hours = abs((mtime_dt - (test_end_dt if test_end_dt else test_start_dt)).total_seconds() / 3600)
                            if diff_hours > 1.0: continue
                        elif only_near_24h_var.get():
                            diff_hours = abs((mtime_dt - (test_end_dt if test_end_dt else test_start_dt)).total_seconds() / 3600)
                            if diff_hours > 24.0: continue
                            
                    filtered_files.append((p, is_best))
                
                if not filtered_files: continue
                
                display_name = os.path.basename(group_path)
                if not display_name: display_name = group_path
                
                folder_tags = ["FOLDER", group_path]
                if group_has_best_match: folder_tags.append("FOLDER_MATCH")
                
                folder_node = tree.insert("", tk.END, text=f"📂 {display_name}", open=True if group_has_best_match else False, tags=tuple(folder_tags))
                
                for p, is_best in sorted(filtered_files):
                    try:
                        stats = os.stat(p)
                        dt_str = datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%y/%m/%d %H:%M')
                        offset_str = _calculate_offset(stats.st_mtime, test_start_dt, test_end_dt)
                        size_str = _format_size(stats.st_size)
                        fname = os.path.basename(p)
                        
                        file_tags = ["FILE", p]
                        if is_best: 
                            file_tags.append("BEST_MATCH")
                            
                        node = tree.insert(folder_node, tk.END, text="", values=(fname, dt_str, offset_str, size_str), tags=tuple(file_tags))
                        if is_best: best_match_nodes.append(node)
                        item_count += 1
                    except:
                        tree.insert(folder_node, tk.END, text="", values=(os.path.basename(p), "Err", "", ""), tags=("FILE", p))
                        item_count += 1
            
            header.config(text=f"🔍 找到 {item_count} 個項目 (時戳比對：{'✅ 啟用' if test_start_dt else '❌ 無效'})")
            
            # 自動選中第一個最佳匹配
            if best_match_nodes:
                tree.selection_set(best_match_nodes[0])
                tree.see(best_match_nodes[0])

        current_photo = None # 保持 PhotoImage 引用避免垃圾回收

        def update_preview(file_path):
            nonlocal current_photo
            try:
                # 載入圖片
                img = Image.open(file_path)
                
                # 簡單計算縮放比例
                pw = preview_label.winfo_width()
                ph = preview_label.winfo_height()
                if pw < 10: pw, ph = 400, 500 # fallback
                
                iw, ih = img.size
                ratio = min(pw/iw, ph/ih)
                new_w = max(10, int(iw * ratio * 0.9))
                new_h = max(10, int(ih * ratio * 0.9))
                
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                current_photo = ImageTk.PhotoImage(img)
                preview_label.config(image=current_photo, text="")
            except Exception as e:
                preview_label.config(image="", text=f"無法預覽圖片:\n{str(e)}")

        def on_selection_change(event):
            selected = tree.selection()
            if not selected: return
            item = tree.item(selected[0])
            tags = item.get('tags', [])
            
            path_text.config(state=tk.NORMAL)
            path_text.delete("1.0", tk.END)
            
            if tags and "FILE" in tags:
                file_path = tags[1]
                path_text.insert("1.0", os.path.normpath(file_path))
                update_preview(file_path)
            elif tags and "FOLDER" in tags:
                path_text.insert("1.0", os.path.normpath(tags[1]))
                preview_label.config(image="", text="請選擇單一圖片以預覽")
            
            path_text.config(state=tk.DISABLED)

        tree.bind("<<TreeviewSelect>>", on_selection_change)
        filter_var.trace_add("write", lambda *a: populate_tree(filter_var.get()))
        
        populate_tree() 

        # 按鈕區
        btn_frame = tk.Frame(main_frame, bg='white', pady=10)
        btn_frame.pack(fill=tk.X)
        
        style.configure('Action.TButton', font=('Microsoft JhengHei', ui_font_size - 1, 'bold'))
        
        def _get_target_images():
            selected = tree.selection()
            if not selected: return []
            item_id = selected[0]
            tags = tree.item(item_id).get('tags', [])
            
            if "FILE" in tags:
                # 找出同分組下的所有檔案
                folder_id = tree.parent(item_id)
                if folder_id:
                    imgs = []
                    for c in tree.get_children(folder_id):
                        c_tags = tree.item(c).get('tags', [])
                        if "FILE" in c_tags: imgs.append(c_tags[1])
                    return imgs
                return [tags[1]]
            elif "FOLDER" in tags:
                imgs = []
                for c in tree.get_children(item_id):
                    c_tags = tree.item(c).get('tags', [])
                    if "FILE" in c_tags: imgs.append(c_tags[1])
                return imgs
            return []

        def on_open_batch():
            imgs = _get_target_images()
            if not imgs: return
            if len(imgs) > 10 and not messagebox.askyesno("確認", f"即將開啟 {len(imgs)} 張圖片，確定？"): return
            for p in imgs:
                if os.path.exists(p): os.startfile(p)

        def on_copy_batch():
            imgs = _get_target_images()
            if not imgs: return
            from tkinter import filedialog
            import shutil
            dest = filedialog.askdirectory(title=f"將 {len(imgs)} 張圖複製到...")
            if not dest: return
            success = 0
            for p in imgs:
                try:
                    shutil.copy2(p, dest)
                    success += 1
                except: pass
            if success: 
                messagebox.showinfo("成功", f"已複製 {success} 個檔案")
                os.startfile(dest)

        ttk.Button(btn_frame, text=" 🖼️ 批次開啟同分組圖片 ", command=on_open_batch, style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=" 💾 複製整組圖片 ", command=on_copy_batch, style='Action.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=" 📁 開啟目錄 ", command=lambda: [p := _get_target_images(), os.startfile(os.path.dirname(p[0])) if p else None]).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=" 關閉 ", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)

        def on_double_click(event):
            sel = tree.selection()
            if not sel: return
            tags = tree.item(sel[0]).get('tags', [])
            if "FILE" in tags and os.path.exists(tags[1]): os.startfile(tags[1])

        tree.bind("<Double-1>", on_double_click)
        dialog.wait_window()

    except Exception as e:
        print(f"CRITICAL: show_image_results failed: {e}")
        import traceback
        traceback.print_exc()
        messagebox.showerror("UI錯誤", f"無法開啟結果視窗: {e}")
