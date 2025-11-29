import sys
import os
import asyncio
import tkinter as tk
from tkinter import filedialog
import time
import aiofiles
import subprocess

file_handle = None
saved_captions = set()
save_dir = ""
current_filename = ""

def open_file_with_default_editor(filename):
    """使用系统默认程序打开文件"""
    try:
        if os.name == 'nt':  # Windows
            os.startfile(filename)
        elif os.name == 'posix':  # macOS and Linux
            subprocess.run(['open', filename], check=True)
    except Exception as e:
        print(f"无法打开文件: {e}")
        return False
    return True

def choose_save_dir():
    global save_dir, current_filename

    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())

    if not save_dir:
        root = tk.Tk()
        root.withdraw()
        save_dir = filedialog.askdirectory(
            title="choose direction",
            initialdir=os.path.expanduser("~")
        )
        root.destroy()

        if not save_dir:
            save_dir = os.path.expanduser("~/Documents/captions")
            os.makedirs(save_dir, exist_ok=True)

    current_filename = os.path.join(save_dir, f"{timestamp}_captions.txt")

    return current_filename

def choose_new_save_dir():
    """选择新的保存位置，用于开始新的录制会话"""
    global save_dir, current_filename, saved_captions

    # 清理当前文件句柄
    if file_handle is not None:
        asyncio.create_task(close_current_file())

    # 清空已保存字幕记录
    saved_captions.clear()

    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())

    root = tk.Tk()
    root.withdraw()
    save_dir = filedialog.askdirectory(
        title="choose direction",
        initialdir=os.path.expanduser("~")
    )
    root.destroy()

    if not save_dir:
        save_dir = os.path.expanduser("~/Documents/captions")
        os.makedirs(save_dir, exist_ok=True)

    current_filename = os.path.join(save_dir, f"{timestamp}_captions.txt")

    return current_filename

async def close_current_file():
    """关闭当前文件"""
    global file_handle
    if file_handle is not None:
        await file_handle.close()
        file_handle = None

async def save_txt(filename, caption, is_pause_marker=False):
    global file_handle

    if file_handle is None:
        file_handle = await aiofiles.open(filename, "a+", encoding="utf-8")

    crt_time = time.time()
    crt_time_formatted = time.strftime("%H:%M:%S", time.localtime(crt_time))

    if is_pause_marker:
        # 添加暂停/继续标记
        marker_text = f"\n[{crt_time_formatted}] ===== {caption} =====\n"
        await file_handle.write(marker_text)
        await file_handle.flush()
    elif caption not in saved_captions:
        await file_handle.write(f"[{crt_time_formatted}] {caption}\n")
        await file_handle.flush()
        saved_captions.add(caption)

async def close_file():
    """完全关闭文件"""
    global file_handle
    if file_handle is not None:
        await file_handle.close()
        file_handle = None