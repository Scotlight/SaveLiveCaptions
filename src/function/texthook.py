import sys
import os
import asyncio
import uiautomation as auto
from .save import save_txt
import re

buffer = ""
incomplete_sentence = ""
processed_sentences = set()
last_complete_sentence = ""


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


def normalize_text(text):
    """标准化文本：清理换行符、多余空格等"""
    # 移除换行符并替换为空格
    text = re.sub(r'[\n\r]+', ' ', text)
    # 将多个空格替换为单个空格
    text = re.sub(r'\s+', ' ', text)
    # 移除首尾空格
    return text.strip()


def extract_sentences(text):
    """提取完整的句子"""
    text = normalize_text(text)
    sentences = []

    # 使用更精确的句子分割正则表达式
    sentence_pattern = r'([^.!?。！？]*[.!?。！？]+)'
    matches = list(re.finditer(sentence_pattern, text))

    last_end = 0
    for match in matches:
        # 检查是否跳过了某些文本
        if match.start() > last_end:
            skipped_text = text[last_end:match.start()].strip()
            if skipped_text and len(skipped_text) > 5:  # 如果跳过的文本足够长，记录为未完成
                incomplete_sentence = skipped_text

        sentence = match.group(1).strip()
        if len(sentence) > 3:  # 过滤太短的句子
            sentences.append(sentence)
        last_end = match.end()

    # 处理剩余文本
    if last_end < len(text):
        remaining = text[last_end:].strip()
        if remaining:
            incomplete_sentence = remaining
            sentences.append(remaining)  # 临时标记为不完整，稍后过滤

    return sentences


async def hook(filename, exit_event, is_paused=False):
    global buffer, incomplete_sentence, processed_sentences, last_complete_sentence

    try:
        lc_flag = lc_detect()
        if not lc_flag:
            return False

        desktop = auto.GetRootControl()
        captions_window = desktop.Control(searchDepth=1, ClassName="LiveCaptionsDesktopWindow")
        captions_scrollviewer = captions_window.Control(searchDepth=5, AutomationId="CaptionsScrollViewer", ClassName="ScrollViewer")

        print("Start capture...")

        # 根据是否为暂停恢复来初始化状态
        if not is_paused:
            buffer = ""
            incomplete_sentence = ""
            processed_sentences = set()
            last_complete_sentence = ""

        while not exit_event.is_set():
            current_text = captions_scrollviewer.Name.strip()

            if current_text and current_text != buffer:
                buffer = current_text

                # 提取并处理句子
                sentences = extract_sentences(buffer)

                for sentence in sentences:
                    # 清理句子
                    clean_sentence = normalize_text(sentence)

                    # 过滤太短的内容
                    if len(clean_sentence) < 5:
                        continue

                    # 避免重复保存
                    sentence_key = clean_sentence.lower().strip()
                    if (sentence_key not in processed_sentences and
                        clean_sentence != last_complete_sentence):

                        processed_sentences.add(sentence_key)
                        last_complete_sentence = clean_sentence
                        print(f"Saving sentence: {clean_sentence}")
                        await save_txt(filename, clean_sentence)

            await asyncio.sleep(0.3)  # 稍微增加检查间隔，提高稳定性

        # 退出时保存未完成的句子（如果足够长且不重复）
        if incomplete_sentence:
            clean_incomplete = normalize_text(incomplete_sentence)
            if (len(clean_incomplete) > 5 and
                clean_incomplete.lower() not in processed_sentences and
                clean_incomplete != last_complete_sentence):
                print(f"Saving incomplete sentence: {clean_incomplete}")
                await save_txt(filename, clean_incomplete)

    except Exception as e:
        print(f"Exception caught: {e}")
        return False
        