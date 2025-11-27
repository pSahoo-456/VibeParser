"""
Utilities for preprocessing scanned PDFs to improve OCR accuracy.
Optimized for speed with minimal quality loss.
"""

import cv2
import numpy as np
from PIL import Image
import io
import fitz  # PyMuPDF

class OCRPreprocessor:
    """
    Preprocess images from scanned PDFs to optimize OCR accuracy.
    Ultra-fast mode prioritizes speed over maximum quality.
    """
    
    def preprocess_image(self, image_bytes: bytes, dpi: int = 150, ultra_fast: bool = True) -> bytes:
        """
        Apply minimal preprocessing for maximum speed.
        
        Args:
            image_bytes: Raw image bytes
            dpi: Target DPI for resizing (lower = faster)
            ultra_fast: If True, use ultra-fast preprocessing
            
        Returns:
            Preprocessed image bytes
        """
        # Convert bytes to OpenCV image
        image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_GRAYSCALE)
        
        if ultra_fast:
            # Ultra-fast preprocessing - minimal operations
            # Just resize to reasonable DPI and apply simple thresholding
            processed = self._ultra_fast_resize(image, min(dpi, 150))
            processed = self._ultra_fast_binarize(processed)
        else:
            # Fast preprocessing - essential steps only
            processed = self._fast_enhance_contrast(image)
            processed = self._fast_binarize_image(processed)
            processed = self._fast_resize_for_ocr(processed, min(dpi, 150))
        
        # Convert back to bytes
        is_success, buffer = cv2.imencode(".png", processed)
        if not is_success:
            raise RuntimeError("Failed to encode processed image")
            
        return buffer.tobytes()
    
    def _ultra_fast_resize(self, image, target_dpi=150):
        """Ultra-fast resizing using nearest neighbor."""
        # Assuming standard DPI is 72
        current_dpi = 72
        scale_factor = target_dpi / current_dpi
        
        if scale_factor >= 1.0:
            return image  # No upsizing needed
            
        height, width = image.shape[:2]
        new_dimensions = (int(width * scale_factor), int(height * scale_factor))
        
        # Use INTER_NEAREST for maximum speed
        resized = cv2.resize(image, new_dimensions, interpolation=cv2.INTER_NEAREST)
        
        return resized
    
    def _ultra_fast_binarize(self, image):
        """Ultra-fast binarization using simple global thresholding."""
        # Apply simple thresholding
        _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary
    
    def _fast_enhance_contrast(self, image):
        """Fast contrast enhancement using simple histogram equalization."""
        # Apply histogram equalization
        enhanced = cv2.equalizeHist(image)
        return enhanced
    
    def _fast_binarize_image(self, image):
        """Fast binarization using adaptive thresholding."""
        # Apply adaptive thresholding with larger block size for speed
        binary = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 2
        )
        return binary
    
    def _fast_resize_for_ocr(self, image, target_dpi=150):
        """Fast resizing for OCR."""
        # Assuming standard DPI is 72
        current_dpi = 72
        scale_factor = target_dpi / current_dpi
        
        if scale_factor >= 1.0:
            return image  # No upsizing needed
            
        height, width = image.shape[:2]
        new_dimensions = (int(width * scale_factor), int(height * scale_factor))
        
        # Resize image with linear interpolation (faster than cubic)
        resized = cv2.resize(image, new_dimensions, interpolation=cv2.INTER_LINEAR)
        
        return resized

def preprocess_scanned_pdf(pdf_path: str, output_path: str, ultra_fast: bool = True) -> str:
    """
    Preprocess scanned PDF with minimal operations for maximum speed.
    
    Args:
        pdf_path: Path to input PDF
        output_path: Path for output PDF
        ultra_fast: If True, use ultra-fast preprocessing
        
    Returns:
        Path to the preprocessed PDF
    """
    doc = fitz.open(pdf_path)
    preprocessor = OCRPreprocessor()
    
    # For performance, only process first few pages in ultra-fast mode
    pages_to_process = range(min(5, len(doc))) if ultra_fast else range(len(doc))
    
    for page_num in pages_to_process:
        page = doc[page_num]
        
        # Get all images on the page
        image_list = page.get_images()
        
        # Limit number of images processed in ultra-fast mode
        images_to_process = image_list[:1] if ultra_fast else image_list[:3]
        
        # Process each image
        for img_index, img in enumerate(images_to_process):
            # Get the image XREF
            xref = img[0]
            
            # Extract the image bytes
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            
            # Preprocess the image
            processed_bytes = preprocessor.preprocess_image(image_bytes, ultra_fast=ultra_fast)
            
            # TODO: Replace the image in the PDF with the processed one
            # This would require more complex PDF manipulation
    
    # Save the (potentially) modified document
    doc.save(output_path)
    doc.close()
    
    return output_path

if __name__ == "__main__":
    # Example usage
    pass