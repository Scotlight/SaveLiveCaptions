# -*- coding: utf-8 -*-
import sys
import os
import asyncio
import uiautomation as auto
from .save import save_to_cache, is_recording_paused
import re
import time

buffer = ""
last_second_text = ""

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
    global buffer, last_second_text
    buffer = ""
    last_second_text = ""


async def hook(filename, exit_event):
    global buffer, last_second_text

    try:
        lc_flag = lc_detect()
        if not lc_flag:
            return False

        desktop = auto.GetRootControl()
        captions_window = desktop.Control(searchDepth=1, ClassName="LiveCaptionsDesktopWindow")
        captions_scrollviewer = captions_window.Control(searchDepth=5, AutomationId="CaptionsScrollViewer", ClassName="ScrollViewer")

        print("Start capture...")
        last_save_time = time.time()

        while not exit_event.is_set():
            # 检查是否暂停
            if is_recording_paused():
                await asyncio.sleep(0.2)
                continue

            current_text = captions_scrollviewer.Name.strip()

            if current_text and current_text != buffer:
                buffer = current_text

            # 检查是否已经过了1秒
            current_time = time.time()
            if current_time - last_save_time >= 1.0:
                if buffer and buffer != last_second_text:
                    # 每秒都保存到缓存
                    print(f"Saving to cache: {buffer}")
                    await save_to_cache(buffer)
                    last_second_text = buffer
                    last_save_time = current_time

            await asyncio.sleep(0.1)  # 更频繁的检查

    except Exception as e:
        print(f"Exception caught: {e}")
        return False