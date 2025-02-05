from openai import OpenAI
from .base_client import BaseLLMClient
from configs.settings import settings
class OpenAIClient(BaseLLMClient):
    def __init__(self, settings):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.API_BASE
        )
    
    def vision_request(self, messages, **kwargs):
        return self.client.chat.completions.create(
            model=settings.VISION_MODEL,
            messages=messages,
            **kwargs
        )
    
    def text_request(self, messages, **kwargs):
        return self.client.chat.completions.create(
            model=settings.TEXT_MODEL,
            messages=messages,
            **kwargs
        )
