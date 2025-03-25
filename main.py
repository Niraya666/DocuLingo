import argparse
import pathlib

from src.core.llm_integration import LLMProcessor
from src.utils.pdf_processor import PDFProcessor
from src.utils.ppt_processor import convert_ppt_to_pdf
from src.utils.html_extractor import combine_html_contents
from src.utils.exporter import save_as_markdown
from configs.settings import settings
import os

def parse_args():
    parser = argparse.ArgumentParser(description='PDF/Office文档转HTML工具')
    parser.add_argument('--pdf_path', type=str, default="assets/test.pdf",
                      help='Path to the input PDF or Office file')
    parser.add_argument('--output_dir', type=str, default="assets/",
                      help='Directory to save intermediate images')
    parser.add_argument('--dpi', type=int, default=150,
                      help='DPI for PDF to image conversion')
    parser.add_argument('--max_tokens', type=int, default=4096,
                      help='Maximum tokens for LLM processing')
    parser.add_argument('--doc_type', type=str, default='qwen_vl_html',
                      help='Document type for processing')
    parser.add_argument('--convert_office', action='store_true',
                      help='Enable Office format conversion using LibreOffice')
    return parser.parse_args()

def main():
    args = parse_args()
    
    # 确保输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)
    images_dir = os.path.join(args.output_dir, 'pdf_images')
    os.makedirs(images_dir, exist_ok=True)
    
    # 检查文件类型，处理Office文档
    input_file_path = args.pdf_path
    file_extension = pathlib.Path(input_file_path).suffix.lower()
    
    # 如果是PPTX/PPT格式且启用了Office转换选项
    if args.convert_office and file_extension in ['.pptx', '.ppt', '.doc', '.docx', '.xls', '.xlsx']:
        from src.utils.ppt_processor import convert_ppt_to_pdf
        pdf_output_path = os.path.join(args.output_dir, os.path.basename(input_file_path).replace(file_extension, '.pdf'))
        input_file_path = convert_ppt_to_pdf(input_file_path, pdf_output_path)
        print(f"已将 {file_extension} 文件转换为 PDF: {input_file_path}")
    
    processor = LLMProcessor(settings)
    pdf_processor = PDFProcessor(dpi=args.dpi)

    # PDF转图像
    image_paths = pdf_processor.pdf_to_images(
        pdf_path=input_file_path,
        output_dir=images_dir
    )

    # 处理图像
    page_contents = processor.process_images_batch(
        image_paths=image_paths,
        doc_type=args.doc_type,
        max_tokens=args.max_tokens,
    )
    if args.doc_type=='qwen_vl_html':
        # 合并HTML内容
        output_images_dir = os.path.join(args.output_dir, 'output_images')
        os.makedirs(output_images_dir, exist_ok=True)
        
        complete_html, all_image_info = combine_html_contents(
            page_contents,
            output_dir=output_images_dir,
            embed_base64=False
        )

        # # 保存HTML文件
        # html_output_path = os.path.join(args.output_dir, 'output.html')
        # with open(html_output_path, "w", encoding="utf-8") as f:
        #     f.write(complete_html)
        # 获取输入文件的基本名称（不含扩展名）并添加.html扩展名
        input_filename = os.path.splitext(os.path.basename(args.pdf_path))[0]
        html_output_path = os.path.join(args.output_dir, f"{input_filename}.html")
        
        with open(html_output_path, "w", encoding="utf-8") as f:
            f.write(complete_html)

        print("处理完成！")
        print("\n图像信息:")
        for bbox, path in all_image_info:
            print(f"页码: {bbox.page}, 索引: {bbox.index}")
            print(f"bbox: {bbox.bbox}")
            print(f"保存路径: {path}\n")

    else:
        content = ""
        for result in page_contents:
            content += str(result) + "\n\n---\n\n"

        # 保存结果
        input_filename = os.path.splitext(os.path.basename(args.pdf_path))[0]
        md_output_path = os.path.join(args.output_dir, f"{input_filename}.md")
        save_as_markdown(content, md_output_path)
        print("处理完成！")

if __name__ == '__main__':
    main()