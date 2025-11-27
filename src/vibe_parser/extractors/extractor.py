import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Tuple
from docling.document_converter import DocumentConverter
import tempfile
import os

# Import our new preprocessing module
try:
    from src.vibe_parser.utils.preprocessing import OCRPreprocessor
    PREPROCESSING_AVAILABLE = True
except ImportError:
    PREPROCESSING_AVAILABLE = False
    print("Warning: OCR preprocessing not available. Install OpenCV for enhanced OCR.")

# Import our new post-processing module
try:
    from src.vibe_parser.utils.postprocessing import post_process_extraction
    POSTPROCESSING_AVAILABLE = True
except ImportError:
    POSTPROCESSING_AVAILABLE = False
    print("Warning: Post-processing not available.")

# Import configuration
from src.vibe_parser.models.config import ExtractionConfig

class DoclingExtractor:
    """
    Heavy lifter for complex document extraction using Docling.
    Optimized for maximum speed with minimal quality loss.
    Supports multiple document formats: PDF, DOCX, PPTX, Images, etc.
    """
    def __init__(self, config: ExtractionConfig = None):
        self.config = config or ExtractionConfig()
        # Initialize converter once for better performance
        self.converter = None

    def _get_converter(self, do_ocr: bool = True, fast_mode: bool = True):
        """Get or create converter with optimized settings."""
        if self.converter is None:
            from docling.datamodel.pipeline_options import PdfPipelineOptions
            from docling.datamodel.base_models import InputFormat
            from docling.document_converter import PdfFormatOption

            pipeline_options = PdfPipelineOptions()
            pipeline_options.do_ocr = do_ocr and self.config.ocr.enabled
            pipeline_options.do_table_structure = False  # Disable for speed
            
            # Performance optimizations
            if fast_mode:
                pipeline_options.images_scale = 0.5  # Reduce image processing
                pipeline_options.generate_picture_images = False  # Skip picture generation
            
            format_options = {
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
            
            from docling.document_converter import DocumentConverter
            self.converter = DocumentConverter(format_options=format_options)
        
        return self.converter

    def extract_complex_pdf(self, file_path: str, do_ocr: bool = True, fast_mode: bool = True) -> Tuple[str, Dict[str, Any]]:
        """
        Converts any supported document to Markdown and JSON with maximum speed optimizations.
        
        Args:
            file_path: Path to the document file.
            do_ocr: Whether to perform OCR (default: True).
            fast_mode: If True, use maximum speed optimizations.
            
        Returns:
            Tuple containing (markdown_content, json_content)
        """
        # Get optimized converter
        converter = self._get_converter(do_ocr, fast_mode)
        
        # Skip preprocessing entirely for maximum speed
        processed_file_path = file_path
        
        result = converter.convert(processed_file_path)
        
        # Export to Markdown
        markdown_content = result.document.export_to_markdown()
        
        # Export to JSON (structure)
        json_content = result.document.export_to_dict()
        
        return markdown_content, json_content

    def extract_and_process(self, file_path: str, do_ocr: bool = True, fast_mode: bool = True) -> Dict[str, Any]:
        """
        Extract document content and apply minimal post-processing.
        
        Args:
            file_path: Path to the document file.
            do_ocr: Whether to perform OCR.
            fast_mode: If True, use maximum speed optimizations.
            
        Returns:
            Processed extraction results with quality metrics
        """
        # Extract content
        markdown_content, json_content = self.extract_complex_pdf(file_path, do_ocr, fast_mode)
        
        # Apply minimal post-processing if available
        if POSTPROCESSING_AVAILABLE:
            processed_results = post_process_extraction(markdown_content, json_content)
            return processed_results
        else:
            # Fallback to basic results
            return {
                "cleaned_text": markdown_content,
                "original_markdown": markdown_content,
                "original_json": json_content,
                "quality_metrics": {"overall": 0.7}  # Higher default since we're using Docling
            }

    def extract_tables(self, doc_result_dict: Dict[str, Any]) -> List[pd.DataFrame]:
        """
        Helper function to extract tables as Pandas DataFrames.
        """
        pass

def extract_tables_from_result(result) -> List[pd.DataFrame]:
    """
    Extracts tables from a Docling conversion result as Pandas DataFrames.
    
    Args:
        result: The result object returned by DocumentConverter.convert()
        
    Returns:
        List of Pandas DataFrames
    """
    tables = []
    # Iterate through tables in the document
    for table in result.document.tables:
        # Export table to dataframe
        df = table.export_to_dataframe()
        tables.append(df)
    return tables

# Script section for direct execution
if __name__ == "__main__":
    import argparse
    import os
    import sys
    
    parser = argparse.ArgumentParser(description="Extract text from documents using Docling.")
    parser.add_argument("file_path", help="Path to the document file")
    parser.add_argument("--no-ocr", action="store_true", help="Disable OCR for faster extraction")
    parser.add_argument("--fast", action="store_true", help="Use fast mode for quicker extraction")
    
    args = parser.parse_args()
    file_path = args.file_path
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)
        
    extractor = DoclingExtractor()
    print(f"Extracting: {file_path} (OCR: {'Disabled' if args.no_ocr else 'Enabled'}, Fast Mode: {'On' if args.fast else 'Off'})...")
    
    do_ocr = not args.no_ocr
    
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.datamodel.base_models import InputFormat
    from docling.document_converter import PdfFormatOption, DocumentConverter

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = do_ocr
    pipeline_options.do_table_structure = False  # Disable for speed
    
    # Performance optimizations for fast mode
    if args.fast:
        pipeline_options.images_scale = 0.5
        pipeline_options.generate_picture_images = False
    
    format_options = {
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
    
    converter = DocumentConverter(format_options=format_options)
    conv_result = converter.convert(file_path)
    
    md = conv_result.document.export_to_markdown()
    
    print("--- Markdown Preview (first 500 chars) ---")
    print(md[:500])
    
    print("\n--- Tables ---")
    dfs = extract_tables_from_result(conv_result)
    for i, df in enumerate(dfs):
        print(f"Table {i+1}:")
        print(df.head())
        print("-" * 20)