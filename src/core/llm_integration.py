from openai import OpenAI
from pydantic import BaseModel
import base64
import yaml
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential
from src.core.api_clients.openai_client import OpenAIClient
from src.core.prompt_manager import PromptManager
# 定义输出结构
class ExtractionResult(BaseModel):
    content: str
    metadata: dict
    document_type: str

class LLMProcessor:
    def __init__(self, settings):
        self.settings = settings
        self.prompt_manager = PromptManager(settings.PROMPTS_DIR)
        self.client = self._init_client(settings)
    
    def _init_client(self, settings):
    
        # return OpenAIClient(settings)
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.API_BASE
        )
        return self.client
        
   
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def process_image(self, image_path, doc_type="default"):
        # 获取动态提示词
        prompt = self.prompt_manager.get_prompt(doc_type, "extraction")
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
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

       
        response = self.client.chat.completions.create(
            model=self.settings.VISION_MODEL,
            messages=messages,
        )

        
        # return response
        return self._parse_response(response)
    
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
    
    def post_process(self, text, document_type):
        """二次润色处理"""
        prompt = self._get_postprocess_prompt(document_type)
        response = self.client.chat.completions.create(
            model=self.config["openai"]["text_model"],
            messages=[{
                "role": "user",
                "content": prompt + "\n\nText to refine:\n" + text
            }],
            temperature=0.2
        )
        return response.choices[0].message.content
    
    def _get_postprocess_prompt(self, doc_type):
        """获取不同文档类型的处理提示"""
        prompts = {
            "paper": "请将以下学术论文内容转换为规范的Markdown格式,修正排版错误,保留数学公式和引用格式。",
            "textbook": "请将教材内容转换为结构清晰的Markdown,确保章节标题、图表说明格式正确。",
            "default": "请将以下文本内容进行整理和润色,保持原有信息的同时优化可读性。"
        }
        return prompts.get(doc_type, prompts["default"])
