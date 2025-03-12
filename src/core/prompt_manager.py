# prompt_manager.py
from pathlib import Path
import yaml

class PromptManager:
    """提示词管理器,用于加载和管理不同类型文档的提示词模板"""
    
    def __init__(self, prompts_dir):
        """
        初始化提示词管理器
        Args:
            prompts_dir: 提示词模板文件目录
        Raises:
            FileNotFoundError: 目录不存在时抛出
        """
        if not Path(prompts_dir).exists():
            raise FileNotFoundError(f"提示词目录不存在: {prompts_dir}")
            
        self.prompts = {}
        for f in Path(prompts_dir).glob("*.yaml"):
            try:
                doc_type = f.stem  # 获取文件名(不含扩展名)作为doc_type
                with open(f) as file:
                    prompts_content = yaml.safe_load(file)
                    # 为每个stage添加doc_type前缀
                    prefixed_prompts = {
                        f"{doc_type}_{k}": v 
                        for k, v in prompts_content.items()
                    }
                    self.prompts.update(prefixed_prompts)
                    
                    # 如果是default文件,同时保存不带前缀的版本
                    if doc_type == "default":
                        self.prompts.update(prompts_content)
                        
            except yaml.YAMLError as e:
                print(f"加载{f}出错: {e}")
                continue

    def get_prompt(self, doc_type="default", stage="extraction"):
        """
        获取指定文档类型和阶段的提示词
        Args:
            doc_type: 文档类型,默认为default
            stage: 处理阶段,默认为extraction
        Returns:
            str: 提示词内容
        Raises:
            KeyError: 找不到对应提示词时抛出
        """
        key = f"{doc_type}_{stage}" if doc_type != "default" else stage
        if key not in self.prompts:
            if stage not in self.prompts:
                raise KeyError(f"找不到提示词: {key}")
            return self.prompts[stage]
        return self.prompts[key]
    

