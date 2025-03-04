import os
from openai import OpenAI
from pydantic import BaseModel
import base64
import yaml
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential
from src.core.api_clients.openai_client import OpenAIClient
from src.core.prompt_manager import PromptManager
from concurrent.futures import ThreadPoolExecutor
from typing import List
import asyncio
# 定义输出结构
class ExtractionResult(BaseModel):
    content: str
    metadata: dict
    document_type: str

class RefinementResult(BaseModel):
    refined_content: str
    changes_made: list[str]

class LLMProcessor:
    def __init__(self, settings):
        self.settings = settings
        self.prompt_manager = PromptManager(settings.PROMPTS_DIR)
        self.client = self._init_client(settings)
        # 创建线程池
        self.executor = ThreadPoolExecutor(settings.MAX_WORKERS)
        
    
    def _init_client(self, settings):
    
        
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.API_BASE
        )
        return self.client
        
    async def async_process_images_concurrent(self, image_paths: List[str], doc_type="default", max_tokens=32768, json_mode=False):
        """并发处理多个图片"""
        loop = asyncio.get_event_loop()
        tasks = []
        
        for image_path in image_paths:
            # 使用线程池执行API调用
            task = loop.run_in_executor(
                self.executor,
                self.process_image,
                image_path,
                doc_type,
                max_tokens,
                json_mode
            )
            tasks.append(task)
            
        # 等待所有任务完成
        results = await asyncio.gather(*tasks)
        return results

    def process_images_batch(self, image_paths: List[str], doc_type="default", max_tokens=32768,json_mode=False):
        """批量处理图片的同步方法封装"""
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(
            self.async_process_images_concurrent(image_paths, doc_type, max_tokens,json_mode)
        )
        return results

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def process_image(self, image_path, doc_type="default",max_tokens=32768,json_mode=False)-> ExtractionResult:
        try:
            # 获取动态提示词
            prompt = self.prompt_manager.get_prompt(doc_type, "extraction")
            base64_image = self._load_image(image_path)
            # 构建消息(示例)
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail":"high"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }]

            api_params = {
                "model": self.settings.VISION_MODEL,
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": max_tokens
            }
            if json_mode:
                api_params["response_format"] = {"type": "json_object"}
            response = self.client.chat.completions.create(**api_params)
            
            
            return self._parse_response(response)
        except Exception as e:
            raise ValueError(f"处理图片失败: {str(e)}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def refine_text(
        self,
        text: str,
        doc_type: str = "default",
        max_tokens: int = 4096
    )-> RefinementResult:
        """
        文本润色方法
        """
        try:
            # 1. 获取润色提示词
            prompt = self.prompt_manager.get_prompt(
                doc_type=doc_type,
                stage="refinement"
            )
            
            # 2. 构建消息
            messages = [{
                "role": "user",
                "content": f"{prompt}\n\n---\n\n{text}"
            }]
            
            # 3. 调用文本API
            response = self.client.chat.completions.create(
                model=self.settings.TEXT_MODEL,
                messages=messages,
                temperature=0.1,
                max_tokens=max_tokens
            )
            
            # 4. 解析响应
            return self._parse_response(response)
        except Exception as e:
            raise ValueError(f"润色失败: {str(e)}")

    def _load_image(self, image_path: str) -> str:
        """加载并编码图片"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
            
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    def _validate_response(self, json_str):
        """验证响应格式"""
        try:
            return ExtractionResult.model_validate_json(json_str)
        except Exception as e:
            raise ValueError(f"Invalid LLM response: {str(e)}")

    def _parse_response(self, response):
        """
        解析LLM响应，提取markdown内容并验证
        
        Args:
            response: LLM的响应对象
        
        Returns:
            str: 提取的markdown内容
        
        Raises:
            ValueError: 当响应格式无效或未找到markdown内容时
        """
        try:
            # 获取响应文本
            content = response.choices[0].message.content
            
            # 查找markdown代码块
            markdown_start = content.find("```markdown")
            markdown_end = content.rfind("```")
            
            # 验证是否找到markdown标记
            if markdown_start == -1 or markdown_end == -1:
                # 如果没有markdown标记，直接返回整个内容
                return content.strip()
                
            # 提取markdown内容（去除```markdown和```标记）
            markdown_start = content.find("\n", markdown_start) + 1
            markdown_content = content[markdown_start:markdown_end].strip()
            
            # 基本验证
            if not markdown_content:
                raise ValueError("提取的markdown内容为空")
                
            # 检查markdown内容的基本结构
            if "##" in markdown_content or "#" in markdown_content:
                # 包含标题标记，可能是有效的markdown
                pass
            
            return markdown_content
            
        except Exception as e:
            raise ValueError(f"解析响应失败: {str(e)}")