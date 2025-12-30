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
