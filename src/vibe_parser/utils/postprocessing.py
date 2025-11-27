"""
Utilities for post-processing extracted text to improve quality and structure.
"""

import re
from typing import List, Dict, Any
import nltk
from collections import Counter

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class TextPostProcessor:
    """
    Post-process extracted text to improve quality and structure.
    """
    
    def __init__(self):
        pass
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing artifacts and normalizing formatting.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Fix common OCR artifacts
        # Replace common OCR misreads
        replacements = {
            '|': 'I',
            'ﬁ': 'fi',
            'ﬂ': 'fl',
            '\uf0b7': '•',  # Bullet point
            '\u2022': '•',   # Bullet point
            '\u2013': '-',   # En dash
            '\u2014': '--',  # Em dash
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Remove isolated special characters that are likely OCR artifacts
        text = re.sub(r'\s[^\w\s]{1,2}\s', ' ', text)
        
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text
    
    def structure_text(self, text: str) -> Dict[str, Any]:
        """
        Structure text into sections, paragraphs, and sentences.
        
        Args:
            text: Cleaned text
            
        Returns:
            Structured text with metadata
        """
        if not text:
            return {"raw": "", "sections": [], "paragraphs": [], "sentences": []}
        
        # Split into paragraphs (double newlines)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # Further split into sections based on heading-like patterns
        sections = self._identify_sections(paragraphs)
        
        # Extract sentences
        sentences = []
        try:
            from nltk.tokenize import sent_tokenize
            for paragraph in paragraphs:
                sentences.extend(sent_tokenize(paragraph))
        except:
            # Fallback if NLTK is not available
            sentences = self._simple_sentence_splitting(paragraphs)
        
        return {
            "raw": text,
            "sections": sections,
            "paragraphs": paragraphs,
            "sentences": sentences,
            "stats": {
                "char_count": len(text),
                "paragraph_count": len(paragraphs),
                "sentence_count": len(sentences),
                "section_count": len(sections)
            }
        }
    
    def _identify_sections(self, paragraphs: List[str]) -> List[Dict[str, Any]]:
        """
        Identify sections based on heading patterns.
        
        Args:
            paragraphs: List of paragraphs
            
        Returns:
            List of sections with titles and content
        """
        sections = []
        current_section = {"title": "Introduction", "content": []}
        
        heading_patterns = [
            r'^[A-Z][A-Za-z\s]{0,50}[.:]?$',  # All caps or title case short lines
            r'^\d+\.\s+[A-Z].*$',             # Numbered headings
            r'^[A-Z].*\n={3,}$',              # Underlined headings
        ]
        
        for paragraph in paragraphs:
            is_heading = False
            
            # Check if paragraph matches heading patterns
            for pattern in heading_patterns:
                if re.match(pattern, paragraph.strip()):
                    is_heading = True
                    break
            
            if is_heading:
                # Save previous section
                if current_section["content"]:
                    sections.append(current_section)
                
                # Start new section
                current_section = {"title": paragraph.strip(), "content": []}
            else:
                current_section["content"].append(paragraph)
        
        # Add final section
        if current_section["content"]:
            sections.append(current_section)
        
        return sections
    
    def _simple_sentence_splitting(self, paragraphs: List[str]) -> List[str]:
        """
        Simple sentence splitting when NLTK is not available.
        
        Args:
            paragraphs: List of paragraphs
            
        Returns:
            List of sentences
        """
        sentences = []
        for paragraph in paragraphs:
            # Split on periods, exclamation marks, and question marks
            parts = re.split(r'[.!?]+', paragraph)
            for part in parts:
                cleaned = part.strip()
                if len(cleaned) > 10:  # Only consider substantial parts as sentences
                    sentences.append(cleaned + ".")
        return sentences
    
    def extract_keywords(self, text: str, num_keywords: int = 10) -> List[str]:
        """
        Extract important keywords from the text.
        
        Args:
            text: Text to analyze
            num_keywords: Number of keywords to extract
            
        Returns:
            List of keywords
        """
        # Simple keyword extraction based on frequency
        # Remove common stopwords
        try:
            from nltk.corpus import stopwords
            stop_words = set(stopwords.words('english'))
        except:
            # Fallback stopwords list
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can'}
        
        # Tokenize and clean words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        filtered_words = [word for word in words if word not in stop_words]
        
        # Get most common words
        word_freq = Counter(filtered_words)
        keywords = [word for word, freq in word_freq.most_common(num_keywords)]
        
        return keywords
    
    def assess_quality(self, text: str) -> Dict[str, float]:
        """
        Assess the quality of extracted text.
        
        Args:
            text: Text to assess
            
        Returns:
            Quality metrics
        """
        if not text:
            return {"readability": 0.0, "coherence": 0.0, "completeness": 0.0}
        
        # Basic readability metric (character to word ratio)
        words = text.split()
        chars = len(text)
        
        if len(words) == 0:
            readability = 0.0
        else:
            avg_word_length = chars / len(words)
            # Ideal average word length is around 5 characters
            readability = max(0.0, 1.0 - abs(avg_word_length - 5) / 10)
        
        # Coherence metric (based on sentence structure)
        sentences = self._simple_sentence_splitting([text])
        if len(sentences) == 0:
            coherence = 0.0
        else:
            # Average sentence length in words
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            # Ideal average sentence length is around 20 words
            coherence = max(0.0, 1.0 - abs(avg_sentence_length - 20) / 50)
        
        # Completeness metric (based on content density)
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        if len(paragraphs) == 0:
            completeness = 0.0
        else:
            # Average paragraph length
            avg_paragraph_length = sum(len(p) for p in paragraphs) / len(paragraphs)
            # Longer paragraphs suggest more complete content
            completeness = min(1.0, avg_paragraph_length / 200)
        
        return {
            "readability": round(readability, 2),
            "coherence": round(coherence, 2),
            "completeness": round(completeness, 2),
            "overall": round((readability + coherence + completeness) / 3, 2)
        }

def post_process_extraction(markdown_content: str, json_content: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Post-process extraction results to improve quality.
    
    Args:
        markdown_content: Markdown content from extraction
        json_content: JSON content from extraction (optional)
        
    Returns:
        Processed content with quality metrics
    """
    processor = TextPostProcessor()
    
    # Clean the markdown content
    cleaned_text = processor.clean_text(markdown_content)
    
    # Structure the text
    structured_text = processor.structure_text(cleaned_text)
    
    # Extract keywords
    keywords = processor.extract_keywords(cleaned_text)
    
    # Assess quality
    quality_metrics = processor.assess_quality(cleaned_text)
    
    return {
        "cleaned_text": cleaned_text,
        "structured_text": structured_text,
        "keywords": keywords,
        "quality_metrics": quality_metrics,
        "original_markdown": markdown_content,
        "original_json": json_content
    }

if __name__ == "__main__":
    # Example usage
    sample_text = """
    This is a SAMPLE document. It contains some text.
    
    INTRODUCTION
    
    The purpose of this document is to demonstrate text processing.
    We will show how to clean and structure text.
    
    METHODOLOGY
    
    Our approach involves several steps:
    • Preprocessing
    • Analysis  
    • Post-processing
    
    RESULTS
    
    The results show significant improvement in text quality.
    """
    
    processor = TextPostProcessor()
    cleaned = processor.clean_text(sample_text)
    structured = processor.structure_text(cleaned)
    keywords = processor.extract_keywords(cleaned)
    quality = processor.assess_quality(cleaned)
    
    print("Cleaned Text:")
    print(cleaned)
    print("\nKeywords:", keywords)
    print("\nQuality Metrics:", quality)
    print("\nSections:")
    for section in structured["sections"]:
        print(f"  {section['title']}: {len(section['content'])} paragraphs")