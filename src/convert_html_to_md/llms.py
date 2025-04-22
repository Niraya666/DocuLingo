from dotenv import load_dotenv
import os

from openai import OpenAI


load_dotenv()

api_key = os.getenv('API_KEY')
api_base = os.getenv('API_BASE')

client = OpenAI(
    api_key = api_key,
    base_url = api_base
    )

def unified_chat_completion(
    messages, 
    model,
    response_format=None,
    max_tokens=1500,
    temperature=0.0,
    top_p=1.0,
    repetition_penalty=None,
    guided_decoding_backend=None,
    **kwargs
):
    """
    统一的聊天完成函数，支持普通输出和结构化输出。
    
    Args:
        messages: 发送给模型的消息列表
        model: 使用的模型名称
        response_format: 结构化输出格式，传入 Pydantic BaseModel 启用结构化输出
        max_tokens: 生成的最大 token 数
        temperature: 控制随机性 (0.0 表示确定性输出)
        top_p: 控制采样多样性
        repetition_penalty: 重复惩罚参数
        guided_decoding_backend: 引导解码后端 (结构化输出时默认为 "outlines")
        **kwargs: 传递给 API 的其他参数
        
    Returns:
        API 响应对象
    """
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
    
    # 根据是否提供 response_format 决定使用哪个 API
    if response_format is not None:
        # 使用结构化输出 API
        params["response_format"] = response_format
        
        # 处理引导解码后端
        if guided_decoding_backend is not None:
            if "extra_body" not in params:
                params["extra_body"] = {}
            params["extra_body"]["guided_decoding_backend"] = guided_decoding_backend
        # elif "guided_decoding_backend" not in extra_body:
        #     # 如果使用结构化输出但未指定解码后端，默认使用 "outlines"
        #     if "extra_body" not in params:
        #         params["extra_body"] = {}
        #     params["extra_body"]["guided_decoding_backend"] = "outlines"
            
        return client.beta.chat.completions.parse(**params)
    else:
        # 使用标准聊天完成 API
        return client.chat.completions.create(**params)
