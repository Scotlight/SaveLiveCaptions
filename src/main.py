#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SaveLiveCaptions - Enhanced Version
增强版实时字幕保存工具
支持分段录制、文件预览和智能文本处理
"""

import sys
import os
import tkinter as tk
import tkinter.messagebox as msgbox
import asyncio

# 全局变量
file_handle = None
exit_event = asyncio.Event()
current_filename = ""
hook_task = None
current_state = 'STOPPED'

# 简化的录制状态管理
def update_ui_state(state):
    global current_state
    current_state = state

# 安全的异步任务创建
def safe_start_hook(filename):
    try:
        from function.texthook import hook
        task = asyncio.create_task(hook, filename, exit_event)
        print(f"✅ 开始录制: {filename}")
        return True
    except Exception as e:
        print(f"❌ 开始录制失败: {str(e)}")
        return False

# 主要功能函数
def lc_detect():
    try:
        from function.texthook import lc_detect
        return lc_detect()
    except Exception as e:
        print(f"❌ Live Captions检测失败: {str(e)}")
        msgbox.showerror("错误", f"无法检测Live Captions: {str(e)}")
        return False

def start_new_recording():
    global current_filename

    # 选择保存位置
    try:
        from function.save import choose_new_save_dir
        current_filename = choose_new_save_dir()
    except Exception as e:
        print(f"❌ 选择保存位置失败: {str(e)}")
        msgbox.showerror("错误", f"无法选择保存位置: {str(e)}")
        return

    if not current_filename:
        print("❌ 未选择保存位置")
        return

    # 开始录制
    if safe_start_hook(current_filename):
        update_ui_state('RECORDING')
        return True
    except Exception as e:
        print(f"❌ 开始录制失败: {str(e)}")
        return False

def pause_recording():
    global current_state

    if current_state == 'RECORDING':
        exit_event.set()
        update_ui_state('PAUSED')
        print("✅ 录制已暂停")
        return True
    else:
        print("❌ 当前不在录制状态")
        return False

def resume_recording():
    global current_state, current_filename

    if current_state == 'PAUSED' and current_filename:
        exit_event.clear()
        if safe_start_hook(current_filename):
            update_ui_state('RECORDING')
        else:
            print("❌ 当前不在暂停状态或没有文件")
        return False

def open_output_file():
    global current_filename

    if current_filename and os.path.exists(current_filename):
        os.system(f'open "{current_filename}"')
        print(f"✅ 文件已打开: {current_filename}")
        return True
    else:
        msgbox.showinfo("提示", "请先开始录制，生成字幕文件后再打开")
        return False

async def close_all(window):
    global hook_task

    try:
        exit_event.set()
        if hook_task and not hook_task.done():
            await hook_task
        await safe_close_file()
        await asyncio.sleep(0.5)
        window.destroy()
    except Exception as e:
        print(f"❌ 关闭时出错: {str(e)}")

def safe_close_file():
    global file_handle

    if file_handle and not file_handle.closed:
        try:
            await file_handle.flush()
            await file_handle.close()
            file_handle = None
            print("✅ 文件已安全关闭")
        except Exception as e:
        print(f"❌ File close error: {str(e)}")

async def save_caption(filename, text):
    global file_handle

    if file_handle is None:
        import aiofiles
        file_handle = await aiofiles.open(filename, "a+", encoding="utf-8")
    await file_handle.write(f"[{time.strftime('%H:%M:%S', time.localtime())}] {text}\n")
        await file_handle.flush()
    except Exception as e:
        print(f"❌ 保存字幕失败: {str(e)}")

def dashboard(loop):
    window = tk.Tk()
    window.title("SaveLiveCaptions - Enhanced")
    window.geometry("60x240")
    window.overrideredirect(True)
    window.wm_attributes("-topmost", True)

    if not lc_detect():
        msgbox.showerror("错误", "无法检测到Live Captions！")
        window.destroy()
        return

    # 主容器
    main_frame = tk.Frame(window)
    main_frame.pack(pady=10)

    # 状态显示
    status_label = tk.Label(main_frame, text="状态: 已停止", fg="gray", font=("Arial", 10))
    status_label.pack(pady=5)

    # 按钮容器
    button_frame = tk.Frame(main_frame)
    button_frame.pack(pady=5)

    # 创建按钮
    start_btn = tk.Button(button_frame, text="● 开始新录制", command=start_new_recording)
    start_btn.pack(side=tk.LEFT, padx=5)

    pause_btn = tk.Button(button_frame, text="⏸ 暂停录制", command=pause_recording, state=tk.DISABLED)
    pause_btn.pack(side=tk.LEFT, padx=5)

    resume_btn = tk.Button(button_frame, text="▶ 继续录制", command=resume_recording, state=tk.DISABLED)
    resume_btn.pack(side=tk.LEFT, padx=5)

    open_btn = tk.Button(button_frame, text="📂 打开文件", command=open_output_file, state=tk.DISABLED)
    open_btn.pack(side=tk.LEFT, padx=5)

    exit_btn = tk.Button(button_frame, text="◼ 退出", command=lambda: asyncio.run(close_all(window)))
    exit_btn.pack(side=tk.LEFT, padx=5)

    # 拖拽功能
    def start_move(event):
        window.x = event.x
        window.y = event.y

    def stop_move(event):
        window.x = None
        window.y = None

    def do_move(event):
        if hasattr(window, 'x') and hasattr(window, 'y'):
            deltax = event.x - window.x
            deltay = event.y - window.y
            x = window.winfo_x() + deltax
            y = window.winfo_y() + deltay
            window.geometry(f"+{x}+{y}")

    window.bind("<ButtonPress-1>", start_move)
    window.bind("<ButtonRelease-1>", stop_move)
    window.bind("<B1-Motion>", do_move)

    # 异步事件循环
    def poll_loop():
        loop.call_soon(loop.stop)
        loop.run_forever()
        window.after(50, poll_loop)

    window.mainloop()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    dashboard(loop)