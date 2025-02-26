import os
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

