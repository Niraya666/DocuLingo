import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from src.utils.ppt_processor import convert_ppt_to_pdf, convert_pdf_to_images

convert_ppt_to_pdf("assets/test.ppt", "assets/test_pdf")
# convert_pdf_to_images("assets/test_pdf/test.pdf", "assets/test_images") 

