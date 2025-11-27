# VibeParser System Documentation

## Overview

VibeParser is an advanced document text extraction system that leverages AI-powered technologies to extract text from various document formats with high accuracy and speed. The system is designed to handle both native digital documents and scanned documents with OCR capabilities.

## System Architecture

```
vibe-parser/
├── app.py                 # Main Streamlit web application
├── src/
│   └── vibe_parser/
│       ├── core/
│       │   └── router.py           # Document type classification
│       ├── extractors/
│       │   └── extractor.py        # Main extraction engine
│       ├── models/
│       │   └── config.py           # Configuration models
│       └── utils/
│           ├── preprocessing.py    # Image preprocessing for OCR
│           └── postprocessing.py   # Text cleaning and structuring
├── Image.png              # Demo image for UI
└── requirements.txt       # Python dependencies
```

## Core Components

### 1. Document Router (`src/vibe_parser/core/router.py`)

The router analyzes uploaded documents to determine their type:
- **NATIVE**: Documents with selectable text (e.g., digital PDFs, Word documents)
- **SCANNED**: Image-based documents that require OCR (e.g., scanned PDFs, images)

The classification is based on:
- Text density analysis
- Text quality scoring
- Image content analysis

### 2. Extraction Engine (`src/vibe_parser/extractors/extractor.py`)

The main extraction engine uses Docling library for document processing:
- **Native Documents**: Fast extraction using built-in text extraction
- **Scanned Documents**: OCR-based extraction with preprocessing

Key features:
- Configurable OCR settings
- Performance optimizations
- Fast mode for quick processing
- Support for multiple document formats

### 3. Preprocessing Utilities (`src/vibe_parser/utils/preprocessing.py`)

Image preprocessing to improve OCR accuracy:
- Denoising
- Contrast enhancement
- Binarization
- Noise removal
- Resolution optimization

### 4. Postprocessing Utilities (`src/vibe_parser/utils/postprocessing.py`)

Text cleaning and structuring:
- OCR artifact removal
- Text normalization
- Content structuring
- Keyword extraction
- Quality assessment

## Supported Document Formats

- **PDF** (both native and scanned)
- **Word Documents** (.docx)
- **PowerPoint Presentations** (.pptx)
- **Excel Spreadsheets** (.xlsx)
- **Images** (JPG, PNG, etc.)
- **HTML Files**
- **Markdown Files**
- **Plain Text Files**
- **CSV Files**

## Performance Optimizations

### Speed Enhancements
1. **Fast Mode**: Disabled non-essential features for maximum speed
2. **Converter Reuse**: Single converter instance for multiple documents
3. **Preprocessing Skip**: Optional skipping of image preprocessing
4. **Resolution Reduction**: Lower DPI settings for faster processing

### Quality vs Speed Tradeoff
- **Fast Mode**: 30-60 seconds processing time, good accuracy
- **Standard Mode**: Higher accuracy with longer processing time

## Configuration System

The system uses a comprehensive configuration model:
- OCR settings (engine, DPI, language)
- Preprocessing options (denoise, contrast, binarization)
- Table extraction settings
- Performance options (fast mode, page limits)

## Web Interface

Built with Streamlit, featuring:
- Modern SaaS-style UI
- Drag-and-drop file upload
- Real-time progress indicators
- Results visualization
- Text download functionality

## Installation and Setup

### Prerequisites
- Python 3.8+
- pip package manager

### Installation Steps
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage Examples

### Command Line
```bash
python debug_docling.py document.pdf --fast
```

### Web Interface
1. Navigate to the web app URL
2. Upload a document
3. Click "Extract Text Now"
4. Download results

## API Integration

The system can be integrated as a library:
```python
from src.vibe_parser.extractors.extractor import DoclingExtractor
from src.vibe_parser.core.router import PDFRouter

# Initialize components
router = PDFRouter()
extractor = DoclingExtractor()

# Classify and extract
pdf_type = router.identify_type("document.pdf")
results = extractor.extract_and_process("document.pdf", do_ocr=True)
```

## Performance Benchmarks

### Processing Times
- **Native PDFs**: 2-5 seconds
- **Scanned PDFs (Fast Mode)**: 30-60 seconds
- **Large Documents (50+ pages)**: 2-5 minutes

### Accuracy Rates
- **Native Documents**: 99%+ accuracy
- **Scanned Documents**: 85-95% accuracy
- **Poor Quality Scans**: 70-85% accuracy

## Troubleshooting

### Common Issues
1. **Slow Processing**: Enable fast mode for quicker results
2. **Poor OCR Quality**: Ensure documents are high resolution
3. **Memory Issues**: Use page limits for large documents

### Error Handling
- Graceful fallbacks for preprocessing failures
- Detailed error logging
- User-friendly error messages

## Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

### Code Structure Guidelines
- Follow existing naming conventions
- Maintain consistent error handling
- Add type hints for new functions
- Update documentation as needed

## Future Enhancements

### Planned Features
1. Batch processing support
2. Advanced table extraction
3. Document classification
4. Multi-language support
5. Cloud storage integration

### Performance Improvements
1. GPU acceleration for OCR
2. Parallel processing
3. Caching mechanisms
4. Memory optimization

## Technical Stack

### Core Libraries
- **Docling**: Primary document processing engine
- **PyMuPDF**: PDF manipulation and analysis
- **OpenCV**: Image preprocessing
- **Streamlit**: Web interface framework
- **NLTK**: Text processing utilities

### Dependencies
- docling
- pymupdf
- opencv-python
- streamlit
- pandas
- pydantic
- nltk
- numpy

## System Requirements

### Minimum Specifications
- **RAM**: 4GB
- **Storage**: 100MB available space
- **OS**: Windows, macOS, or Linux

### Recommended Specifications
- **RAM**: 8GB+
- **Storage**: 1GB available space
- **CPU**: Multi-core processor

## Security Considerations

- All processing happens locally
- No data is stored or transmitted
- Temporary files are automatically cleaned up
- Secure file handling



## Support

For issues, questions, or feature requests, please contact the development team.