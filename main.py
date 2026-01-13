#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試Log分析器GUI應用程式
提供現代化的圖形使用者介面來分析測試log檔案
僅啟動增強版模式
"""

import tkinter as tk
import sys
import os

def main():
    """主程式入口點（僅增強版）"""
    # 建立簡易日誌以診斷啟動問題
    import sys
    import os
    import traceback
    
    log_file = "startup_debug.log"
    try:
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("=== PEGA Log Analyzer Startup Debug ===\n")
            f.write(f"Working Dir: {os.getcwd()}\n")
            f.write(f"Executable: {sys.executable}\n")
    except:
        pass # 如果無法寫入日誌則忽略
    
    try:
        # 延遲載入 heavy 模組的預備
        from app.settings_loader import load_settings
        settings = load_settings()
        selected_theme = settings.get('theme', 'superhero')
        
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"Loaded Settings: {list(settings.keys())}\n")
                f.write(f"Selected Theme: {selected_theme}\n")
        except: pass
        
        import ttkbootstrap as ttk
        
        # 直接建立 ttk.Window 作為唯一的 root
        root = ttk.Window(
            title="PEGA Log Analyzer",
            themename=selected_theme,
            resizable=(True, True)
        )
        root.withdraw() # 初始隱藏，先做啟動畫面
        
        # 建立啟動畫面 (作為 Toplevel 或在 root 上佈置)
        splash_frame = ttk.Frame(root, style='secondary.TFrame')
        splash_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # 設定視窗大小與置中
        ww, wh = 450, 300
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        root.geometry(f"{ww}x{wh}+{(sw-ww)//2}+{(sh-wh)//2}")
        root.overrideredirect(True) # 暫時隱藏標題列
        root.deiconify()
        
        canvas = tk.Canvas(splash_frame, width=ww, height=wh, bg='#2c3e50', highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        canvas.create_rectangle(0, 0, ww, wh, outline='#3498db', width=4)
        canvas.create_text(ww//2, wh//2-30, text="PEGA Log Analyzer", fill='white', font=('Arial', 22, 'bold'))
        status_text = canvas.create_text(ww//2, wh//2+40, text="正在初始化核心服務...", fill='#bdc3c7', font=('Arial', 10))
        
        def animate_splash(step=0):
            if not root.winfo_exists(): return
            colors = ['#bdc3c7', '#ecf0f1', '#3498db']
            canvas.itemconfig(status_text, fill=colors[step % len(colors)])
            root.after(300, lambda: animate_splash(step + 1))
        
        animate_splash()
        
        def load_app():
            try:
                # 載入主程式類別
                canvas.itemconfig(status_text, text="正在載入介面組件...")
                root.update()
                from app.main_app import EnhancedLogAnalyzerApp
                
                canvas.itemconfig(status_text, text="正在完成最後部署...")
                root.update()
                
                # 初始化 App
                app = EnhancedLogAnalyzerApp(root)
                
                # 恢復視窗標準外觀
                root.overrideredirect(False)
                
                # 讀取視窗幾何設定（如果有存的話）
                if hasattr(app, 'config_manager'):
                    app.config_manager.load_window_geometry()
                else:
                    root.geometry("1280x800")
                
                # 移除啟動畫面
                splash_frame.destroy()
                
                # 如果有 PyInstaller 的啟動畫面，關閉它
                try:
                    import pyi_splash
                    pyi_splash.close()
                except ImportError:
                    pass
                    
            except Exception as e:
                error_msg = f"啟動時發生錯誤: {e}\n{traceback.format_exc()}"
                print(error_msg)
                try:
                    with open(log_file, "a", encoding="utf-8") as f:
                        f.write(error_msg + "\n")
                except: pass
                
                try:
                    import tkinter.messagebox as messagebox
                    messagebox.showerror("啟動失敗", f"程式啟動時發生嚴重錯誤，請檢查 {log_file}。\n\n錯誤訊息: {e}")
                except:
                    pass
                root.destroy()

        # 稍微延遲後開始載入
        root.after(500, load_app)
        root.mainloop()

    except Exception as e:
        error_msg = f"初始化階段發生錯誤: {e}\n{traceback.format_exc()}"
        print(error_msg)
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(error_msg + "\n")
        except: pass
        sys.exit(1)

if __name__ == '__main__':
    main()