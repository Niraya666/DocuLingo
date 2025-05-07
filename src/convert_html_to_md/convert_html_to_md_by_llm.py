from llms import unified_chat_completion
from html_chunking import chunk_html_by_headings
from utils import html_cleaning

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import json
import os
from tqdm import tqdm
import time

class ChunkInfo(BaseModel):
    chunk_id: int 
    summary: str 
    key_findings: str
    keywords: list
    original_page_id: list[int]

model_name = "openai/gpt-4.1-mini"

def convert_to_md_by_llm(html_content: str, model_name: str, client=None, max_retry: int = 3) -> str:
    """
    将HTML内容转换为Markdown格式
    
    Args:
        html_content: 要转换的HTML内容
        model_name: 使用的模型名称
        client: API客户端实例
        max_retry: 最大重试次数
        
    Returns:
        转换后的Markdown内容
    """
    messages = [
        {"role": "system", "content": "Extract the main content from the given HTML and convert it to clean, well-formatted Markdown. Preserve structure, headings, lists, and important formatting."},
        {"role": "user", "content": f"```html\n{html_content}\n```"}
    ]

    for attempt in range(max_retry):
        try:
            res = unified_chat_completion(
                messages=messages, 
                model=model_name, 
                max_tokens=min(4000, len(html_content) + 1000),  # 限制token数量但给予足够空间
                client=client
            )
            return res.choices[0].message.content
        except Exception as e:
            if attempt < max_retry - 1:
                print(f"Error converting HTML to Markdown: {e}. Retrying ({attempt+1}/{max_retry})...")
                time.sleep(2)  # 添加延迟避免频率限制
            else:
                print(f"Failed after {max_retry} attempts: {e}")
                return f"ERROR: Could not convert HTML to Markdown: {str(e)}"

def extract_info_by_llm(
    index: int, 
    html_content: str, 
    model_name: str, 
    client=None, 
    max_retry: int = 3
) -> Dict[str, Any]:
    """
    从HTML内容中提取结构化信息
    
    Args:
        index: 块ID
        html_content: HTML内容
        model_name: 使用的模型名称
        client: API客户端实例
        max_retry: 最大重试次数
        
    Returns:
        提取的结构化信息（字典格式）
    """
    system_prompt = """Please summarize the following text. The summary should focus on the main findings, recommendations, and any key data point. The summary should be concise, capturing the essential information, and no longer than 100 words. Additionally, extract the following metadata:
    - key findings: The main findings or conclusions of the content.
    - keywords: 3-5 keywords that capture the main themes of the content.
    - original_page_id: where the original contents belong 
    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"chunk_id: {index}\n```html\n{html_content}\n```"}
    ]

    for attempt in range(max_retry):
        try:
            res = unified_chat_completion(
                messages=messages, 
                model=model_name, 
                response_format=ChunkInfo, 
                max_tokens=min(2000, len(html_content) // 2),  # 调整token数量
                return_format="dict",
                client=client
            )
            # 确保chunk_id正确
            if isinstance(res, dict) and "chunk_id" in res:
                res["chunk_id"] = index
            return res
        except Exception as e:
            if attempt < max_retry - 1:
                print(f"Error extracting info from chunk {index}: {e}. Retrying ({attempt+1}/{max_retry})...")
                time.sleep(2)
            else:
                print(f"Failed to extract info from chunk {index} after {max_retry} attempts: {e}")
                return {
                    "chunk_id": index,
                    "summary": f"Error: {str(e)}",
                    "key_findings": "Could not extract information",
                    "keywords": ["error", "processing_failed"]
                }

def process_html_chunks(
    chunks: List[str],
    model_name: str,
    output_dir: str = "output",
    markdown_filename: str = "content.md",
    json_filename: str = "metadata.json",
    client = None,
    process_markdown: bool = True,
    process_info: bool = True
) -> None:
    """
    处理HTML块列表，转换为Markdown并提取信息
    
    Args:
        chunks: HTML块列表
        model_name: 使用的模型名称
        output_dir: 输出目录
        markdown_filename: 输出的Markdown文件名
        json_filename: 输出的JSON文件名
        client: API客户端
        process_markdown: 是否处理Markdown转换
        process_info: 是否处理信息提取
    """
    # 创建输出目录（如果不存在）
    os.makedirs(output_dir, exist_ok=True)
    
    markdown_results = []
    info_results = []
    
    # 处理所有HTML块
    for i, chunk in enumerate(tqdm(chunks, desc="Processing HTML chunks")):
        # 转换为Markdown（如果需要）
        if process_markdown:
            print(f"\nProcessing chunk {i+1}/{len(chunks)} for Markdown conversion...")
            md_content = convert_to_md_by_llm(chunk, model_name, client)
            markdown_results.append(md_content)
            
            # 每个块都保存一次，避免中途失败丢失所有结果
            with open(os.path.join(output_dir, markdown_filename), 'w', encoding='utf-8') as f:
                f.write("\n\n---\n\n".join(markdown_results))
        
        # 提取信息（如果需要）
        if process_info:
            print(f"Processing chunk {i+1}/{len(chunks)} for information extraction...")
            info = extract_info_by_llm(i, chunk, model_name, client)
            info_results.append(info)
            
            # 每个块都保存一次JSON
            with open(os.path.join(output_dir, json_filename), 'w', encoding='utf-8') as f:
                json.dump(info_results, f, indent=2, ensure_ascii=False)
    
    print(f"\nProcessing complete. Results saved to {output_dir}/{markdown_filename} and {output_dir}/{json_filename}")


if __name__ == '__main__':

    with open('../../assets/test.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    html = html_cleaning(html_content, clean_svg = True, clean_base64 = True)

    # 使用h2标签作为分块标志
    chunks,chunk_start_pages = chunk_html_by_headings(html_content, heading_tags=["h2", "h3", "table"])

    # 打印分块结果
    print(f"分成了{len(chunks)}个块")
    for i, chunk in enumerate(chunks):
        print(f"块 {i+1} 长度: {len(chunk)} 字符")
    # index = 0
    # HTML_CONENT = chunks[index]

    # print(chunks)

    process_html_chunks(
        chunks=chunks,
        model_name=model_name,
        output_dir="./output",
        markdown_filename="converted_content.md",
        json_filename="content_metadata.json"
    )






