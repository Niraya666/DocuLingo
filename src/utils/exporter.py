import os
from typing import List
def save_as_markdown(content: str, file_name: str) -> None:
    """
    将给定的字符串内容保存为一个Markdown文件。

    :param content: 要保存到Markdown文件的字符串内容。
    :param file_name: 目标Markdown文件的文件名（包括路径）。
    """
    try:
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Markdown 文件已成功保存为 '{file_name}'")
    except Exception as e:
        print(f"保存文件时发生错误: {e}")

def save_as_jsonl(content: List, file_name: str) -> None:
    """
    将给定的字符串内容保存为一个JSONL文件。

    :param content: 要保存到JSONL文件的字符串内容。
    :param file_name: 目标JSONL文件的文件名（包括路径）。
    """ 
    try:
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"JSONL 文件已成功保存为 '{file_name}'")
    except Exception as e:
        print(f"保存文件时发生错误: {e}")   

def save_as_json(content: List, file_name: str) -> None:
    """
    将给定的字符串内容保存为一个JSON文件。

    :param content: 要保存到JSON文件的字符串内容。
    :param file_name: 目标JSON文件的文件名（包括路径）。
    """ 
    try:
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"JSON 文件已成功保存为 '{file_name}'")
    except Exception as e:
        print(f"保存文件时发生错误: {e}")   