# DocuLingo

[English](./README.md) | [中文](./docs/README-CN.md)


<a id="english"></a>

## 🌍 Overview

DocuLingo combines "Document" processing with "Linguistic" intelligence, offering a powerful end-to-end parsing solution based on multimodal large language models. It enhances RAG (Retrieval Augmented Generation) workflows by intelligently parsing and structuring content from various document formats, including accurate extraction of formulas, tables, and images. While primarily optimized for Qwen2.5-VL, DocuLingo supports integration with other Vision Language Models (VLMs) through flexible configuration options, bridging the gap between document understanding and language processing capabilities.

## ✨ Features

- **PDF to HTML Conversion**: Convert PDF documents to HTML format with preserved images
- **PDF to Markdown Conversion**: Transform PDF content into clean, structured markdown
- **Office Document Support**: Process DOCX, PPTX, and other office formats with proper image extraction
- **Intelligent Layout Analysis**: Maintains document structure including tables, lists, and formatting
- **Multi-language Support**: Works effectively with documents in multiple languages
- **Customizable Processing Parameters**: Adjust DPI, token limits, and other settings based on your needs

## 🔧 Installation

### Prerequisites

- Python 3.11 or higher
- LibreOffice (for processing Office documents)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Niraya666/DocuLingo.git
cd DocuLingo
```

2. Create a conda environment:
```bash
conda create -n doculingo python=3.11
conda activate doculingo
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

### Additional Dependencies

#### For Mac:
```bash
brew install --cask libreoffice
brew install poppler

# Create symbolic link
sudo ln -s /Applications/LibreOffice.app/Contents/MacOS/soffice /usr/local/bin/libreoffice
```

#### For Linux:
```bash
apt-get update
apt-get install -y libreoffice
apt-get install -y unoconv

# Install Chinese fonts
apt-get update
apt-get install -y fonts-wqy-zenhei fonts-wqy-microhei
apt-get install -y fonts-noto-cjk
```

## ⚙️ Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Configure your API keys and model preferences:
```
OPENAI_API_KEY=sk-xxx
API_BASE=your-api-base
VISION_MODEL=Qwen/Qwen2-VL-72B-Instruct
TEXT_MODEL=Qwen/Qwen2.5-72B-Instruct
```

## 📚 Usage

### Converting PDF to HTML with Images

```bash
python pdf_to_html_with_image.py \
    --pdf_path your-file-path \
    --output_dir path-to-save \
    --doc_type qwen_vl_html
```

### Converting Office Documents (PPTX, DOCX) to HTML with Images

```bash
python pdf_to_html_with_image.py \
    --pdf_path your-file-path \
    --output_dir path-to-save \
    --dpi 150 \
    --max_tokens 4096 \
    --doc_type qwen_vl_html \
    --convert_office
```

> **Note**: It's recommended to use absolute paths for file locations.

### Command Line Arguments

```
--pdf_path        Path to the input PDF or Office file
--output_dir      Directory to save intermediate images
--dpi             DPI for PDF to image conversion (default: 150)
--max_tokens      Maximum tokens for LLM processing (default: 4096)
--doc_type        Document type for processing (default: qwen_vl_html)
--convert_office  Enable Office format conversion using LibreOffice
```

### Concurrency and Retry Configuration

You can adjust the concurrency and retry parameters in `.env`:

```

MAX_RETRIES: 3    # Maximum number of retry attempts for failed requests
MAX_WORKERS: 2    # Maximum number of concurrent workers for parallel processing
```

## 🙏 Acknowledgements

- [Qwen2.5-VL](https://github.com/QwenLM/Qwen2.5-VL) for the powerful multimodal language model
