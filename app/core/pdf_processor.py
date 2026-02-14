"""PDF text extraction with better encoding handling."""

from typing import Dict, List
import pypdf
import pdfplumber
from pathlib import Path
from app.utils.logger import logger

class PDFProcessor:
    """Extract text and metadata from PDF files."""
    
    def __init__(self):
        self.supported_methods = ["pypdf", "pdfplumber"]
    
    def clean_text(self, text: str) -> str:
        """Clean text of problematic characters."""
        # Replace problematic Unicode characters
        text = text.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        # Remove null bytes
        text = text.replace('\x00', '')
        # Remove replacement character
        text = text.replace('\ufffd', '')
        # Normalize whitespace
        text = ' '.join(text.split())
        return text
    
    def extract_text_pypdf(self, file_path: str) -> Dict[str, any]:
        """Extract text using pypdf (faster, basic)."""
        try:
            reader = pypdf.PdfReader(file_path)
            
            text_by_page = []
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if text and text.strip():
                    # Clean the text
                    cleaned_text = self.clean_text(text)
                    if cleaned_text:
                        text_by_page.append({
                            "page_number": page_num,
                            "text": cleaned_text
                        })
            
            # Extract metadata safely
            metadata = {
                "title": self.clean_text(str(reader.metadata.title)) if reader.metadata and reader.metadata.title else "Unknown",
                "author": self.clean_text(str(reader.metadata.author)) if reader.metadata and reader.metadata.author else "Unknown",
                "num_pages": len(reader.pages),
                "extraction_method": "pypdf"
            }
            
            logger.info(f"Extracted {len(text_by_page)} pages using pypdf")
            return {
                "pages": text_by_page,
                "metadata": metadata
            }
        
        except Exception as e:
            logger.error(f"pypdf extraction failed: {str(e)}")
            raise
    
    def extract_text_pdfplumber(self, file_path: str) -> Dict[str, any]:
        """Extract text using pdfplumber (better for tables/complex layouts)."""
        try:
            text_by_page = []
            
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    if text and text.strip():
                        # Clean the text
                        cleaned_text = self.clean_text(text)
                        if cleaned_text:
                            text_by_page.append({
                                "page_number": page_num,
                                "text": cleaned_text
                            })
                
                # Extract metadata safely
                metadata = {
                    "title": self.clean_text(str(pdf.metadata.get("Title", "Unknown"))),
                    "author": self.clean_text(str(pdf.metadata.get("Author", "Unknown"))),
                    "num_pages": len(pdf.pages),
                    "extraction_method": "pdfplumber"
                }
            
            logger.info(f"Extracted {len(text_by_page)} pages using pdfplumber")
            return {
                "pages": text_by_page,
                "metadata": metadata
            }
        
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {str(e)}")
            raise
    
    def process_pdf(self, file_path: str, method: str = "pypdf") -> Dict[str, any]:
        """
        Process a PDF file and extract text.
        
        Args:
            file_path: Path to PDF file
            method: Extraction method ("pypdf" or "pdfplumber")
        
        Returns:
            Dict with 'pages' (list of page dicts) and 'metadata'
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        if method == "pypdf":
            return self.extract_text_pypdf(file_path)
        elif method == "pdfplumber":
            return self.extract_text_pdfplumber(file_path)
        else:
            raise ValueError(f"Unsupported extraction method: {method}")
    
    def get_file_info(self, file_path: str) -> Dict[str, any]:
        """Get basic file information without full extraction."""
        file_path = Path(file_path)
        return {
            "filename": file_path.name,
            "size_bytes": file_path.stat().st_size,
            "size_mb": round(file_path.stat().st_size / (1024 * 1024), 2)
        }
