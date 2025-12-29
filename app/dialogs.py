import tkinter as tk
from tkinter import messagebox
import os

def show_mixed_content_dialog(parent, archives, log_count, folder_path):
    """
    美化版：顯示混合內容選擇對話框 (白底、字體綁定)
    """
    import ttkbootstrap as tb
    from ttkbootstrap.constants import SUCCESS, INFO, SECONDARY, DANGER, PRIMARY
    
    # 獲取字體大小
    ui_font_size = 12
    if hasattr(parent, 'settings'):
        ui_font_size = parent.settings.get('ui_font_size', 12)
    
    dialog = tb.Toplevel(parent)
    dialog.title("發現混合內容 - 請選擇操作")
    dialog.configure(bg='white')
    
    # 根據字體調整視窗大小
    win_w = int(650 * (ui_font_size / 12))
    win_h = int(550 * (ui_font_size / 12))
    
    dialog.transient(parent)
    dialog.grab_set()
    
    # 居中
    parent_x = parent.winfo_rootx()
    parent_y = parent.winfo_rooty()
    parent_w = parent.winfo_width()
    parent_h = parent.winfo_height()
    x = parent_x + (parent_w - win_w) // 2
    y = parent_y + (parent_h - win_h) // 2
    dialog.geometry(f"{win_w}x{win_h}+{x}+{y}")
    
    result = {'action': 'cancel', 'selected': []}
    
    # 主容器
    main_frame = tb.Frame(dialog, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    main_frame.configure(style='light.TFrame') # 使用 light 樣式基礎
    
    # 標題區
    header = tb.Frame(main_frame, background='white')
    header.pack(fill=tk.X, pady=(0, 15))
    
    msg = f"📂 資料夾：{os.path.basename(folder_path)}\n"
    msg += f"• 發現 {len(archives)} 個 壓縮檔案 (.zip/.7z/.rar)\n"
    msg += f"• 發現 {log_count} 個 Log 檔案"
    
    tb.Label(header, text=msg, font=('Microsoft JhengHei', ui_font_size, 'bold'), 
             background='white', justify=tk.LEFT).pack(anchor='w')
    
    tb.Label(header, text="請檢視並勾選要處理的壓縮檔：", font=('Microsoft JhengHei', ui_font_size - 1),
             foreground='#666', background='white').pack(anchor='w', pady=(10, 0))
    
    # 列表區 (卡片式)
    list_frame = tb.Frame(main_frame, relief=tk.SOLID, borderwidth=1)
    list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    canvas = tk.Canvas(list_frame, bg='white', highlightthickness=0)
    scrollbar = tb.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
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
                                 bg='white', font=('Microsoft JhengHei', ui_font_size - 1),
                                 anchor='w', cursor='hand2')
        chk.pack(fill=tk.X, padx=10, pady=3)
        vars_.append((var, p))
        
    # 按鈕區
    btn_frame = tb.Frame(main_frame, background='white', pady=15)
    btn_frame.pack(fill=tk.X)
    
    # 左側：全選/全不選
    def check_all(val):
        for v, _ in vars_: v.set(val)
            
    left_btns = tb.Frame(btn_frame, background='white')
    left_btns.pack(side=tk.LEFT)
    tb.Button(left_btns, text="全選", command=lambda: check_all(True), 
              bootstyle=SECONDARY, width=8).pack(side=tk.LEFT, padx=2)
    tb.Button(left_btns, text="全不選", command=lambda: check_all(False), 
              bootstyle=SECONDARY, width=8).pack(side=tk.LEFT, padx=2)
    
    # 右側：操作按鈕
    right_btns = tb.Frame(btn_frame, background='white')
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
        
    # 處理壓縮檔
    btn_proc_arc = tb.Button(right_btns, text=" 處理選中內容 ", command=on_archives, 
                            bootstyle=SUCCESS, padding=(15, 8))
    btn_proc_arc.pack(side=tk.LEFT, padx=5)
    
    if log_count > 0:
        btn_proc_log = tb.Button(right_btns, text=" 僅處理 LOG ", command=on_logs,
                                bootstyle=INFO, padding=(10, 8))
        btn_proc_log.pack(side=tk.LEFT, padx=5)
        
    tb.Button(right_btns, text=" 取 消 ", command=on_cancel, 
              bootstyle=SECONDARY, padding=(10, 8)).pack(side=tk.LEFT, padx=5)
    
    dialog.protocol("WM_DELETE_WINDOW", on_cancel)
    dialog.wait_window()
    return result

def show_smart_select_dialog(parent, selected_files, folder_path):
    """
    智慧選擇確認對話框 - 美化版
    """
    import ttkbootstrap as tb
    from ttkbootstrap.constants import SUCCESS, INFO, SECONDARY, PRIMARY
    
    ui_font_size = 12
    if hasattr(parent, 'settings'):
        ui_font_size = parent.settings.get('ui_font_size', 12)
        
    dialog = tb.Toplevel(parent)
    dialog.title("選擇操作")
    dialog.configure(bg='white')
    
    win_w = int(500 * (ui_font_size / 12))
    win_h = int(280 * (ui_font_size / 12))
    
    dialog.transient(parent)
    dialog.grab_set()
    
    # 居中
    parent_x = parent.winfo_rootx()
    parent_y = parent.winfo_rooty()
    parent_w = parent.winfo_width()
    parent_h = parent.winfo_height()
    x = parent_x + (parent_w - win_w) // 2
    y = parent_y + (parent_h - win_h) // 2
    dialog.geometry(f"{win_w}x{win_h}+{x}+{y}")
    
    action = 'cancel'
    
    main_frame = tb.Frame(dialog, padding=25)
    main_frame.pack(fill=tk.BOTH, expand=True)
    main_frame.configure(style='light.TFrame')
    
    tb.Label(main_frame, text="❓ 您已選取檔案，要執行哪種操作？", 
             font=('Microsoft JhengHei', ui_font_size, 'bold'), 
             background='white').pack(pady=(0, 15))
    
    # 資訊卡片
    info_box = tb.Frame(main_frame, padding=15, relief=tk.SOLID, borderwidth=1)
    info_box.pack(fill=tk.X, pady=5)
    info_box.configure(background='#F8F9FA')
    
    file_msg = f"已選取: {len(selected_files)} 個檔案"
    if len(selected_files) == 1:
        file_msg += f" ({os.path.basename(selected_files[0])})"
    tb.Label(info_box, text=f"📄 {file_msg}", font=('Microsoft JhengHei', ui_font_size - 1),
             foreground='#555', background='#F8F9FA').pack(anchor='w')
    
    folder_msg = f"所在資料夾: {os.path.basename(folder_path)}"
    tb.Label(info_box, text=f"📂 {folder_msg}", font=('Microsoft JhengHei', ui_font_size - 1),
             foreground='#555', background='#F8F9FA').pack(anchor='w', pady=(5, 0))
    
    # 按鈕
    btn_frame = tb.Frame(main_frame, background='white', pady=20)
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

    tb.Button(btn_frame, text=" 僅處理選定檔案 ", command=on_files, 
             bootstyle=INFO, width=18, padding=10).pack(side=tk.LEFT, padx=10, expand=True)
             
    tb.Button(btn_frame, text=" 掃描整個資料夾 ", command=on_folder,
             bootstyle=SUCCESS, width=18, padding=10).pack(side=tk.LEFT, padx=10, expand=True)
    
    dialog.protocol("WM_DELETE_WINDOW", on_close)
    dialog.wait_window()
    return action
