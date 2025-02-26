import fitz  # PyMuPDF
from pathlib import Path
import tempfile

class PDFProcessor:
    def __init__(self, dpi=300):
        self.dpi = dpi
        
    def pdf_to_images(self, pdf_path, output_dir):
        """将PDF转换为有序的PNG图片"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        doc = fitz.open(pdf_path)
        image_paths = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=self.dpi)
            img_path = Path(output_dir) / f"page_{page_num+1:03d}.png"
            pix.save(img_path)
            image_paths.append(str(img_path))
            
        return sorted(image_paths)
