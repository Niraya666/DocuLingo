import asyncio
import argparse
from pathlib import Path
from src.utils.pdf_processor import PDFProcessor
from src.core.llm_integration import LLMProcessor
from configs.settings import settings
from src.utils.exporter import save_as_markdown

def parse_arguments():
    parser = argparse.ArgumentParser(description='PDF to Markdown converter using LLM')
    parser.add_argument('--pdf_path', type=str, default="assets/test.pdf",
                      help='Path to the input PDF file')
    parser.add_argument('--output_dir', type=str, default="assets/test_images",
                      help='Directory to save intermediate images')
    parser.add_argument('--output_md', type=str, default="assets/output.md",
                      help='Path to save the output markdown file')
    parser.add_argument('--dpi', type=int, default=300,
                      help='DPI for PDF to image conversion')
    parser.add_argument('--max_tokens', type=int, default=4096,
                      help='Maximum tokens for LLM processing')
    parser.add_argument('--doc_type', type=str, default="default",
                      help='Document type for processing')
    parser.add_argument('--json_mode', action='store_true',
                      help='Enable JSON mode for output')
    parser.add_argument('--parse_type', type=str, default='markdown',
                      help='Parse type for output (markdown/json)')
    
    return parser.parse_args()

def ensure_directory(path):
    """确保目录存在"""
    Path(path).parent.mkdir(parents=True, exist_ok=True)

def run(args):
    # 确保输出目录存在
    ensure_directory(args.output_md)
    ensure_directory(Path(args.output_dir))

    # 初始化 PDF 处理器
    pdf_processor = PDFProcessor(dpi=args.dpi)
    
    # PDF 转换为图片
    image_paths = pdf_processor.pdf_to_images(
        pdf_path=args.pdf_path,
        output_dir=args.output_dir
    )   

    # 初始化 LLM 处理器
    processor = LLMProcessor(settings)
    
    # 使用同步方法批量处理
    results = processor.process_images_batch(
        image_paths=image_paths, 
        doc_type=args.doc_type,
        max_tokens=args.max_tokens,
        json_mode=args.json_mode,
        parse_type=args.parse_type
    )
    
    # 合并结果
    content = ""
    for result in results:
        content += str(result) + "\n\n---\n\n"

    # 保存结果
    save_as_markdown(content, args.output_md)
    print(f"Processing complete. Output saved to {args.output_md}")

if __name__ == "__main__":
    args = parse_arguments()
    run(args)
