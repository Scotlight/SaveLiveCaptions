# -*- coding: utf-8 -*-
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
current_state = 'STOPPED'  # 状态: STOPPED, RECORDING, PAUSED
pending_tasks = []  # 待处理的异步任务
# UI控件变量
start_btn = None
pause_btn = None
resume_btn = None
preview_btn = None
exit_btn = None

def safe_create_task(coro_func, *args, **kwargs):
    """安全创建异步任务"""
    global hook_task

    if hook_task and not hook_task.done():
        try:
            hook_task.cancel()
        except:
            pass

    try:
        hook_task = asyncio.create_task(coro_func(*args, **kwargs))
        return hook_task
    except Exception as e:
        print(f"❌ Task creation failed: {str(e)}")
        return None

async def safe_save_caption(filename, caption, is_pause_marker=False):
    """安全保存字幕"""
    global file_handle

    if file_handle is None:
        import aiofiles
        file_handle = await aiofiles.open(filename, "a+", encoding="utf-8")

    try:
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        await file_handle.write(f"[{timestamp}] {caption}\n")
        await file_handle.flush()
    except Exception as e:
        print(f"❌ 保存失败: {str(e)}")

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

def start_new_recording():
    """开始新的录制会话"""
    global current_filename, hook_task
    from function.save import choose_save_dir

    current_filename = choose_save_dir()
    if not current_filename:
        print("❌ 未选择保存位置")
        return

    # 在poll_loop中处理异步任务
    pending_tasks.append(('start', current_filename))
    print("✅ 开始录制")

def pause_recording():
    """暂停录制"""
    global current_state

    if current_state == 'RECORDING':
        # 在poll_loop中处理异步任务
        pending_tasks.append(('pause', current_filename))
        print("✅ 暂停已暂停")
    else:
        print("❌ 当前状态无法暂停")
        return False

def resume_recording():
    """继续录制"""
    global current_state, hook_task

    if current_state == 'PAUSED':
        # 在poll_loop中处理异步任务
        pending_tasks.append(('resume', current_filename))
        print("✅ 录制已继续")
    else:
        print("❌ 当前状态无法继续")
        return False

async def open_current_caption():
    """打开当前字幕文件预览"""
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

def lc_detect():
    """检测实时字幕功能"""
    try:
        from function.texthook import lc_detect
        return lc_detect()
    except Exception as e:
        print(f"❌ Live Captions检测失败: {str(e)}")
        return False

def update_ui_state(state):
    """更新UI状态"""
    global current_state, start_btn, pause_btn, resume_btn, preview_btn, exit_btn
    current_state = state

    if state == 'STOPPED':
        # 停止状态：只有开始和退出可用
        start_btn.config(state=tk.NORMAL, bg="#000000")
        pause_btn.config(state=tk.DISABLED, bg="#404040")
        resume_btn.config(state=tk.DISABLED, bg="#404040")
        preview_btn.config(state=tk.DISABLED, bg="#404040")
        exit_btn.config(state=tk.NORMAL, bg="#000000")
    elif state == 'RECORDING':
        # 录制状态：只有暂停、预览、退出可用
        start_btn.config(state=tk.DISABLED, bg="#404040")
        pause_btn.config(state=tk.NORMAL, bg="#000000")
        resume_btn.config(state=tk.DISABLED, bg="#404040")
        preview_btn.config(state=tk.NORMAL, bg="#000000")
        exit_btn.config(state=tk.NORMAL, bg="#000000")
    elif state == 'PAUSED':
        # 暂停状态：只有继续、预览、退出可用
        start_btn.config(state=tk.DISABLED, bg="#404040")
        pause_btn.config(state=tk.DISABLED, bg="#404040")
        resume_btn.config(state=tk.NORMAL, bg="#000000")
        preview_btn.config(state=tk.NORMAL, bg="#000000")
        exit_btn.config(state=tk.NORMAL, bg="#000000")

async def process_pending_tasks():
    """处理待处理的异步任务"""
    global pending_tasks, hook_task, current_state

    while pending_tasks:
        task_type, filename = pending_tasks.pop(0)

        if task_type == 'start':
            if hook_task and not hook_task.done():
                hook_task.cancel()

            from function.texthook import hook
            hook_task = asyncio.create_task(hook(filename, exit_event))
            update_ui_state('RECORDING')
            print("✅ 开始录制")

        elif task_type == 'pause':
            exit_event.set()
            await safe_save_caption(filename, "录制暂停", is_pause_marker=True)
            update_ui_state('PAUSED')
            print("✅ 暂停已暂停")

        elif task_type == 'resume':
            if hook_task and not hook_task.done():
                hook_task.cancel()

            from function.texthook import hook
            exit_event.clear()
            await safe_save_caption(filename, "录制继续", is_pause_marker=True)
            hook_task = asyncio.create_task(hook(filename, exit_event))
            update_ui_state('RECORDING')
            print("✅ 录制已继续")

def dashboard(loop):
    """主界面 - 专业多媒体控制栏样式"""
    global start_btn, pause_btn, resume_btn, preview_btn, exit_btn

    window = tk.Tk()
    window.title("SaveLiveCaptions")
    window.geometry("300x180")  # 垂直控制栏尺寸
    window.overrideredirect(True)
    window.wm_attributes("-topmost", True)
    window.configure(bg="#2c3e50")  # 专业软件背景色

    # 状态文本区域 - 顶部
    status_frame = tk.Frame(window, bg="#2c3e50", height=40)
    status_frame.pack(fill=tk.X, padx=10, pady=5)

    status_label = tk.Label(status_frame, text="状态: 已停止", fg="#ffffff",
                          bg="#2c3e50", font=("Microsoft YaHei UI", 10))
    status_label.pack(side=tk.LEFT, padx=5)

    # 录制状态指示器
    record_indicator = tk.Canvas(status_frame, width=8, height=8, bg="#2c3e50", highlightthickness=0)
    record_indicator.create_oval(2, 2, 6, 6, fill="#ff0000", outline="#2c3e50", width=2)
    record_indicator.pack(side=tk.LEFT, padx=5)

    # 控制按钮区域 - 垂直排列
    control_frame = tk.Frame(window, bg="#2c3e50", relief="flat", borderwidth=1)
    control_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    # 录制按钮 - 黑色实心圆点
    record_frame = tk.Frame(control_frame, bg="#2c3e50", relief="raised", borderwidth=1)
    record_frame.pack(fill=tk.X, pady=5)

    record_btn = tk.Button(record_frame, text="●", command=start_new_recording,
                           bg="#2c3e50", fg="#ffffff", width=40, height=35,
                           font=("Microsoft YaHei UI", 14), relief="flat", borderwidth=0)
    record_btn.pack(fill=tk.X, pady=5)
    create_tooltip(record_btn, "开始录制 (Record)")

    # 暂停按钮 - 两条垂直线，外框圆角矩形
    pause_frame = tk.Frame(control_frame, bg="#2c3e50", relief="raised", borderwidth=1)
    pause_frame.pack(fill=tk.X, pady=5)

    pause_canvas = tk.Canvas(pause_frame, width=40, height=35, bg="#2c3e50", highlightthickness=0)
    pause_canvas.pack(side=tk.LEFT, pady=5)

    # 外框圆角矩形
    pause_canvas.create_rectangle(4, 4, 32, 27, outline="#2c3e50", width=2, fill="")

    # 两条垂直线
    pause_canvas.create_line(20, 7, 20, 28, fill="#2c3e50", width=2)
    pause_canvas.create_line(20, 7, 20, 28, fill="#2c3e50", width=2)

    pause_canvas.bind("<Button-1>", lambda e: pause_recording())
    create_tooltip(pause_canvas, "暂停录制 (Pause)")

    # 播放按钮 - 指向右侧的三角形
    play_frame = tk.Frame(control_frame, bg="#2c3e50", relief="raised", borderwidth=1)
    play_frame.pack(fill=tk.X, pady=5)

    play_canvas = tk.Canvas(play_frame, width=40, height=35, bg="#2c3e50", highlightthickness=0)
    play_canvas.pack(side=tk.LEFT, pady=5)

    # 三角形指向右侧
    points = [8, 12, 20, 12, 20]  # 指向右侧的三角形
    play_canvas.create_polygon(points, fill="#808080", outline="#2c3e50", width=2)

    play_canvas.bind("<Button-1>", lambda e: resume_recording())
    create_tooltip(play_canvas, "继续录制 (Play)")

    # 文件夹按钮 - 文件夹轮廓
    preview_frame = tk.Frame(control_frame, bg="#2c3e50", relief="raised", borderwidth=1)
    preview_frame.pack(fill=tk.X, pady=5)

    preview_canvas = tk.Canvas(preview_frame, width=40, height=35, bg="#2c3e50", highlightthickness=0)
    preview_canvas.pack(side=tk.LEFT, pady=5)

    # 文件夹轮廓（带顶部开口）
    preview_canvas.create_rectangle(8, 6, 32, 24, outline="#2c3e50", width=2, fill="")
    preview_canvas.create_line(8, 6, 8, 18, 16, fill="#2c3e50", width=2)  # 顶部开口

    preview_canvas.bind("<Button-1>", lambda e: asyncio.run(open_current_caption()))
    create_tooltip(preview_canvas, "预览文件 (Open File)")

    # 停止按钮 - 黑色实心正方形
    stop_frame = tk.Frame(control_frame, bg="#2c3e50", relief="raised", borderwidth=1)
    stop_frame.pack(fill=tk.X, pady=5)

    stop_btn = tk.Button(stop_frame, text="■", command=lambda: asyncio.run(close_all(window)),
                           bg="#2c3e50", fg="#ffffff", width=40, height=35,
                           font=("Microsoft YaHei UI", 14), relief="flat", borderwidth=0)
    stop_btn.pack(fill=tk.X, pady=5)
    create_tooltip(stop_btn, "停止并退出 (Stop)")

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
                asyncio.run_coroutine_threadsafe(process_pending_tasks(), loop)
        except Exception as e:
            print(f"❌ 任务处理错误: {str(e)}")
        window.after(10, poll_loop)

    # 主事件循环
    window.mainloop()

def main():
    """主程序入口"""
    print("SaveLiveCaptions - Professional")
    loop = asyncio.new_event_loop()
    dashboard(loop)

if __name__ == "__main__":
    main()