# -*- coding: utf-8 -*-
import sys
import os
import asyncio
import tkinter as tk
from tkinter import filedialog
import time
import aiofiles

file_handle = None
saved_captions = set()
save_dir = ""

def choose_save_dir():
    global save_dir

    # 获取当前脚本所在目录的上级目录（项目根目录）
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    default_dir = os.path.join(script_dir, "new")

    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())

    # 默认使用项目根目录下的 new 文件夹
    save_dir = default_dir
    os.makedirs(save_dir, exist_ok=True)

    filename = os.path.join(save_dir, f"{timestamp}_captions.txt")

    return filename

def get_current_filename():
    """获取当前正在使用的文件名"""
    return None

def set_paused(paused):
    """设置暂停状态"""
    pass

def is_recording_paused():
    """检查是否处于暂停状态"""
    return False

def reset_for_new_recording():
    """重置状态以开始新的录制"""
    global file_handle, saved_captions
    file_handle = None
    saved_captions = set()

def clear_saved_captions():
    """清除已保存的字幕集合"""
    global saved_captions
    saved_captions = set()

async def save_txt(filename, caption):
    global file_handle

    if file_handle is None:
        file_handle = await aiofiles.open(filename, "a+", encoding="utf-8")

    crt_time = time.time()
    crt_time_formatted = time.strftime("%H:%M:%S", time.localtime(crt_time))

    if caption not in saved_captions:
        await file_handle.write(f"[{crt_time_formatted}] {caption}\n")
        await file_handle.flush()
        saved_captions.add(caption)

async def close_file():
    global file_handle
    if file_handle is not None:
        await file_handle.close()
        file_handle = None

def merge_cache_to_file():
    """合并缓存到文件 - 原项目不需要此功能"""
    pass

async def close_cache():
    """关闭缓存文件 - 原项目不需要此功能"""
    pass

def cleanup_cache():
    """删除缓存文件 - 原项目不需要此功能"""
    pass

def close_file_sync():
    """同步关闭文件"""
    global file_handle
    if file_handle is not None:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(close_file())
            else:
                loop.run_until_complete(close_file())
        except:
            file_handle = None