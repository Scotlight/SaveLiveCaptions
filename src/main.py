# -*- coding: utf-8 -*-
import sys
import os
import tkinter as tk
import tkinter.messagebox as msgbox
from function.texthook import hook, lc_detect, reset_hook_state
from function.save import choose_save_dir, close_file, reset_for_new_recording
import asyncio

file_handle = None
exit_event = asyncio.Event()
hook_task = None
current_filename = None
current_state = "stopped"  # stopped, recording, paused

async def close_all(window):
    await asyncio.sleep(0.5)
    await close_file()
    window.destroy()

def dashboard(loop):
    global hook_task, current_filename, current_state

    window = tk.Tk()
    window.title("CatchCaptionsTool")
    window.geometry("60x280")
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
        global hook_task, current_filename, current_state
        reset_for_new_recording()
        reset_hook_state()
        exit_event.clear()
        current_filename = choose_save_dir()
        hook_task = loop.create_task(hook(current_filename, exit_event))
        current_state = "recording"
        update_ui_state()

    def pause_capture():
        global current_state
        exit_event.set()
        current_state = "paused"
        update_ui_state()

    def resume_capture():
        global current_state
        exit_event.clear()
        hook_task = loop.create_task(hook(current_filename, exit_event))
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

    # 5个按钮：开始、暂停、继续、预览、退出
    start_btn = tk.Button(window, text="●", command=start_capture, width=4)
    start_btn.pack(pady=5)

    pause_btn = tk.Button(window, text="⏸", command=pause_capture, width=4)
    pause_btn.pack(pady=5)

    resume_btn = tk.Button(window, text="▶", command=resume_capture, width=4)
    resume_btn.pack(pady=5)

    preview_btn = tk.Button(window, text="👁", command=preview_file, width=4)
    preview_btn.pack(pady=5)

    stop_btn = tk.Button(window, text="◼", command=stop_capture, width=4)
    stop_btn.pack(pady=5)

    # 初始化按钮状态
    update_ui_state()

    def poll_loop():
        loop.call_soon(loop.stop)
        loop.run_forever()
        window.after(10, poll_loop)

    window.after(10, poll_loop)
    window.mainloop()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    dashboard(loop)