# DocuLingo
<a id="中文"></a>

## 🌍 项目概述

DocuLingo 将"文档(Document)"处理与"语言(Linguistic)"智能相结合，提供了一个基于多模态大语言模型的端到端解析方案。它通过智能解析和结构化各种文档格式中的内容，包括精确提取公式、表格和图片，从而增强 RAG (检索增强生成) 工作流。虽然主要针对 Qwen2.5-VL 模型优化，DocuLingo 支持通过灵活的配置选项接入其他视觉语言模型(VLMs)，实现了文档理解与语言处理能力的无缝衔接。

## ✨ 特点功能

- **PDF 转 HTML 转换**：将 PDF 文档转换为 HTML 格式，同时保留图像
- **PDF 转 Markdown 转换**：将 PDF 内容转换为清晰、结构化的 markdown
- **Office 文档支持**：处理 DOCX、PPTX 等 Office 格式，并正确提取图像
- **智能布局分析**：维持文档结构，包括表格、列表和格式
- **多语言支持**：有效处理多种语言的文档
- **可自定义处理参数**：根据需求调整 DPI、令牌限制等设置

## 🔧 安装步骤

### 前提条件

- Python 3.11 或更高版本
- LibreOffice（用于处理 Office 文档）

### 设置

1. 克隆仓库：
```bash
git clone https://github.com/your-username/DocuLingo.git
cd DocuLingo
```

2. 创建 conda 环境：
```bash
conda create -n doculingo python=3.11
conda activate doculingo
```

3. 安装所需包：
```bash
pip install -r requirements.txt
```

### 额外依赖

#### Mac 系统：
```bash
brew install --cask libreoffice
brew install poppler

# 创建符号链接
sudo ln -s /Applications/LibreOffice.app/Contents/MacOS/soffice /usr/local/bin/libreoffice
```

#### Linux 系统：
```bash
apt-get update
apt-get install -y libreoffice
apt-get install -y unoconv

# 安装中文字体
apt-get update
apt-get install -y fonts-wqy-zenhei fonts-wqy-microhei
apt-get install -y fonts-noto-cjk
```

## ⚙️ 配置

1. 复制示例环境文件：
```bash
cp .env.example .env
```

2. 配置 API 密钥和模型偏好：
```
OPENAI_API_KEY=sk-xxx
API_BASE=your-api-base
VISION_MODEL=Qwen/Qwen2-VL-72B-Instruct
TEXT_MODEL=Qwen/Qwen2.5-72B-Instruct
```

## 📚 使用方法

### 将 PDF 转换为 HTML 并包含图像

```bash
python pdf_to_html_with_image.py \
    --pdf_path your-file-path \
    --output_dir path-to-save \
    --doc_type qwen_vl_html
```

### 将 Office 文档（PPTX、DOCX）转换为 HTML 并包含图像

```bash
python pdf_to_html_with_image.py \
    --pdf_path your-file-path \
    --output_dir path-to-save \
    --dpi 150 \
    --max_tokens 4096 \
    --doc_type qwen_vl_html \
    --convert_office
```

> **注意**：建议使用文件位置的绝对路径。

### 命令行参数

```
--pdf_path        输入的PDF或Office文件路径
--output_dir      保存中间图像的目录
--dpi             PDF转图像的DPI（默认：150）
--max_tokens      LLM处理的最大令牌数（默认：4096）
--doc_type        处理的文档类型（默认：qwen_vl_html）
--convert_office  启用使用LibreOffice的Office格式转换
```

### 并发和重试配置

你可以在 `configs/settings.yaml` 中调整并发和重试参数：

```yaml
# configs/settings.yaml
processing:
  max_retries: 3    # 失败请求的最大重试次数
  max_workers: 2    # 并行处理的最大工作线程数
```

## 🙏 致谢

- [Qwen2.5-VL](https://github.com/QwenLM/Qwen2.5-VL) 提供强大的多模态语言模型