import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from src.utils.pdf_processor import PDFProcessor
from src.core.llm_integration import LLMProcessor
from src.core.prompt_manager import PromptManager
from configs.settings import settings
from src.utils.markdown_exporter import save_as_markdown

pdf_processor = PDFProcessor(dpi=300)
image_paths = pdf_processor.pdf_to_images(
    pdf_path="assets/test.pdf",
    output_dir="assets/test_images",
   
)   


processor = LLMProcessor(settings)
results = []
for image_path in image_paths:
    print(image_path)
    result = processor.process_image(image_path,max_tokens=4096)
    # refined = processor.refine_text(
    #     text=result,   
    #     doc_type="paper"
    # )
    # print(refined)
    results.append(result)

content = ""
for result in results:
    content += result + "\n\n---\n\n"


save_as_markdown(content, 'assets/output.md')




