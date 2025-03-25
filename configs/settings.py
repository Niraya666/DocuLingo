from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    API_BASE: str = Field("https://api.openai.com/v1", env="API_BASE") 
    VISION_MODEL: str = Field("Qwen/Qwen2-VL-72B-Instruct", env="VISION_MODEL")
    TEXT_MODEL: str = Field("Qwen/Qwen2.5-72B-Instruct", env="TEXT_MODEL")
    PROMPTS_DIR: str = "configs/prompts"
    MAX_WORKERS: int = Field(1, env="MAX_WORKERS")
    MAX_RETRIES: int = Field(3, env="MAX_RETRIES")
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
# print(settings)