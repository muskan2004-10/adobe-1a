"""
Heading Extractor using font-based analysis for detecting H1, H2, H3 headings
"""

import re
from typing import List, Dict, Any, Optional
from collections import Counter

class HeadingExtractor:
    """
    Extract headings from PDF text blocks using font-based analysis
    """
    
    def __init__(self):
        # Heading patterns (common patterns for headings)
        self.heading_patterns = [
            r'^\d+\.?\s+',                    # "1. " or "1 "
            r'^\d+\.\d+\.?\s+',              # "1.1. " or "1.1 "
            r'^\d+\.\d+\.\d+\.?\s+',         # "1.1.1. " or "1.1.1 "
            r'^[A-Z][A-Z\s]{2,}$',           # ALL CAPS headings
            r'^[IVX]+\.?\s+',                # Roman numerals "I. ", "II. "
            r'^[A-Z]\.?\s+',                 # Single capital letter "A. "
            r'^\([a-z]\)\s+',                # "(a) ", "(b) "
            r'^Chapter\s+\d+',               # "Chapter 1"
            r'^Section\s+\d+',               # "Section 1"
            r'^Part\s+[IVX]+',               # "Part I"
        ]
        
        # Common heading keywords
        self.heading_keywords = [
            'introduction', 'conclusion', 'abstract', 'summary', 'overview',
            'background', 'methodology', 'results', 'discussion', 'references',
            'acknowledgments', 'appendix', 'chapter', 'section', 'part',
            'table of contents', 'executive summary', 'literature review'
        ]
    
    def extract_title(self, pages_data: List[Dict]) -> str:
        """
        Extract document title from the first page
        
        Args:
            pages_data (List[Dict]): Parsed pages data
            
        Returns:
            str: Document title
        """
        
        if not pages_data or not pages_data[0]['text_blocks']:
            return "Untitled Document"
        
        first_page = pages_data[0]
        
        # Get document statistics for font analysis
        doc_stats = self._get_doc_stats(pages_data)
        
        # Find the largest font text in the first page (likely title)
        title_candidates = []
        
        for block in first_page['text_blocks']:
            # Skip very small text
            if block['font_size'] < doc_stats.get('avg_font_size', 12):
                continue
            
            # Skip single characters or very long text
            text = block['text'].strip()
            if len(text) < 3 or len(text) > 200:
                continue
            
            # Skip obvious non-titles
            if self._is_likely_header_footer(text):
                continue
            
            title_candidates.append({
                'text': text,
                'font_size': block['font_size'],
                'is_bold': block['is_bold'],
                'y_position': block['y_position'],
                'page_number': block.get('page_number', 1)
            })
        
        if not title_candidates:
            return "Untitled Document"
        
        # Sort by font size (desc) and position (asc - higher on page)
        title_candidates.sort(key=lambda x: (-x['font_size'], x['y_position']))
        
        # Take the first candidate as title
        title = title_candidates[0]['text']
        
        # Clean up title
        title = self._clean_title_text(title)
        
        return title if title else "Untitled Document"
    
    def extract_headings(self, pages_data: List[Dict]) -> List[Dict[str, Any]]:
        """
        Extract headings (H1, H2, H3) from all pages
        
        Args:
            pages_data (List[Dict]): Parsed pages data
            
        Returns:
            List[Dict]: List of headings with level, text, and page
        """
        
        if not pages_data:
            return []
        
        # Get document statistics
        doc_stats = self._get_doc_stats(pages_data)
        
        # Extract all potential headings
        potential_headings = []
        
        for page in pages_data:
            page_headings = self._extract_page_headings(page, doc_stats)
            potential_headings.extend(page_headings)
        
        # Classify headings into H1, H2, H3
        classified_headings = self._classify_headings(potential_headings, doc_stats)
        
        # Sort by page and position
        classified_headings.sort(key=lambda x: (x['page'], x.get('y_position', 0)))
        
        # Format for output
        final_headings = []
        for heading in classified_headings:
            final_headings.append({
                'level': heading['level'],
                'text': heading['text'],
                'page': heading['page']
            })
        
        return final_headings
    
    def _extract_page_headings(self, page: Dict, doc_stats: Dict) -> List[Dict]:
        """Extract potential headings from a single page"""
        
        headings = []
        page_num = page['page_number']
        
        for block in page['text_blocks']:
            text = block['text'].strip()
            
            # Skip empty or very short text
            if len(text) < 2:
                continue
            
            # Skip obvious non-headings
            if self._is_likely_header_footer(text):
                continue
            
            # Skip very long text (likely paragraphs)
            if len(text) > 300:
                continue
            
            # Check if this could be a heading
            heading_score = self._calculate_heading_score(block, doc_stats)
            
            if heading_score > 0.3:  # Threshold for potential heading
                headings.append({
                    'text': text,
                    'page': page_num,
                    'font_size': block['font_size'],
                    'is_bold': block['is_bold'],
                    'y_position': block['y_position'],
                    'x_position': block['x_position'],
                    'heading_score': heading_score,
                    'has_numbering': self._has_numbering(text),
                    'matches_pattern': self._matches_heading_pattern(text),
                    'contains_keywords': self._contains_heading_keywords(text)
                })
        
        return headings
    
    def _calculate_heading_score(self, block: Dict, doc_stats: Dict) -> float:
        """
        Calculate likelihood that a text block is a heading
        
        Returns:
            float: Score between 0 and 1 (higher = more likely heading)
        """
        
        text = block['text'].strip()
        score = 0.0
        
        # Font size factor (larger = higher score)
        avg_font_size = doc_stats.get('avg_font_size', 12)
        if block['font_size'] > avg_font_size * 1.2:
            score += 0.3
        elif block['font_size'] > avg_font_size:
            score += 0.15
        
        # Bold text factor
        if block['is_bold']:
            score += 0.2
        
        # Position factor (headings often left-aligned)
        if block['x_position'] < 100:  # Assume left margin
            score += 0.1
        
        # Pattern matching factor
        if self._matches_heading_pattern(text):
            score += 0.25
        
        # Keyword factor
        if self._contains_heading_keywords(text):
            score += 0.15
        
        # Length factor (headings are usually not too long)
        if 5 <= len(text) <= 100:
            score += 0.1
        elif len(text) > 200:
            score -= 0.2
        
        # Case factor (titles often have title case)
        if self._is_title_case(text):
            score += 0.1
        elif text.isupper() and len(text) > 3:
            score += 0.15
        
        # Line ending factor (headings usually don't end with periods)
        if not text.endswith('.') and not text.endswith(','):
            score += 0.05
        
        return min(score, 1.0)
    
    def _classify_headings(self, headings: List[Dict], doc_stats: Dict) -> List[Dict]:
        """
        Classify headings into H1, H2, H3 based on font sizes and patterns
        """
        
        if not headings:
            return []
        
        # Sort headings by font size (descending)
        headings.sort(key=lambda x: x['font_size'], reverse=True)
        
        # Get unique font sizes
        font_sizes = list(set([h['font_size'] for h in headings]))
        font_sizes.sort(reverse=True)
        
        # Assign levels based on font size hierarchy
        size_to_level = {}
        
        if len(font_sizes) >= 3:
            size_to_level[font_sizes[0]] = 'H1'
            size_to_level[font_sizes[1]] = 'H2'
            size_to_level[font_sizes[2]] = 'H3'
            # Map remaining sizes to H3
            for size in font_sizes[3:]:
                size_to_level[size] = 'H3'
        elif len(font_sizes) == 2:
            size_to_level[font_sizes[0]] = 'H1'
            size_to_level[font_sizes[1]] = 'H2'
        elif len(font_sizes) == 1:
            size_to_level[font_sizes[0]] = 'H1'
        
        # Apply classification with pattern-based refinement
        classified = []
        
        for heading in headings:
            base_level = size_to_level.get(heading['font_size'], 'H3')
            
            # Refine level based on numbering patterns
            text = heading['text'].strip()
            
            # Check for hierarchical numbering
            if re.match(r'^\d+\.?\s+', text):  # "1. " pattern
                refined_level = 'H1'
            elif re.match(r'^\d+\.\d+\.?\s+', text):  # "1.1. " pattern
                refined_level = 'H2'
            elif re.match(r'^\d+\.\d+\.\d+\.?\s+', text):  # "1.1.1. " pattern
                refined_level = 'H3'
            else:
                refined_level = base_level
            
            heading['level'] = refined_level
            classified.append(heading)
        
        return classified
    
    def _get_doc_stats(self, pages_data: List[Dict]) -> Dict:
        """Get document statistics for analysis"""
        
        all_font_sizes = []
        all_blocks = []
        
        for page in pages_data:
            for block in page['text_blocks']:
                all_font_sizes.append(block['font_size'])
                all_blocks.append(block)
        
        if not all_font_sizes:
            return {'avg_font_size': 12}
        
        return {
            'avg_font_size': sum(all_font_sizes) / len(all_font_sizes),
            'max_font_size': max(all_font_sizes),
            'min_font_size': min(all_font_sizes),
            'total_blocks': len(all_blocks)
        }
    
    def _matches_heading_pattern(self, text: str) -> bool:
        """Check if text matches common heading patterns"""
        for pattern in self.heading_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _has_numbering(self, text: str) -> bool:
        """Check if text starts with numbering"""
        return bool(re.match(r'^\d+\.?\s+', text))
    
    def _contains_heading_keywords(self, text: str) -> bool:
        """Check if text contains common heading keywords"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.heading_keywords)
    
    def _is_title_case(self, text: str) -> bool:
        """Check if text is in title case"""
        words = text.split()
        if len(words) < 2:
            return False
        
        title_words = 0
        for word in words:
            if word and word[0].isupper() and len(word) > 1:
                title_words += 1
        
        return title_words / len(words) >= 0.6
    
    def _is_likely_header_footer(self, text: str) -> bool:
        """Check if text is likely a header or footer"""
        text_lower = text.lower().strip()
        
        # Common header/footer patterns
        header_footer_patterns = [
            r'^\d+$',  # Just a page number
            r'^page\s+\d+',  # "Page 1"
            r'^\d+\s*$',  # Page number with spaces
            r'^copyright',  # Copyright notices
            r'^\u00a9',  # Copyright symbol
            r'^©',  # Copyright symbol
            r'^www\.',  # URLs
            r'^http',  # URLs
            r'@',  # Email addresses
        ]
        
        for pattern in header_footer_patterns:
            if re.match(pattern, text_lower):
                return True
        
        # Very short text (likely page numbers)
        if len(text_lower) <= 3 and text_lower.isdigit():
            return True
        
        return False
    
    def _clean_title_text(self, title: str) -> str:
        """Clean and format title text"""
        # Remove extra whitespace
        title = ' '.join(title.split())
        
        # Remove common prefixes
        prefixes_to_remove = ['title:', 'document:', 'paper:']
        title_lower = title.lower()
        
        for prefix in prefixes_to_remove:
            if title_lower.startswith(prefix):
                title = title[len(prefix):].strip()
                break
        
        # Capitalize first letter if needed
        if title and title[0].islower():
            title = title[0].upper() + title[1:]
        
        return title