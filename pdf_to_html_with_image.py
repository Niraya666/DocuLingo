import argparse
from src.core.llm_integration import LLMProcessor, ExtractionResult
from src.utils.pdf_processor import PDFProcessor
from src.utils.html_extractor import combine_html_contents
from configs.settings import settings
import os

def parse_args():
    parser = argparse.ArgumentParser(description='PDF转HTML工具')
    parser.add_argument('--pdf_path', type=str, default="assets/test.pdf",
                      help='Path to the input PDF file')
    parser.add_argument('--output_dir', type=str, default="assets/",
                      help='Directory to save intermediate images')
    parser.add_argument('--dpi', type=int, default=150,
                      help='DPI for PDF to image conversion')
    parser.add_argument('--max_tokens', type=int, default=4096,
                      help='Maximum tokens for LLM processing')
    parser.add_argument('--doc_type', type=str, default='qwen_vl_html',
                      help='Document type for processing')
    return parser.parse_args()

def main():
    args = parse_args()
    
    # 确保输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)
    images_dir = os.path.join(args.output_dir, 'pdf_images')
    os.makedirs(images_dir, exist_ok=True)
    
    processor = LLMProcessor(settings)
    pdf_processor = PDFProcessor(dpi=args.dpi)

    # PDF转图像
    image_paths = pdf_processor.pdf_to_images(
        pdf_path=args.pdf_path,
        output_dir=images_dir
    )

    # 处理图像
    page_contents = processor.process_images_batch(
        image_paths=image_paths,
        doc_type=args.doc_type,
        max_tokens=args.max_tokens,
    )

    # 合并HTML内容
    output_images_dir = os.path.join(args.output_dir, 'output_images')
    os.makedirs(output_images_dir, exist_ok=True)
    
    complete_html, all_image_info = combine_html_contents(
        page_contents,
        output_dir=output_images_dir,
        embed_base64=False
    )

    # 保存HTML文件
    html_output_path = os.path.join(args.output_dir, 'output.html')
    with open(html_output_path, "w", encoding="utf-8") as f:
        f.write(complete_html)

    print("处理完成！")
    print("\n图像信息:")
    for bbox, path in all_image_info:
        print(f"页码: {bbox.page}, 索引: {bbox.index}")
        print(f"bbox: {bbox.bbox}")
        print(f"保存路径: {path}\n")

if __name__ == '__main__':
    main()