# -*- coding: utf-8 -*-
import sys
import os
import tkinter as tk
import tkinter.messagebox as msgbox
import asyncio
from datetime import datetime

# 全局变量
current_filename = ""
hook_task = None
current_state = 'STOPPED'  # 状态: STOPPED, RECORDING, PAUSED
pending_tasks = []  # 待处理的异步任务
start_btn = None
pause_btn = None
resume_btn = None
file_btn = None
stop_btn = None

def safe_save_caption(filename, caption, is_pause_marker=False):
    """安全保存字幕"""
    try:
        timestamp = datetime.now().strftime("%H:%M:%S")

        # 读取现有内容
        existing_content = ""
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                existing_content = f.read()

        # 添加新内容
        with open(filename, 'a', encoding='utf-8') as f:
            if existing_content and not existing_content.endswith('\n'):
                f.write('\n')
            f.write(f"[{timestamp}] {caption}\n")

        print(f"✅ 保存字幕: {caption}")
        return True
    except Exception as e:
        print(f"❌ 保存失败: {str(e)}")
        return False

def choose_save_dir():
    """选择保存目录"""
    try:
        from tkinter import filedialog

        save_path = filedialog.asksaveasfilename(
            title="保存实时字幕",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialdir=os.path.expanduser("~/Documents/LiveCaptions")
        )

        if save_path:
            print(f"✅ 选择保存位置: {save_path}")
            return save_path
        else:
            print("❌ 未选择保存位置")
            return ""
    except Exception as e:
        print(f"❌ 选择目录失败: {str(e)}")
        return ""

async def hook_current_events(filename, exit_event):
    """简单的字幕捕获模拟"""
    try:
        print(f"🎯 开始捕获字幕到: {filename}")

        # 模拟字幕捕获
        sentences = [
            "今天天气很好",
            "欢迎使用实时字幕功能",
            "这是一个测试字幕",
            "您可以开始录制了",
            "字幕内容会实时保存",
            "测试第一句话",
            "测试第二句话",
            "录制进行中..."
        ]

        sentence_index = 0
        while not exit_event.is_set():
            if sentence_index < len(sentences):
                caption = sentences[sentence_index]
                await safe_save_caption(filename, caption)
                sentence_index += 1
            await asyncio.sleep(3)  # 每3秒保存一个测试字幕

        print("🎯 字幕捕获已停止")

    except Exception as e:
        print(f"❌ 字幕捕获错误: {str(e)}")

def update_ui_state(state):
    """更新UI状态"""
    global current_state, start_btn, pause_btn, resume_btn, file_btn, stop_btn
    current_state = state

    if state == 'STOPPED':
        # 停止状态：只有开始和停止可用
        start_btn.config(state=tk.NORMAL, bg="#000000")
        pause_btn.config(state=tk.DISABLED, bg="#404040")
        resume_btn.config(state=tk.DISABLED, bg="#404040")
        file_btn.config(state=tk.DISABLED, bg="#404040")
        stop_btn.config(state=tk.NORMAL, bg="#000000")
    elif state == 'RECORDING':
        # 录制状态：只有暂停、预览、退出可用
        start_btn.config(state=tk.DISABLED, bg="#404040")
        pause_btn.config(state=tk.NORMAL, bg="#000000")
        resume_btn.config(state=tk.DISABLED, bg="#404040")
        file_btn.config(state=tk.NORMAL, bg="#000000")
        stop_btn.config(state=tk.NORMAL, bg="#000000")
    elif state == 'PAUSED':
        # 暂停状态：只有继续、预览、退出可用
        start_btn.config(state=tk.DISABLED, bg="#404040")
        pause_btn.config(state=tk.DISABLED, bg="#404040")
        resume_btn.config(state=tk.NORMAL, bg="#000000")
        file_btn.config(state=tk.NORMAL, bg="#000000")
        stop_btn.config(state=tk.NORMAL, bg="#000000")

def start_new_recording():
    """开始新的录制会话"""
    global current_filename, hook_task, current_state
    current_filename = choose_save_dir()
    if not current_filename:
        print("❌ 未选择保存位置")
        return

    if hook_task and not hook_task.done():
        try:
            hook_task.cancel()
        except:
            pass

    try:
        import asyncio
        hook_task = asyncio.create_task(hook_current_events(current_filename, asyncio.Event()))
        update_ui_state('RECORDING')
        print("✅ 开始录制")
        return hook_task
    except Exception as e:
        print(f"❌ Task creation failed: {str(e)}")
        return None

def pause_recording():
    """暂停录制"""
    global current_state

    if current_state == 'RECORDING':
        try:
            # 在poll_loop中处理异步任务
            pending_tasks.append(('pause', current_filename))
            update_ui_state('PAUSED')
            print("✅ 暂停已暂停")
            return True
        except Exception as e:
            print(f"❌ 暂停失败: {str(e)}")
            return False
    else:
        print("❌ 当前状态无法暂停")
        return False

def resume_recording():
    """继续录制"""
    global current_state, hook_task

    if current_state == 'PAUSED':
        try:
            # 在poll_loop中处理异步任务
            pending_tasks.append(('resume', current_filename))
            update_ui_state('RECORDING')
            print("✅ 录制已继续")
            return True
        except Exception as e:
            print(f"❌ 继续录制失败: {str(e)}")
            return False
    else:
        print("❌ 当前状态无法继续")
        return False

def open_current_caption():
    """打开当前字幕文件预览"""
    global current_filename

    if current_filename and os.path.exists(current_filename):
        try:
            os.startfile(current_filename)
            print(f"✅ 已打开字幕文件: {current_filename}")
            return True
        except Exception as e:
            print(f"❌ 打开文件失败: {str(e)}")
            return False
    else:
        print("❌ 没有找到字幕文件")
        return False

async def close_all(window):
    """关闭所有资源并退出应用"""
    global hook_task

    if hook_task and not hook_task.done():
        try:
            hook_task.cancel()
        except:
            pass

    await safe_save_caption(current_filename, "录制结束", is_pause_marker=True)
    window.destroy()
    sys.exit(0)

def create_tooltip(widget, text):
    """为控件创建工具提示"""
    def on_enter(event):
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        label = tk.Label(tooltip, text=text, background="lightyellow",
                        relief="solid", borderwidth=1, font=("Arial", 9))
        label.pack()
        widget.tooltip = tooltip

    def on_leave(event):
        if hasattr(widget, 'tooltip'):
            widget.tooltip.destroy()
            del widget.tooltip

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

async def process_pending_tasks():
    """处理待处理的异步任务"""
    global pending_tasks, hook_task, current_state

    while pending_tasks:
        task_type, filename = pending_tasks.pop(0)

        if task_type == 'start':
            if hook_task and not hook_task.done():
                hook_task.cancel()

            hook_task = asyncio.create_task(hook_current_events(filename, asyncio.Event()))
            update_ui_state('RECORDING')
            print("✅ 开始录制")

        elif task_type == 'pause':
            update_ui_state('PAUSED')
            print("✅ 暂停已暂停")

        elif task_type == 'resume':
            update_ui_state('RECORDING')
            print("✅ 录制已继续")

def dashboard():
    """主界面 - 简单垂直控制栏样式"""
    global start_btn, pause_btn, resume_btn, file_btn, stop_btn

    # 创建主窗口
    window = tk.Tk()
    window.title("SaveLiveCaptions - Professional")
    window.geometry("150x350")  # 加宽窗口，适合垂直排列
    window.overrideredirect(True)
    window.wm_attributes("-topmost", True)
    window.configure(bg="#f0f0f0")  # 白色背景

    # 顶部状态区域
    status_frame = tk.Frame(window, bg="#f0f0f0", height=50)
    status_frame.pack(fill=tk.X, padx=15, pady=(15, 10))

    status_label = tk.Label(status_frame, text="状态: 已停止", fg="#000000", bg="#f0f0f0",
                          font=("Microsoft YaHei UI", 11))
    status_label.pack(side=tk.LEFT, padx=10)

    # 控制按钮区域 - 垂直排列
    control_frame = tk.Frame(window, bg="#f0f0f0", relief="solid", borderwidth=1)
    control_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

    # 按钮样式
    button_style = {
        'font': ("Arial", 12),
        'fg': "#000000",
        'bg': "#ffffff",
        'activebackground': "#e0e0e0",
        'activeforeground': "#000000",
        'relief': "solid",
        'borderwidth': 2,
        'width': 12,
        'height': 3
    }

    # 录制按钮 - 黑色实心圆点
    start_btn = tk.Button(control_frame, text="●", command=start_new_recording,
                           **button_style)
    start_btn.pack(fill=tk.X, pady=8)
    create_tooltip(start_btn, "开始录制")

    # 暂停按钮 - 两条竖线
    pause_btn = tk.Button(control_frame, text="⏸", command=pause_recording,
                          **button_style)
    pause_btn.pack(fill=tk.X, pady=8)
    create_tooltip(pause_btn, "暂停录制")

    # 播放按钮 - 右指三角形
    resume_btn = tk.Button(control_frame, text="▶", command=resume_recording,
                          **button_style)
    resume_btn.pack(fill=tk.X, pady=8)
    create_tooltip(resume_btn, "继续录制")

    # 文件夹按钮 - 文件夹图标
    file_btn = tk.Button(control_frame, text="📁", command=open_current_caption,
                       **button_style)
    file_btn.pack(fill=tk.X, pady=8)
    create_tooltip(file_btn, "预览文件")

    # 停止按钮 - 黑色实心方形
    stop_btn = tk.Button(control_frame, text="■", command=lambda: asyncio.run(close_all(window)),
                       **button_style)
    stop_btn.pack(fill=tk.X, pady=8)
    create_tooltip(stop_btn, "停止并退出")

    # 设置初始状态
    update_ui_state('STOPPED')

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
        try:
            if pending_tasks:
                asyncio.run(process_pending_tasks())
        except Exception as e:
            print(f"❌ 任务处理错误: {str(e)}")
        window.after(100, poll_loop)

    # 主事件循环
    poll_loop()
    window.mainloop()

def main():
    """主程序入口"""
    print("SaveLiveCaptions - Professional Vertical Control")
    dashboard()

if __name__ == "__main__":
    main()