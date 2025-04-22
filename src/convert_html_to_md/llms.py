from dotenv import load_dotenv
import os

from openai import OpenAI
from typing import TypeVar, Optional, Union, Type, Any, Dict, List, Literal
from pydantic import BaseModel
import json


load_dotenv()

api_key = os.getenv('API_KEY')
api_base = os.getenv('API_BASE')

client = OpenAI(
    api_key = api_key,
    base_url = api_base
    )




T = TypeVar("T", bound=BaseModel)

def unified_chat_completion(
    messages: List[Dict[str, str]], 
    model: str,
    response_format: Optional[Type[T]] = None,
    provider: Optional[str] = None,
    return_format: Literal["pydantic", "dict", "json"] = "pydantic",
    max_tokens: int = 1500,
    temperature: float = 0.0,
    top_p: float = 1.0,
    repetition_penalty: Optional[float] = None,
    guided_decoding_backend: Optional[str] = None,
    client = None,
    **kwargs
) -> Any:
    """
    统一的聊天完成函数，支持多种模型提供商、普通输出和结构化输出。
    
    Args:
        messages: 发送给模型的消息列表
        model: 使用的模型名称
        response_format: 结构化输出格式，传入 Pydantic BaseModel 启用结构化输出
        provider: 模型提供商，可选值: "openai", "vllm", "openrouter"，若不提供则尝试从model名称推断
        return_format: 结构化数据的返回格式，可选值: "pydantic"(默认), "dict", "json"
        max_tokens: 生成的最大 token 数
        temperature: 控制随机性 (0.0 表示确定性输出)
        top_p: 控制采样多样性
        repetition_penalty: 重复惩罚参数
        guided_decoding_backend: 引导解码后端 (VLLM时默认为 "outlines")
        client: OpenAI客户端实例，如果不提供则使用全局client
        **kwargs: 传递给 API 的其他参数
        
    Returns:
        根据return_format返回API响应对象、Pydantic对象、字典或JSON字符串
    """
    # 如果未提供client，假设使用全局定义的client
    if client is None:
        try:
            from openai import OpenAI
            client = globals().get("client") or OpenAI()
        except ImportError:
            raise ImportError("OpenAI客户端未找到。请安装openai包或提供client参数。")
    
    # 如果未提供provider，尝试从model名称推断
    if provider is None:
        if model.startswith(("gpt-", "claude-", "text-", "mistral-", "dall-e")):
            provider = "openai"
        elif "openrouter" in model or "/" in model:  # openrouter经常使用带命名空间的模型名
            provider = "openrouter"
        else:
            # 默认使用openai作为provider
            provider = "openai"
    
    # 构建基本参数
    params = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
    }
    
    # 合并其他参数
    params.update({k: v for k, v in kwargs.items() if k not in ["extra_body"]})
    
    # 处理 extra_body 参数
    extra_body = kwargs.get("extra_body", {}).copy() if "extra_body" in kwargs else {}
    
    # 添加重复惩罚参数（如果提供）
    if repetition_penalty is not None:
        extra_body["repetition_penalty"] = repetition_penalty
    
    # 如果 extra_body 不为空，添加到参数中
    if extra_body:
        params["extra_body"] = extra_body
    
    # 根据provider和是否提供response_format决定使用哪个API
    if response_format is not None:
        # 使用结构化输出
        if provider == "vllm":
            # VLLM的结构化输出方式
            params["response_format"] = response_format
            
            # 处理引导解码后端
            if guided_decoding_backend is not None:
                if "extra_body" not in params:
                    params["extra_body"] = {}
                params["extra_body"]["guided_decoding_backend"] = guided_decoding_backend
            else:
                # 默认使用"outlines"作为引导解码后端
                if "extra_body" not in params:
                    params["extra_body"] = {}
                params["extra_body"]["guided_decoding_backend"] = "outlines"
                
            response = client.beta.chat.completions.parse(**params)
            
            # 根据return_format处理返回结果
            content = response.choices[0].message.content
            if return_format == "dict":
                return content.model_dump()
            elif return_format == "json":
                return content.model_dump_json()
            else:  # "pydantic"
                return content
            
        elif provider == "openai":
            # OpenAI的结构化输出方式
            params["response_format"] = response_format
            response = client.beta.chat.completions.parse(**params)
            
            # 根据return_format处理返回结果
            content = response.choices[0].message.content
            if return_format == "dict":
                return content.model_dump()
            elif return_format == "json":
                return content.model_dump_json()
            else:  # "pydantic"
                return content
            
        elif provider == "openrouter":
            # OpenRouter的结构化输出方式
            schema = {
                "type": "json_schema", 
                "json_schema": {
                    "name": response_format.__name__, 
                    "schema": response_format.model_json_schema()
                }
            }
            params["response_format"] = schema
            
            response = client.chat.completions.create(**params)
            # 获取返回的JSON字符串
            json_str = response.choices[0].message.content
            
            # 根据return_format处理返回结果
            if return_format == "json":
                return json_str
            elif return_format == "dict":
                return json.loads(json_str)
            else:  # "pydantic"
                return response_format.model_validate_json(json_str)
    else:
        # 普通聊天完成
        return client.chat.completions.create(**params)


# 实用的辅助函数，获取结构化数据
def get_structured_data(
    messages: List[Dict[str, str]],
    schema_class: Type[T],
    model: str,
    return_format: Literal["pydantic", "dict", "json"] = "dict",  # 默认返回字典
    provider: Optional[str] = None,
    **kwargs
) -> Union[T, Dict, str]:
    """
    简化的函数，直接返回结构化数据，可选返回格式
    
    Args:
        messages: 发送给模型的消息列表
        schema_class: Pydantic模型类
        model: 使用的模型名称
        return_format: 返回格式：pydantic, dict 或 json
        provider: 模型提供商
        **kwargs: 其他参数
        
    Returns:
        结构化数据（Pydantic对象、字典或JSON字符串）
    """
    return unified_chat_completion(
        messages=messages,
        model=model,
        response_format=schema_class,
        provider=provider,
        return_format=return_format,
        **kwargs
    )


