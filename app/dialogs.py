import tkinter as tk
from tkinter import messagebox
import os

def show_mixed_content_dialog(parent, archives, log_count, folder_path):
    """
    顯示混合內容選擇對話框
    :param parent: 父視窗
    :param archives: 壓縮檔路徑清單
    :param log_count: LOG檔案數量
    :param folder_path: 資料夾路徑
    :return: (action, selected_archives)
             action: 'process_archives', 'process_logs', 'cancel'
             selected_archives: List of selected archive paths (if action is 'process_archives')
    """
    dialog = tk.Toplevel(parent)
    dialog.title("發現混合內容 - 請選擇操作")
    dialog.geometry("600x500")
    dialog.transient(parent)
    dialog.grab_set()
    
    # 居中
    parent_x = parent.winfo_rootx()
    parent_y = parent.winfo_rooty()
    parent_w = parent.winfo_width()
    parent_h = parent.winfo_height()
    x = parent_x + (parent_w - 600) // 2
    y = parent_y + (parent_h - 500) // 2
    dialog.geometry(f"+{x}+{y}")
    
    result = {'action': 'cancel', 'selected': []}
    
    # 標題區
    header_frame = tk.Frame(dialog, pady=10, padx=10)
    header_frame.pack(fill=tk.X)
    
    msg = f"在資料夾中發現：\n• {len(archives)} 個 壓縮檔案 (.zip/.7z/.rar)\n• {log_count} 個 Log 檔案"
    tk.Label(header_frame, text=msg, font=('Arial', 11, 'bold'), justify=tk.LEFT).pack(anchor='w')
    
    tk.Label(header_frame, text="請檢視下方的壓縮檔案列表，並選擇操作：", pady=5).pack(anchor='w')
    
    # 列表區
    list_frame = tk.Frame(dialog, padx=10)
    list_frame.pack(fill=tk.BOTH, expand=True)
    
    canvas = tk.Canvas(list_frame, bg='white', bd=1, relief=tk.SUNKEN)
    scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
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
        # 顯示相對路徑或檔名
        display_name = os.path.basename(p)
        chk = tk.Checkbutton(scrollable_frame, text=display_name, variable=var, bg='white', anchor='w')
        chk.pack(fill=tk.X, padx=5, pady=2)
        vars_.append((var, p))
        
    # 按鈕區
    btn_frame = tk.Frame(dialog, pady=15, padx=10)
    btn_frame.pack(fill=tk.X)
    
    # 左側：全選/全不選
    def check_all(val):
        for v, _ in vars_:
            v.set(val)
            
    left_btns = tk.Frame(btn_frame)
    left_btns.pack(side=tk.LEFT)
    tk.Button(left_btns, text="全選", command=lambda: check_all(True)).pack(side=tk.LEFT, padx=2)
    tk.Button(left_btns, text="全不選", command=lambda: check_all(False)).pack(side=tk.LEFT, padx=2)
    
    # 右側：操作按鈕
    right_btns = tk.Frame(btn_frame)
    right_btns.pack(side=tk.RIGHT)
    
    def on_archives():
        selected = [p for v, p in vars_ if v.get()]
        if not selected:
            messagebox.showwarning("提示", "請至少選擇一個壓縮檔案", parent=dialog)
            return
        result['action'] = 'process_archives'
        result['selected'] = selected
        try:
            dialog.grab_release()
        except:
            pass
        dialog.destroy()
        
    def on_logs():
        if log_count == 0:
            messagebox.showinfo("提示", "此資料夾中沒有直接的 Log 檔案", parent=dialog)
            return
        result['action'] = 'process_logs'
        try:
            dialog.grab_release()
        except:
            pass
        dialog.destroy()
        
    def on_cancel():
        try:
            dialog.grab_release()
        except:
            pass
        dialog.destroy()
        
    # 處理壓縮檔按鈕 (主要動作)
    btn_proc_arc = tk.Button(right_btns, text="處理選中的壓縮檔", command=on_archives, 
                            bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'), padx=10)
    btn_proc_arc.pack(side=tk.LEFT, padx=5)
    
    # 處理Log按鈕 (如果有Log)
    if log_count > 0:
        btn_proc_log = tk.Button(right_btns, text="僅處理 Log 檔案", command=on_logs,
                                bg='#2196F3', fg='white', font=('Arial', 10))
        btn_proc_log.pack(side=tk.LEFT, padx=5)
        
    # 取消按鈕
    tk.Button(right_btns, text="取消", command=on_cancel).pack(side=tk.LEFT, padx=5)
    
    # 綁定視窗關閉事件
    dialog.protocol("WM_DELETE_WINDOW", on_cancel)
    
    dialog.wait_window()
    return result

def show_smart_select_dialog(parent, selected_files, folder_path):
    """
    顯示智慧選擇確認對話框
    :param parent: 父視窗
    :param selected_files: 已選取的檔案列表
    :param folder_path: 所在資料夾
    :return: 'files' 或 'folder' 或 'cancel'
    """
    dialog = tk.Toplevel(parent)
    dialog.title("選擇操作")
    dialog.geometry("450x220")
    dialog.transient(parent)
    dialog.grab_set()
    
    # 居中
    parent_x = parent.winfo_rootx()
    parent_y = parent.winfo_rooty()
    parent_w = parent.winfo_width()
    parent_h = parent.winfo_height()
    x = parent_x + (parent_w - 450) // 2
    y = parent_y + (parent_h - 220) // 2
    dialog.geometry(f"+{x}+{y}")
    
    action = 'cancel'
    
    tk.Label(dialog, text="您已選取檔案，請問要執行哪種操作？", font=('Arial', 11, 'bold'), pady=15).pack()
    
    # 資訊
    info_frame = tk.Frame(dialog)
    info_frame.pack(fill=tk.X, padx=20)
    
    file_msg = f"已選取: {len(selected_files)} 個檔案"
    if len(selected_files) == 1:
        file_msg += f" ({os.path.basename(selected_files[0])})"
    tk.Label(info_frame, text=file_msg, anchor='w', fg='#555').pack(fill=tk.X)
    
    folder_msg = f"所在資料夾: {os.path.basename(folder_path)}"
    tk.Label(info_frame, text=folder_msg, anchor='w', fg='#555').pack(fill=tk.X)
    
    # 按鈕
    btn_frame = tk.Frame(dialog, pady=20)
    btn_frame.pack()
    
    def on_files():
        nonlocal action
        action = 'files'
        try:
            dialog.grab_release()
        except:
            pass
        dialog.destroy()
        
    def on_folder():
        nonlocal action
        action = 'folder'
        try:
            dialog.grab_release()
        except:
            pass
        dialog.destroy()
    
    def on_close():
        """處理視窗關閉事件"""
        try:
            dialog.grab_release()
        except:
            pass
        dialog.destroy()

    tk.Button(btn_frame, text="僅處理選定檔案", command=on_files, 
             bg='#2196F3', fg='white', font=('Arial', 10), width=15).pack(side=tk.LEFT, padx=10)
             
    tk.Button(btn_frame, text="掃描整個資料夾", command=on_folder,
             bg='#4CAF50', fg='white', font=('Arial', 10), width=15).pack(side=tk.LEFT, padx=10)
    
    # 綁定視窗關閉事件
    dialog.protocol("WM_DELETE_WINDOW", on_close)
             
    dialog.wait_window()
    return action
