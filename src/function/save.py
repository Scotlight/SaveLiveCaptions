# -*- coding: utf-8 -*-
import sys
import os
import asyncio
import tkinter as tk
from tkinter import filedialog
import time
import aiofiles
import re

cache_handle = None
saved_captions = set()
save_dir = ""
current_filename = None
cache_filename = None
is_paused = False
line_buffer = []  # 用于记录每行的信息：(timestamp, text)

def choose_save_dir():
    global save_dir, current_filename, cache_filename

    # 获取当前脚本所在目录的上级目录（项目根目录）
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    default_dir = os.path.join(script_dir, "new")

    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())

    # 默认使用项目根目录下的 new 文件夹
    save_dir = default_dir
    os.makedirs(save_dir, exist_ok=True)

    current_filename = os.path.join(save_dir, f"{timestamp}_captions.txt")
    cache_filename = os.path.join(save_dir, f"{timestamp}_cache.tmp")

    return current_filename

def get_current_filename():
    """获取当前正在使用的文件名"""
    global current_filename
    return current_filename

def get_cache_filename():
    """获取缓存文件名"""
    global cache_filename
    return cache_filename

def set_paused(paused):
    """设置暂停状态"""
    global is_paused
    is_paused = paused

def is_recording_paused():
    """检查是否处于暂停状态"""
    global is_paused
    return is_paused

def reset_for_new_recording():
    """重置状态以开始新的录制"""
    global cache_handle, saved_captions, current_filename, cache_filename, is_paused, line_buffer
    cache_handle = None
    saved_captions = set()
    current_filename = None
    cache_filename = None
    is_paused = False
    line_buffer = []

def clear_saved_captions():
    """清除已保存的字幕集合（用于继续录制时避免重复）"""
    global saved_captions, line_buffer
    saved_captions = set()
    line_buffer = []

async def save_to_cache(text):
    """保存原始文本片段到缓存文件，带时间戳"""
    global cache_handle, cache_filename, line_buffer

    if not cache_filename:
        return

    if cache_handle is None:
        cache_handle = await aiofiles.open(cache_filename, "a+", encoding="utf-8")

    timestamp = time.strftime("%H:%M:%S", time.localtime())
    line = f"{timestamp}|{text}"  # 使用 | 分隔时间戳和文本
    await cache_handle.write(line + "\n")
    await cache_handle.flush()

    # 记录到内存缓冲区
    line_buffer.append((timestamp, text))
    print(f"Saved to cache file: {text}")  # 只是保存到缓存，不是最终文件

async def save_txt(filename, caption):
    """保存整合后的句子到最终文件 - 不应该在录制时使用"""
    # 这个函数现在不应该被直接调用
    pass

def merge_cache_to_file():
    """读取缓存文件，智能合并句子后写入最终文件"""
    global cache_filename, current_filename, line_buffer

    if not cache_filename or not os.path.exists(cache_filename):
        return

    try:
        # 优先使用内存缓冲区
        if line_buffer:
            lines_data = line_buffer
        else:
            # 从文件读取
            with open(cache_filename, "r", encoding="utf-8") as f:
                lines_data = []
                for line in f:
                    if "|" in line:
                        timestamp, text = line.strip().split("|", 1)
                        lines_data.append((timestamp, text))

        if not lines_data:
            return

        # 合并逻辑
        final_lines = []
        current_segment = []
        start_time = None
        end_time = None

        for timestamp, text in lines_data:
            # 检查是否有标点符号
            has_sentence_end = bool(re.search(r'[。！？.!?]', text))

            if not start_time:
                start_time = timestamp

            current_segment.append(text)
            end_time = timestamp

            # 如果有句末标点，结束当前段落
            if has_sentence_end:
                merged_text = "".join(current_segment)
                if merged_text.strip():
                    if start_time == end_time:
                        time_range = start_time
                    else:
                        time_range = f"{start_time}-{end_time}"
                    final_lines.append((time_range, merged_text))
                current_segment = []
                start_time = None
                end_time = None

        # 处理最后剩余的段落（没有标点的）
        if current_segment:
            # 每个没有标点的片段单独一行
            for i, text in enumerate(current_segment):
                timestamp = lines_data[-len(current_segment) + i][0]
                final_lines.append((timestamp, text))

        # 写入最终文件
        if final_lines and current_filename:
            with open(current_filename, "a", encoding="utf-8") as f:
                for time_range, text in final_lines:
                    # 避免重复保存
                    if text not in saved_captions:
                        if "-" in time_range:
                            f.write(f"[{time_range}] {text}\n")
                        else:
                            f.write(f"[{time_range}] {text}\n")
                        saved_captions.add(text)
                        print(f"Merged to final file: [{time_range}] {text}")

        # 清空缓存文件
        with open(cache_filename, "w", encoding="utf-8") as f:
            f.write("")

        # 清空内存缓冲区
        line_buffer = []

    except Exception as e:
        print(f"Error merging cache: {e}")

async def close_cache():
    """关闭缓存文件"""
    global cache_handle
    if cache_handle is not None:
        await cache_handle.close()
        cache_handle = None

async def close_file():
    """关闭最终文件"""
    pass  # 不再需要，因为我们只在合并时写入

def cleanup_cache():
    """删除缓存文件"""
    global cache_filename
    if cache_filename and os.path.exists(cache_filename):
        try:
            os.remove(cache_filename)
        except:
            pass

def close_file_sync():
    """同步关闭文件（用于非异步上下文）"""
    global cache_handle
    if cache_handle is not None:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(close_cache())
            else:
                loop.run_until_complete(close_cache())
        except:
            cache_handle = None