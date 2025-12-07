# -*- coding: utf-8 -*-
import sys
import os
import asyncio
import uiautomation as auto
from .save import save_to_cache, is_recording_paused
import re
import time

buffer = ""
last_saved_text = ""

def lc_detect():
    try:
        auto.SetGlobalSearchTimeout(0.5)

        desktop = auto.GetRootControl()
        captions_window = desktop.Control(
            searchDepth=1,
            ClassName="LiveCaptionsDesktopWindow",
            timeout=0.2
        )

        if captions_window.Exists(0):
            print("Live Captions Found")
            return True
        else:
            print(f"Live Captions Not Found")
            return False

    except Exception as e:
        print(f"Live Captions Not Found: {str(e)[:50]}...")
        return False


def reset_hook_state():
    """重置hook状态，用于新录制"""
    global buffer, last_saved_text
    buffer = ""
    last_saved_text = ""


def extract_new_text(current_text, previous_text):
    """提取新增的文本内容"""
    if not previous_text:
        # 第一次，返回全部文本
        return current_text

    if current_text.startswith(previous_text):
        # 新文本包含旧文本，返回新增部分
        new_part = current_text[len(previous_text):].strip()
        return new_part
    elif previous_text.startswith(current_text):
        # 文本缩短了，返回空
        return ""
    else:
        # 完全不同的文本，返回全部
        return current_text


async def hook(filename, exit_event):
    global buffer, last_saved_text

    try:
        lc_flag = lc_detect()
        if not lc_flag:
            return False

        desktop = auto.GetRootControl()
        captions_window = desktop.Control(searchDepth=1, ClassName="LiveCaptionsDesktopWindow")
        captions_scrollviewer = captions_window.Control(searchDepth=5, AutomationId="CaptionsScrollViewer", ClassName="ScrollViewer")

        print("Start capture...")

        while not exit_event.is_set():
            # 检查是否暂停
            if is_recording_paused():
                await asyncio.sleep(0.2)
                continue

            current_text = captions_scrollviewer.Name.strip()

            if current_text and current_text != buffer:
                # 提取新增文本
                new_text = extract_new_text(current_text, buffer)
                buffer = current_text

                # 保存新增内容到缓存
                if new_text and len(new_text) > 1:
                    print(f"New text detected: {new_text[:50]}...")
                    await save_to_cache(new_text)
                    last_saved_text = buffer

            # 检查间隔适中（避免太频繁）
            await asyncio.sleep(0.3)

    except Exception as e:
        print(f"Exception caught: {e}")
        return False