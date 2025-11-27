import fitz  # pymupdf
import sys
from typing import Literal
import math

class PDFRouter:
    """
    Routes PDFs to the appropriate extraction pipeline based on their content characteristics.
    Uses enhanced heuristics for more accurate classification.
    """

    def _calculate_text_quality_score(self, doc) -> float:
        """
        Calculate a quality score for text content to distinguish between 
        readable text and OCR artifacts/gibberish.
        
        Returns:
            float: Score between 0-1, where higher means better quality text
        """
        total_chars = 0
        valid_word_chars = 0
        space_count = 0
        
        # Check first few pages
        pages_to_check = min(3, len(doc))
        
        for i in range(pages_to_check):
            page = doc[i]
            text = page.get_text()
            
            total_chars += len(text)
            space_count += text.count(' ')
            
            # Count alphanumeric characters (good indicator of real text)
            for char in text:
                if char.isalnum():
                    valid_word_chars += 1
        
        if total_chars == 0:
            return 0.0
            
        # Calculate ratios
        alpha_ratio = valid_word_chars / total_chars if total_chars > 0 else 0
        space_ratio = space_count / total_chars if total_chars > 0 else 0
        
        # Weighted score - prioritize alpha ratio but consider spacing too
        quality_score = (alpha_ratio * 0.7) + (space_ratio * 0.3)
        
        return quality_score

    def _analyze_image_content(self, doc) -> dict:
        """
        Analyze image content to detect scanned documents.
        
        Returns:
            dict: Contains image analysis metrics
        """
        total_pages = len(doc)
        pages_to_check = min(3, total_pages)
        
        image_count = 0
        total_images_area = 0.0
        total_page_area = 0.0
        
        for i in range(pages_to_check):
            page = doc[i]
            page_rect = page.rect
            total_page_area += page_rect.get_area()
            
            # Get images on page
            images = page.get_images()
            image_count += len(images)
            
            # Calculate total image area
            for img in images:
                # Get image bbox
                try:
                    img_bbox = page.get_image_bbox(img)
                    total_images_area += img_bbox.get_area()
                except:
                    # If we can't get bbox, estimate
                    total_images_area += page_rect.get_area() * 0.5  # Assume 50% coverage
        
        return {
            'image_count': image_count,
            'images_area_ratio': total_images_area / total_page_area if total_page_area > 0 else 0,
            'avg_images_per_page': image_count / pages_to_check if pages_to_check > 0 else 0
        }

    def identify_type(self, pdf_path: str) -> Literal["NATIVE", "SCANNED"]:
        """
        Identifies if a PDF is NATIVE (selectable text) or SCANNED (image-based).
        Uses multiple heuristics for more accurate detection.
        
        Args:
            pdf_path: Path to the PDF file.
            
        Returns:
            'NATIVE' or 'SCANNED'
        """
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            if total_pages == 0:
                return "SCANNED"

            total_text_area = 0.0
            total_page_area = 0.0
            
            # Check first few pages to save time on large docs
            pages_to_check = min(5, total_pages)
            
            for i in range(pages_to_check):
                page = doc[i]
                page_rect = page.rect
                total_page_area += page_rect.get_area()
                
                # Get all text blocks
                text_blocks = page.get_text("blocks")
                for block in text_blocks:
                    # block is (x0, y0, x1, y1, "text", block_no, block_type)
                    # block_type 0 is text
                    if block[6] == 0:
                        r = fitz.Rect(block[:4])
                        total_text_area += r.get_area()

            if total_page_area == 0:
                doc.close()
                return "SCANNED"

            text_density = (total_text_area / total_page_area) * 100
            
            # Get text quality score
            text_quality = self._calculate_text_quality_score(doc)
            
            # Analyze image content
            image_analysis = self._analyze_image_content(doc)
            
            doc.close()
            
            # Enhanced decision logic:
            # 1. Low text density strongly suggests scanned
            if text_density < 2.0:
                return "SCANNED"
            
            # 2. High text density with poor quality suggests OCR artifacts
            if text_density > 5.0 and text_quality < 0.3:
                return "SCANNED"
            
            # 3. Significant image content suggests scanned
            if image_analysis['images_area_ratio'] > 0.7:
                return "SCANNED"
            
            # 4. Very high text density with good quality suggests native
            if text_density > 10.0 and text_quality > 0.4:
                return "NATIVE"
            
            # 5. Moderate text density with good quality suggests native
            if text_density > 3.0 and text_quality > 0.5:
                return "NATIVE"
            
            # Default to scanned for safety
            return "SCANNED"

        except Exception as e:
            print(f"Error identifying PDF type: {e}", file=sys.stderr)
            return "SCANNED"  # Fallback

if __name__ == "__main__":
    # Simple test block
    import os
    
    # Create a dummy PDF for testing if one doesn't exist
    test_pdf_path = "test_router.pdf"
    if not os.path.exists(test_pdf_path):
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "This is a native PDF test. " * 50)
        doc.save(test_pdf_path)
        doc.close()
        print(f"Created dummy native PDF: {test_pdf_path}")

    router = PDFRouter()
    pdf_type = router.identify_type(test_pdf_path)
    print(f"PDF Type for {test_pdf_path}: {pdf_type}")
    
    # Clean up
    if os.path.exists(test_pdf_path):
        os.remove(test_pdf_path)