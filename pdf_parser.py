"""
PDF Parser using PyMuPDF for extracting text with formatting information
"""

import fitz  # PyMuPDF
import re
from typing import List, Dict, Any

class PDFParser:
    """
    PDF parser that extracts text with formatting information
    needed for heading detection
    """
    
    def __init__(self):
        self.supported_formats = ['pdf']
    
    def parse_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Parse PDF and extract text with formatting information
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            List[Dict]: List of pages with text blocks and formatting info
        """
        try:
            # Open PDF document
            doc = fitz.open(pdf_path)
            pages_data = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_data = self._extract_page_data(page, page_num + 1)
                pages_data.append(page_data)
            
            doc.close()
            return pages_data
            
        except Exception as e:
            print(f"Error parsing PDF {pdf_path}: {str(e)}")
            return []
    
    def _extract_page_data(self, page, page_num: int) -> Dict[str, Any]:
        """
        Extract text blocks with formatting from a single page
        
        Args:
            page: PyMuPDF page object
            page_num (int): Page number (1-indexed)
            
        Returns:
            Dict: Page data with text blocks and formatting
        """
        
        page_data = {
            'page_number': page_num,
            'text_blocks': [],
            'page_text': '',
            'page_bbox': page.rect
        }
        
        try:
            # Get text blocks with formatting (dictionary format)
            blocks = page.get_text("dict")
            
            # Process each block
            for block in blocks.get("blocks", []):
                if "lines" in block:  # Text block
                    self._process_text_block(block, page_data)
            
            # Also get plain text for fallback
            page_data['page_text'] = page.get_text()
            
        except Exception as e:
            print(f"Error extracting page {page_num} data: {str(e)}")
            # Fallback to plain text
            page_data['page_text'] = page.get_text()
        
        return page_data
    
    def _process_text_block(self, block: Dict, page_data: Dict):
        """
        Process a text block and extract formatting information
        
        Args:
            block (Dict): Text block from PyMuPDF
            page_data (Dict): Page data to append to
        """
        
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span.get("text", "").strip()
                
                if not text:  # Skip empty text
                    continue
                
                # Extract formatting information
                text_info = {
                    'text': text,
                    'font_size': span.get("size", 12),
                    'font_name': span.get("font", ""),
                    'font_flags': span.get("flags", 0),  # Bold, italic flags
                    'bbox': span.get("bbox", [0, 0, 0, 0]),  # [x0, y0, x1, y1]
                    'color': span.get("color", 0),
                    'line_bbox': line.get("bbox", [0, 0, 0, 0]),
                    'block_bbox': block.get("bbox", [0, 0, 0, 0])
                }
                
                # Add computed properties
                text_info['is_bold'] = self._is_bold(text_info['font_flags'])
                text_info['is_italic'] = self._is_italic(text_info['font_flags'])
                text_info['x_position'] = text_info['bbox'][0]
                text_info['y_position'] = text_info['bbox'][1]
                text_info['text_width'] = text_info['bbox'][2] - text_info['bbox'][0]
                text_info['text_height'] = text_info['bbox'][3] - text_info['bbox'][1]
                
                page_data['text_blocks'].append(text_info)
    
    def _is_bold(self, flags: int) -> bool:
        """Check if text is bold based on font flags"""
        return bool(flags & 2**4)  # Bold flag
    
    def _is_italic(self, flags: int) -> bool:
        """Check if text is italic based on font flags"""
        return bool(flags & 2**1)  # Italic flag
    
    def get_document_stats(self, pages_data: List[Dict]) -> Dict[str, Any]:
        """
        Get statistics about the document for better heading detection
        
        Args:
            pages_data (List[Dict]): Parsed pages data
            
        Returns:
            Dict: Document statistics
        """
        
        all_font_sizes = []
        all_texts = []
        
        for page in pages_data:
            for block in page['text_blocks']:
                all_font_sizes.append(block['font_size'])
                all_texts.append(block['text'])
        
        if not all_font_sizes:
            return {}
        
        # Calculate statistics
        stats = {
            'total_text_blocks': len(all_texts),
            'unique_font_sizes': list(set(all_font_sizes)),
            'min_font_size': min(all_font_sizes),
            'max_font_size': max(all_font_sizes),
            'avg_font_size': sum(all_font_sizes) / len(all_font_sizes),
            'most_common_font_size': max(set(all_font_sizes), key=all_font_sizes.count)
        }
        
        # Sort font sizes for hierarchy detection
        stats['sorted_font_sizes'] = sorted(stats['unique_font_sizes'], reverse=True)
        
        return stats