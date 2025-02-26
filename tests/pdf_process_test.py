import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from src.utils.pdf_processor import PDFProcessor

pdf_processor = PDFProcessor()

pdf_processor.pdf_to_images(
    pdf_path="assets/2501.19393v2.pdf",
    output_dir="assets/test_images")