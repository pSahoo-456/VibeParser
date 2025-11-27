"""
Configuration models for the VibeParser system.
"""

import os
import json
from pydantic import BaseModel
from typing import Optional, Dict, Any

class OCRConfig(BaseModel):
    """Configuration for OCR processing."""
    enabled: bool = True
    engine: str = "default"  # Options: "default", "tesseract", "easyocr"
    dpi: int = 200
    lang: str = "en"
    tess_cmd: Optional[str] = None  # Custom tesseract command
    
class TableConfig(BaseModel):
    """Configuration for table extraction."""
    enabled: bool = True
    structure_only: bool = False
    html_output: bool = False
    
class PreprocessingConfig(BaseModel):
    """Configuration for image preprocessing."""
    enabled: bool = True
    denoise: bool = True
    contrast_enhancement: bool = True
    binarization: bool = True
    noise_removal: bool = True
    
class PerformanceConfig(BaseModel):
    """Configuration for performance optimization."""
    fast_mode: bool = False
    max_pages: Optional[int] = None
    timeout_seconds: int = 300  # 5 minutes default timeout
    
class ExtractionConfig(BaseModel):
    """Main configuration for PDF extraction."""
    ocr: OCRConfig = OCRConfig()
    tables: TableConfig = TableConfig()
    preprocessing: PreprocessingConfig = PreprocessingConfig()
    performance: PerformanceConfig = PerformanceConfig()
    # Add more configuration options as needed
    
    class Config:
        # Allow arbitrary types for flexibility
        arbitrary_types_allowed = True

# Default configuration
DEFAULT_CONFIG = ExtractionConfig()

def load_config(config_path: Optional[str] = None) -> ExtractionConfig:
    """
    Load configuration from a file or return default configuration.
    
    Args:
        config_path: Path to configuration file (JSON/YAML)
        
    Returns:
        ExtractionConfig instance
    """
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            return ExtractionConfig(**config_data)
        except Exception as e:
            print(f"Warning: Failed to load config from {config_path}: {e}")
            print("Using default configuration.")
    
    return DEFAULT_CONFIG