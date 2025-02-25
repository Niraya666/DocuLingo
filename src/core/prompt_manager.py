from pathlib import Path
import yaml

class PromptManager:
    def __init__(self, prompts_dir):
        self.prompts = {}
        for f in Path(prompts_dir).glob("*.yaml"):
            with open(f) as file:
                self.prompts.update(yaml.safe_load(file))

    def get_prompt(self, doc_type, stage="extraction"):
        """获取指定文档类型和阶段的提示词"""
        key = f"{doc_type}_{stage}" if doc_type != "default" else stage
        return self.prompts.get(key, self.prompts[stage])
