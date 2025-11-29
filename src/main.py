import sys
import os
import tkinter as tk
import tkinter.messagebox as msgbox
from function.texthook import hook, lc_detect
from function.save import choose_save_dir, choose_new_save_dir, close_file, save_txt, open_file_with_default_editor
import asyncio

file_handle = None
exit_event = asyncio.Event()

# 录制状态
RECORDING_STATES = {
    'STOPPED': '已停止',
    'RECORDING': '录制中',
    'PAUSED': '已暂停'
}
current_state = 'STOPPED'
current_filename = ""
hook_task = None

async def close_all(window):
    await asyncio.sleep(0.5)
    await close_file()
    window.destroy()

def dashboard(loop):
    window = tk.Tk()
    window.title("CatchCaptionsTool")
    window.geometry("60x240")  # 增加高度容纳新的打开文件按钮
    window.overrideredirect(True)
    window.wm_attributes("-topmost", True)

    if not lc_detect():
        msgbox.showerror("Error", "Live Captions Not Found")
        window.destroy()
        return

    # 状态标签
    status_label = tk.Label(window, text="状态: 已停止", fg="gray")
    status_label.pack(pady=5)

    # 先定义按钮变量（稍后绑定命令）
    start_btn = tk.Button(window, text="●", width=5)
    start_btn.pack(pady=2)

    pause_btn = tk.Button(window, text="⏸", state=tk.DISABLED, width=5)
    pause_btn.pack(pady=2)

    resume_btn = tk.Button(window, text="▶", state=tk.DISABLED, width=5)
    resume_btn.pack(pady=2)

    open_file_btn = tk.Button(window, text="📂", state=tk.DISABLED, width=5)
    open_file_btn.pack(pady=2)

    stop_btn = tk.Button(window, text="◼", width=5)
    stop_btn.pack(pady=2)

    def update_ui_state(state):
        """更新UI状态"""
        global current_state
        current_state = state

        if state == 'STOPPED':
            status_label.config(text="状态: 已停止", fg="gray")
            start_btn.config(state=tk.NORMAL)
            pause_btn.config(state=tk.DISABLED)
            resume_btn.config(state=tk.DISABLED)
            open_file_btn.config(state=tk.DISABLED)
            stop_btn.config(state=tk.NORMAL)
        elif state == 'RECORDING':
            status_label.config(text="状态: 录制中", fg="green")
            start_btn.config(state=tk.DISABLED)
            pause_btn.config(state=tk.NORMAL)
            resume_btn.config(state=tk.DISABLED)
            open_file_btn.config(state=tk.DISABLED)
            stop_btn.config(state=tk.NORMAL)
        elif state == 'PAUSED':
            status_label.config(text="状态: 已暂停", fg="orange")
            start_btn.config(state=tk.DISABLED)
            pause_btn.config(state=tk.DISABLED)
            resume_btn.config(state=tk.NORMAL)
            open_file_btn.config(state=tk.NORMAL)
            stop_btn.config(state=tk.NORMAL)

    def start_new_recording():
        """开始新的录制会话"""
        global current_filename

        # 选择新的保存位置
        current_filename = choose_new_save_dir()

        # 清除停止事件
        exit_event.clear()

        # 开始录制（这是新的录制，不是从暂停恢复）
        global hook_task
        hook_task = loop.create_task(hook(current_filename, exit_event, is_paused=False))

        update_ui_state('RECORDING')

    def pause_recording():
        """暂停录制"""
        global hook_task

        # 先设置停止事件来暂停hook（停止捕获新的字幕）
        exit_event.set()

        # 添加暂停标记到文件
        if current_filename:
            loop.create_task(save_txt(current_filename, "录制暂停", is_pause_marker=True))

        update_ui_state('PAUSED')

    def resume_recording():
        """继续录制"""
        global hook_task

        # 清除停止事件
        exit_event.clear()

        # 添加继续标记
        if current_filename:
            loop.create_task(save_txt(current_filename, "录制继续", is_pause_marker=True))

        # 重新开始hook（这是从暂停状态恢复）
        hook_task = loop.create_task(hook(current_filename, exit_event, is_paused=True))

        update_ui_state('RECORDING')

    def open_output_file():
        """打开输出文件"""
        try:
            # 先确保文件缓冲区被刷新
            loop.create_task(flush_and_open_file())
        except Exception as e:
            msgbox.showerror("错误", f"无法打开文件: {str(e)}")

    async def flush_and_open_file():
        """刷新文件缓冲区并打开文件"""
        from function.save import file_handle

        # 刷新文件缓冲区
        if file_handle and not file_handle.closed:
            await file_handle.flush()

        # 确保文件存在且有内容
        if current_filename and os.path.exists(current_filename):
            open_file_with_default_editor(current_filename)
        else:
            msgbox.showinfo("提示", "文件不存在或尚未创建，请先进行录制。")

    def stop_and_exit(window):
        """停止录制并退出应用"""
        global hook_task

        # 设置停止事件
        exit_event.set()

        # 添加结束标记
        if current_filename:
            loop.create_task(save_txt(current_filename, "录制结束", is_pause_marker=True))

        update_ui_state('STOPPED')

        # 关闭应用
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

    # 在所有函数定义完成后，绑定按钮命令
    start_btn.config(command=start_new_recording)
    pause_btn.config(command=pause_recording)
    resume_btn.config(command=resume_recording)
    open_file_btn.config(command=open_output_file)
    stop_btn.config(command=lambda: stop_and_exit(window))

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
