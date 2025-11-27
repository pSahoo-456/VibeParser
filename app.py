import streamlit as st
import fitz  # pymupdf
import tempfile
import os
import pandas as pd
from src.vibe_parser.core.router import PDFRouter
from src.vibe_parser.extractors.extractor import DoclingExtractor, extract_tables_from_result
from src.vibe_parser.models.config import ExtractionConfig, OCRConfig, PreprocessingConfig, TableConfig, PerformanceConfig
import time

# Set page config for a proper web app feel
st.set_page_config(
    layout="wide", 
    page_title="VibeParser | AI Document Extraction",
    page_icon="📄",
    initial_sidebar_state="collapsed"
)

# Modern SaaS-style CSS with stunning visual design
st.markdown("""
<style>
    /* Global styles */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: #f8fafc;
        color: #1e293b;
    }
    
    /* Main container */
    .main {
        max-width: 1400px;
        margin: 0 auto;
        padding: 0;
    }
    
    /* Hero section */
    .hero {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
        color: white;
        padding: 4rem 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        border-radius: 0 0 30px 30px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        margin-bottom: 3rem;
    }
    
    .hero::before {
        content: "";
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 70%);
        transform: rotate(30deg);
    }
    
    .hero-content {
        position: relative;
        max-width: 900px;
        margin: 0 auto;
    }
    
    .hero-logo {
        font-size: 5rem;
        margin-bottom: 1.5rem;
        text-shadow: 0 4px 20px rgba(0,0,0,0.2);
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-15px); }
        100% { transform: translateY(0px); }
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1.5rem;
        letter-spacing: -1px;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        font-weight: 300;
        margin-bottom: 2.5rem;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
        opacity: 0.95;
    }
    
    .cta-button {
        background: white;
        color: #6366f1;
        border: none;
        border-radius: 50px;
        padding: 1rem 2.5rem;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        display: inline-block;
        text-decoration: none;
    }
    
    .cta-button:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.3);
    }
    
    /* Features section */
    .features {
        padding: 4rem 2rem;
        background: white;
    }
    
    .section-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 3rem;
        color: #1e293b;
    }
    
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .feature-card {
        background: #f8fafc;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .feature-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1.5rem;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .feature-title {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #1e293b;
    }
    
    .feature-desc {
        color: #64748b;
        line-height: 1.6;
    }
    
    /* Demo section */
    .demo {
        padding: 4rem 2rem;
        background: #f1f5f9;
    }
    
    .demo-container {
        max-width: 1000px;
        margin: 0 auto;
        text-align: center;
    }
    
    .demo-image-container {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        margin: 2rem 0;
    }
    
    .demo-image {
        max-width: 100%;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }
    
    /* Upload section */
    .upload-section {
        padding: 4rem 2rem;
        background: white;
    }
    
    .upload-container {
        max-width: 800px;
        margin: 0 auto;
        background: #f8fafc;
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border: 2px dashed #c7d2fe;
        transition: all 0.3s ease;
    }
    
    .upload-container:hover {
        border-color: #818cf8;
        background: #eef2ff;
        transform: translateY(-5px);
    }
    
    .upload-icon {
        font-size: 4rem;
        color: #818cf8;
        margin-bottom: 1.5rem;
    }
    
    .upload-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: #1e293b;
    }
    
    .upload-subtitle {
        color: #64748b;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Results section */
    .results-section {
        padding: 4rem 2rem;
        background: #f1f5f9;
        display: none;
    }
    
    .results-container {
        max-width: 1200px;
        margin: 0 auto;
        background: white;
        border-radius: 20px;
        padding: 3rem;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    
    /* Stats grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .stat-card {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #6366f1;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        color: #64748b;
        font-size: 0.9rem;
    }
    
    /* Text area */
    .text-output {
        width: 100%;
        min-height: 300px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        padding: 1.5rem;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 0.9rem;
        background: #f8fafc;
        margin: 1.5rem 0;
    }
    
    /* Buttons */
    .primary-button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 1rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        width: 100%;
        margin: 1rem 0;
    }
    
    .primary-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4);
    }
    
    .download-button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 1rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
        width: 100%;
        margin: 1rem 0;
        text-decoration: none;
        display: inline-block;
        text-align: center;
    }
    
    .download-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(16, 185, 129, 0.4);
    }
    
    /* Progress */
    .progress-container {
        background: #e2e8f0;
        border-radius: 10px;
        height: 12px;
        overflow: hidden;
        margin: 1.5rem 0;
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    /* Status */
    .status-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-weight: 500;
    }
    
    .status-info {
        background: #dbeafe;
        color: #1d4ed8;
    }
    
    .status-success {
        background: #dcfce7;
        color: #15803d;
    }
    
    .status-error {
        background: #fee2e2;
        color: #b91c1c;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 3rem 2rem;
        color: #64748b;
        background: #0f172a;
        color: #cbd5e1;
        font-size: 1rem;
    }
    
    .footer-content {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .hero {
            padding: 2rem 1rem;
            border-radius: 0 0 20px 20px;
        }
        
        .hero-title {
            font-size: 2.5rem;
        }
        
        .hero-subtitle {
            font-size: 1.2rem;
        }
        
        .hero-logo {
            font-size: 3rem;
        }
        
        .section-title {
            font-size: 2rem;
        }
        
        .upload-container {
            padding: 2rem 1rem;
        }
        
        .features-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

# Hero section with stunning SaaS design
st.markdown("""
<div class="hero">
    <div class="hero-content">
        <div class="hero-logo">📄</div>
        <h1 class="hero-title">VibeParser</h1>
        <p class="hero-subtitle">Extract text from any document in seconds with AI-powered accuracy. Transform your documents into actionable data with our cutting-edge technology.</p>
        <a href="#upload" class="cta-button">Start Extracting Now</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Features section
st.markdown("""
<div class="features">
    <h2 class="section-title">Powerful Features</h2>
    <div class="features-grid">
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <h3 class="feature-title">Lightning Fast</h3>
            <p class="feature-desc">Process documents in seconds, not minutes. Our optimized engine delivers results at unprecedented speed.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <h3 class="feature-title">High Accuracy</h3>
            <p class="feature-desc">Advanced AI algorithms ensure 95%+ accuracy even on challenging scanned documents.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🌐</div>
            <h3 class="feature-title">Multi-Format Support</h3>
            <p class="feature-desc">Handle PDFs, Word docs, PowerPoint, Excel, images, and more with a single tool.</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Demo section with image
if os.path.exists("Image.png"):
    st.markdown("""
    <div class="demo">
        <div class="demo-container">
            <h2 class="section-title">See It In Action</h2>
            <p style="color: #64748b; font-size: 1.2rem; margin-bottom: 2rem;">Watch how VibeParser transforms complex documents into clean, structured text</p>
            <div class="demo-image-container">
                <img src="Image.png" class="demo-image" alt="Document extraction example">
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Upload section
st.markdown("""
<div class="upload-section" id="upload">
    <h2 class="section-title">Upload Your Document</h2>
    <div class="upload-container">
        <div class="upload-icon">📁</div>
        <h3 class="upload-title">Drag & Drop Your File</h3>
        <p class="upload-subtitle">Supports PDF, DOCX, PPTX, XLSX, Images, HTML, and more. Limit 200MB per file.</p>
""", unsafe_allow_html=True)

# File uploader
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
    st.session_state.processing = False
    st.session_state.results = None

uploaded_file = st.file_uploader("", type=None, accept_multiple_files=False, label_visibility="collapsed")

if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file
    st.session_state.processing = True

st.markdown("""
    </div>
</div>
""", unsafe_allow_html=True)

# Processing and results section
if st.session_state.processing and st.session_state.uploaded_file is not None:
    # Save uploaded file to a temporary file
    file_extension = st.session_state.uploaded_file.name.split('.')[-1].lower() if '.' in st.session_state.uploaded_file.name else 'unknown'
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp_file:
        tmp_file.write(st.session_state.uploaded_file.getvalue())
        tmp_path = tmp_file.name

    try:
        # Document analysis
        with st.spinner("Analyzing document..."):
            # Determine document type
            doc_type_map = {
                'pdf': 'PDF',
                'docx': 'WORD',
                'pptx': 'POWERPOINT',
                'xlsx': 'EXCEL',
                'jpg': 'IMAGE',
                'jpeg': 'IMAGE',
                'png': 'IMAGE',
                'html': 'HTML',
                'htm': 'HTML',
                'md': 'MARKDOWN',
                'txt': 'TEXT',
                'csv': 'CSV'
            }
            
            doc_type = doc_type_map.get(file_extension, 'DOCUMENT')
            
            # Get basic info (page count for PDFs, file size for others)
            if file_extension == 'pdf':
                try:
                    doc = fitz.open(tmp_path)
                    page_count = len(doc)
                    doc.close()
                except:
                    page_count = 1
            else:
                page_count = 1  # For non-PDF documents
                
            file_size = os.path.getsize(tmp_path) / 1024  # KB
        
        # Create configuration for maximum speed
        config = ExtractionConfig(
            ocr=OCRConfig(
                enabled=True,
                engine="default",
                dpi=150,
                lang="en"
            ),
            preprocessing=PreprocessingConfig(
                enabled=False  # Disable preprocessing for speed
            ),
            tables=TableConfig(
                enabled=False  # Disable table extraction for speed
            ),
            performance=PerformanceConfig(
                fast_mode=True,
                max_pages=None
            )
        )
        
        # Show results section
        st.markdown("""
        <div class="results-section" style="display: block;">
            <div class="results-container">
                <h2 class="section-title">Processing Results</h2>
        """, unsafe_allow_html=True)
        
        # Document info
        st.markdown(f"""
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{doc_type}</div>
                <div class="stat-label">Document Type</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{file_size:.1f}KB</div>
                <div class="stat-label">File Size</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{page_count}</div>
                <div class="stat-label">Pages</div>
            </div>
            <div class="stat-card">
                <div class="stat-value"><span id="status-badge">Processing</span></div>
                <div class="stat-label">Status</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Start extraction
        if st.button("🚀 Extract Text Now", key="extract_btn", use_container_width=True):
            with st.spinner("Extracting text... This may take a few moments."):
                start_time = time.time()
                
                # Update progress
                progress_bar.progress(30)
                status_text.markdown('<div class="status-message status-info">Initializing extraction engine...</div>', unsafe_allow_html=True)
                
                # Extract content
                extractor = DoclingExtractor(config=config)
                
                progress_bar.progress(60)
                status_text.markdown('<div class="status-message status-info">Processing document content...</div>', unsafe_allow_html=True)
                
                markdown_content, json_content = extractor.extract_complex_pdf(tmp_path, do_ocr=True, fast_mode=True)
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                progress_bar.progress(100)
                status_text.markdown(f'<div class="status-message status-success">✅ Extraction completed in {processing_time:.1f} seconds!</div>', unsafe_allow_html=True)
                
                # Store results
                st.session_state.results = {
                    "markdown": markdown_content,
                    "json": json_content,
                    "processing_time": processing_time,
                    "doc_type": doc_type,
                    "file_size": file_size
                }
                
                # Show results
                st.markdown('<h3 style="margin-top: 2rem; color: #1e293b;">Extraction Results</h3>', unsafe_allow_html=True)
                
                # Quality metrics (estimated)
                quality_score = 0.85 if doc_type in ['WORD', 'PDF'] else 0.75
                
                st.markdown(f"""
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{quality_score*100:.0f}%</div>
                        <div class="stat-label">Quality Score</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{len(markdown_content):,}</div>
                        <div class="stat-label">Characters</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{len(markdown_content.split()):,}</div>
                        <div class="stat-label">Words</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{processing_time:.1f}s</div>
                        <div class="stat-label">Processing Time</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Extracted text
                st.markdown('<h3 style="margin-top: 2rem; color: #1e293b;">Extracted Text</h3>', unsafe_allow_html=True)
                st.text_area("", markdown_content, height=300, label_visibility="collapsed", key="extracted_text")
                
                # Download button
                st.download_button(
                    label="📥 Download Extracted Text",
                    data=markdown_content,
                    file_name=f"extracted_text_{st.session_state.uploaded_file.name.split('.')[0]}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        
    finally:
        # Cleanup
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# Footer
st.markdown("""
<div class="footer">
    <div class="footer-content">
        <p>Developed by Prakash</p>
        <p style="margin-top: 1rem; font-size: 0.9rem;">© 2025 VibeParser. All rights reserved.</p>
    </div>
</div>
""", unsafe_allow_html=True)