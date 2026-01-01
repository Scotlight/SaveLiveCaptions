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

def choose_save_dir(config=None):
    """选择保存目录并返回文件名
    
    Args:
        config: 配置字典，包含 save_directory 和 timestamp_format
    """
    global save_dir

    # 获取当前脚本所在目录的上级目录（项目根目录）
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 从配置中读取保存目录，默认为 "new"
    save_subdir = config.get("save_directory", "new") if config else "new"
    default_dir = os.path.join(script_dir, save_subdir)

    # 从配置中读取时间戳格式，默认为 "%Y-%m-%d_%H-%M-%S"
    timestamp_format = config.get("timestamp_format", "%Y-%m-%d_%H-%M-%S") if config else "%Y-%m-%d_%H-%M-%S"
    timestamp = time.strftime(timestamp_format, time.localtime())

    # 默认使用项目根目录下的配置文件夹
    save_dir = default_dir
    os.makedirs(save_dir, exist_ok=True)

    filename = os.path.join(save_dir, f"{timestamp}_captions.txt")

    return filename

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
    """关闭文件句柄"""
    global file_handle
    if file_handle is not None:
        try:
            await file_handle.close()
            file_handle = None
        except Exception as e:
            print(f"关闭文件时出错: {e}")
            file_handle = None