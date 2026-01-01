# -*- coding: utf-8 -*-
import sys
import os
import tkinter as tk
import tkinter.messagebox as msgbox
from function.texthook import hook, lc_detect, reset_hook_state
from function.save import choose_save_dir, close_file, reset_for_new_recording
import asyncio
import json
import time

file_handle = None
exit_event = asyncio.Event()
hook_task = None
current_filename = None
current_state = "stopped"  # stopped, recording, paused
start_time = None
app_config = {}

def load_config():
    """加载配置文件，如果不存在则使用默认值"""
    global app_config
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
    
    # 默认配置
    default_config = {
        "save_directory": "new",
        "polling_interval": 0.2,
        "timestamp_format": "%Y-%m-%d_%H-%M-%S",
        "time_format": "%H:%M:%S"
    }
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                app_config = json.load(f)
                # 合并默认配置，确保所有键都存在
                for key, value in default_config.items():
                    if key not in app_config:
                        app_config[key] = value
                print(f"已加载配置: {config_path}")
        else:
            app_config = default_config
            print("使用默认配置")
    except Exception as e:
        print(f"加载配置失败，使用默认值: {e}")
        app_config = default_config
    
    return app_config

async def close_all(window):
    await asyncio.sleep(0.5)
    await close_file()
    window.destroy()

def dashboard(loop):
    global hook_task, current_filename, current_state, start_time
    
    # 加载配置
    load_config()

    window = tk.Tk()
    window.title("CatchCaptionsTool")
    window.geometry("150x320")
    window.overrideredirect(True)
    window.wm_attributes("-topmost", True)

    if not lc_detect():
        msgbox.showerror("Error", "Live Captions Not Found")
        window.destroy()
        return

    def update_ui_state():
        """根据当前状态更新按钮可用性"""
        if current_state == "stopped":
            start_btn.config(state=tk.NORMAL)
            pause_btn.config(state=tk.DISABLED)
            resume_btn.config(state=tk.DISABLED)
            preview_btn.config(state=tk.DISABLED)
        elif current_state == "recording":
            start_btn.config(state=tk.DISABLED)
            pause_btn.config(state=tk.NORMAL)
            resume_btn.config(state=tk.DISABLED)
            preview_btn.config(state=tk.NORMAL)
        elif current_state == "paused":
            start_btn.config(state=tk.DISABLED)
            pause_btn.config(state=tk.DISABLED)
            resume_btn.config(state=tk.NORMAL)
            preview_btn.config(state=tk.NORMAL)

    def start_capture():
        global hook_task, current_filename, current_state, start_time
        reset_for_new_recording()
        reset_hook_state()
        exit_event.clear()
        start_time = time.time()
        current_filename = choose_save_dir(app_config)
        hook_task = loop.create_task(hook(current_filename, exit_event, app_config))
        current_state = "recording"
        update_ui_state()

    def pause_capture():
        global current_state
        exit_event.set()
        current_state = "paused"
        update_ui_state()

    def resume_capture():
        global current_state, hook_task
        exit_event.clear()
        hook_task = loop.create_task(hook(current_filename, exit_event, app_config))
        current_state = "recording"
        update_ui_state()

    def preview_file():
        global current_filename
        if current_filename and os.path.exists(current_filename):
            os.startfile(current_filename)
        else:
            msgbox.showinfo("Info", "No file to preview")

    def stop_capture():
        global current_state
        exit_event.set()
        current_state = "stopped"
        loop.create_task(close_all(window))

    def start_move(event):
        window.x = event.x
        window.y = event.y

    def stop_move(event):
        window.x = None
        window.y = None

    def do_move(event):
        deltax = event.x - window.x
        deltay = event.y - window.y
        x = window.winfo_x() + deltax
        y = window.winfo_y() + deltay
        window.geometry(f"+{x}+{y}")

    window.bind("<ButtonPress-1>", start_move)
    window.bind("<ButtonRelease-1>", stop_move)
    window.bind("<B1-Motion>", do_move)

    # 录制时长标签
    duration_label = tk.Label(window, text="时长: 00:00", font=("Arial", 10))
    duration_label.pack(pady=5)
    
    def update_stats():
        """更新录制时长显示"""
        if current_state == "recording" and start_time is not None:
            elapsed = int(time.time() - start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            duration_label.config(text=f"时长: {minutes:02d}:{seconds:02d}")
        elif current_state == "stopped":
            duration_label.config(text="时长: 00:00")
    
    # 5个按钮：开始、暂停、继续、预览、退出
    start_btn = tk.Button(window, text="●", command=start_capture, width=8)
    start_btn.pack(pady=3)

    pause_btn = tk.Button(window, text="⏸", command=pause_capture, width=8)
    pause_btn.pack(pady=3)

    resume_btn = tk.Button(window, text="▶", command=resume_capture, width=8)
    resume_btn.pack(pady=3)

    preview_btn = tk.Button(window, text="👁", command=preview_file, width=8)
    preview_btn.pack(pady=3)

    stop_btn = tk.Button(window, text="◼", command=stop_capture, width=8)
    stop_btn.pack(pady=3)

    # 初始化按钮状态和统计显示
    update_ui_state()
    update_stats()

    def poll_loop():
        update_stats()  # 每次轮询时更新统计信息
        loop.call_soon(loop.stop)
        loop.run_forever()
        window.after(500, poll_loop)  # 每500ms更新一次

    window.after(10, poll_loop)
    window.mainloop()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    dashboard(loop)