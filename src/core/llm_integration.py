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
        
    async def async_process_images_concurrent(self, image_paths: List[str], doc_type="default", max_tokens=32768, json_mode=False,parse_type='markdown'):
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
                json_mode,
                parse_type
            )
            tasks.append(task)
            
        # 等待所有任务完成
        results = await asyncio.gather(*tasks)
        return results

    def process_images_batch(self, image_paths: List[str], doc_type="default", max_tokens=32768,json_mode=False,parse_type='markdown'):
        """批量处理图片的同步方法封装"""
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(
            self.async_process_images_concurrent(image_paths, doc_type, max_tokens,json_mode,parse_type)
        )
        return results

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def process_image(self, image_input, doc_type="default", max_tokens=32768, json_mode=False, parse_type=None)-> ExtractionResult:
        try:
            # 获取动态提示词
            system_prompt =  self.prompt_manager.get_prompt(doc_type, "system_prompt")
            prompt = self.prompt_manager.get_prompt(doc_type, "extraction")
            # 获取解析类型
            parse_type = self.prompt_manager.get_prompt(doc_type, "parse_type") if parse_type is None else parse_type
        
            
            # 处理不同类型的图像输入
            image_url = self._get_image_url(image_input)


            # 构建消息
            # 构建消息列表
            messages = []
            
            # system prompt
            messages = [{
                "role": "system",
                "content": system_prompt
            }]
            
            # 添加用户消息
            messages.append({
                "role": "user", 
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                            "detail": "high"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            })

            api_params = {
                "model": self.settings.VISION_MODEL,
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": max_tokens
            }
            
            if json_mode:
                api_params["response_format"] = {"type": "json_object"}
                
            response = self.client.chat.completions.create(**api_params)
            # return self._parse_response(response, parse_type=parse_type)
            parsed_response = self._parse_response(response, parse_type=parse_type)
            if doc_type == "qwen_vl_html":
                return self._format_page_content(image_input, parsed_response)
        
            return parsed_response
        
            
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
        

    def _get_image_url(self, image_input: str) -> str:
        """
        处理图像输入并返回可用的图像URL
        
        Args:
            image_input: 图像输入(URL或本地文件路径)
            
        Returns:
            str: 处理后的图像URL
            
        Raises:
            ValueError: 当输入格式不支持或文件类型不支持时抛出
        """
        if not isinstance(image_input, str):
            raise ValueError("图像输入必须是URL或本地文件路径")
            
        # 检查是否是URL
        if image_input.startswith(('http://', 'https://')):
            return image_input
            
        # 处理本地文件
        supported_formats = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp']
        file_ext = os.path.splitext(image_input)[1].lower()
        
        if file_ext not in supported_formats:
            raise ValueError(f"不支持的图像格式: {file_ext}")
            
        base64_image = self._load_image(image_input)
        return f"data:image/{file_ext[1:]};base64,{base64_image}"
    

    def _validate_response(self, json_str):
        """验证响应格式"""
        try:
            return ExtractionResult.model_validate_json(json_str)
        except Exception as e:
            raise ValueError(f"Invalid LLM response: {str(e)}")

    def _parse_response(self, response, parse_type='markdown'):
        """
        解析LLM响应，支持markdown、json和html格式
        
        Args:
            response: LLM的响应对象
            parse_type: 解析类型，支持 'markdown'、'json'和'html'，默认为 'markdown'
        
        Returns:
            str/dict: 根据parse_type返回提取的内容
        """
        try:
            content = response.choices[0].message.content
            
            # 定义解析器映射
            parsers = {
                'markdown': self._parse_code_block('markdown'),
                'json': self._parse_json,
                'html': self._parse_code_block('html')
            }
            
            parser = parsers.get(parse_type)
            return parser(content) if parser else content
            
        except Exception:
            return content

    def _parse_code_block(self, block_type):
        """
        通用代码块解析器工厂函数
        
        Args:
            block_type: 代码块类型（markdown/html）
        
        Returns:
            function: 解析函数
        """
        def parser(content):
            start = content.find(f"```{block_type}")
            end = content.rfind("```")
            
            if start == -1 or end == -1:
                return content.strip()
                
            start = content.find("\n", start) + 1
            return content[start:end].strip()
        
        return parser

    def _parse_json(self, content):
        """
        解析JSON内容
        
        Args:
            content: 需要解析的文本内容
        
        Returns:
            dict: 解析后的JSON对象
        """
        import json
        
        # 尝试从代码块中提取JSON
        json_content = self._parse_code_block('json')(content)
        
        try:
            return json.loads(json_content)
        except json.JSONDecodeError:
            # 如果解析失败，尝试直接解析整个内容
            try:
                return json.loads(content.strip())
            except json.JSONDecodeError:
                return content
            
    def _format_page_content(self, image_input: str, parsed_content: str) -> dict:
        """
        将解析后的内容和图片信息整合成统一格式
        
        Args:
            image_input: 输入图片路径
            parsed_content: 解析后的内容
            
        Returns:
            dict: 包含页码和内容信息的字典
        """
        try:
            # 从文件名中提取页码
            filename = Path(image_input).stem  # 获取不带扩展名的文件名
            # 尝试从文件名中提取数字
            page_num = ''.join(filter(str.isdigit, filename))
            page = int(page_num) if page_num else 1
            
            return {
                "page": page,
                "content": {
                    "html_content": parsed_content,
                    "original_image_path": image_input
                }
            }
        except Exception as e:
            # 如果解析失败，返回默认值
            return {
                "page": 1,
                "content": {
                    "html_content": parsed_content,
                    "original_image_path": image_input
                }
            }
    # def _test(self, doc_type):
    #     prompt_manager = PromptManager('configs/prompts')
    #     system_prompt =  prompt_manager.get_prompt(doc_type, "system_prompt")
    #     return system_prompt

