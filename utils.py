"""
Utility functions for JSON handling, validation, and file operations
"""

import json
import os
from typing import Dict, Any, List
from pathlib import Path

def save_json_output(data: Dict[str, Any], output_path: str) -> bool:
    """
    Save the extraction result to JSON file
    
    Args:
        data (Dict): The result data to save
        output_path (str): Path to save the JSON file
        
    Returns:
        bool: Success status
    """
    try:
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON with proper formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Output saved to: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error saving JSON to {output_path}: {str(e)}")
        return False

def validate_output(data: Dict[str, Any]) -> bool:
    """
    Validate the output format according to competition requirements
    
    Args:
        data (Dict): The data to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    
    try:
        # Check required top-level keys
        if not isinstance(data, dict):
            print("Error: Output must be a dictionary")
            return False
        
        if 'title' not in data:
            print("Error: Missing 'title' field")
            return False
        
        if 'outline' not in data:
            print("Error: Missing 'outline' field")
            return False
        
        # Validate title
        if not isinstance(data['title'], str):
            print("Error: 'title' must be a string")
            return False
        
        # Validate outline
        if not isinstance(data['outline'], list):
            print("Error: 'outline' must be a list")
            return False
        
        # Validate each heading in outline
        for i, heading in enumerate(data['outline']):
            if not isinstance(heading, dict):
                print(f"Error: Heading {i} must be a dictionary")
                return False
            
            # Check required fields
            required_fields = ['level', 'text', 'page']
            for field in required_fields:
                if field not in heading:
                    print(f"Error: Heading {i} missing '{field}' field")
                    return False
            
            # Validate field types and values
            if heading['level'] not in ['H1', 'H2', 'H3']:
                print(f"Error: Heading {i} level must be H1, H2, or H3")
                return False
            
            if not isinstance(heading['text'], str) or not heading['text'].strip():
                print(f"Error: Heading {i} text must be a non-empty string")
                return False
            
            if not isinstance(heading['page'], int) or heading['page'] < 1:
                print(f"Error: Heading {i} page must be a positive integer")
                return False
        
        return True
        
    except Exception as e:
        print(f"Validation error: {str(e)}")
        return False

def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load JSON file and return data
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        Dict: Loaded JSON data, empty dict if error
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON from {file_path}: {str(e)}")
        return {}

def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text (str): Input text
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    
    return text.strip()

def format_heading_text(text: str) -> str:
    """
    Format heading text by removing numbering and cleaning
    
    Args:
        text (str): Raw heading text
        
    Returns:
        str: Formatted heading text
    """
    if not text:
        return ""
    
    # Clean the text first
    text = clean_text(text)
    
    # Remove common numbering patterns but keep the content
    import re
    
    # Remove patterns like "1. ", "1.1. ", "1.1.1. "
    text = re.sub(r'^\d+(\.\d+)*\.?\s+', '', text)
    
    # Remove patterns like "I. ", "II. ", "III. "
    text = re.sub(r'^[IVX]+\.?\s+', '', text, flags=re.IGNORECASE)
    
    # Remove patterns like "A. ", "B. "
    text = re.sub(r'^[A-Z]\.?\s+', '', text)
    
    # Remove patterns like "(a) ", "(b) "
    text = re.sub(r'^\([a-z]\)\s+', '', text)
    
    # Clean up extra spaces
    text = ' '.join(text.split())
    
    return text.strip()

def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in megabytes
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        float: File size in MB
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except Exception:
        return 0.0

def validate_pdf_constraints(pdf_path: str) -> bool:
    """
    Validate PDF meets competition constraints
    
    Args:
        pdf_path (str): Path to PDF file
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        import fitz  # PyMuPDF
        
        # Check file size (should be reasonable)
        file_size_mb = get_file_size_mb(pdf_path)
        if file_size_mb > 100:  # 100MB limit (reasonable assumption)
            print(f"Warning: PDF file is large ({file_size_mb:.1f} MB)")
        
        # Check page count
        doc = fitz.open(pdf_path)
        page_count = len(doc)
        doc.close()
        
        if page_count > 50:
            print(f"Error: PDF has {page_count} pages (max 50 allowed)")
            return False
        
        print(f"PDF validation passed: {page_count} pages, {file_size_mb:.1f} MB")
        return True
        
    except Exception as e:
        print(f"Error validating PDF {pdf_path}: {str(e)}")
        return False

def print_extraction_summary(result: Dict[str, Any]) -> None:
    """
    Print a summary of the extraction results
    
    Args:
        result (Dict): The extraction result
    """
    print("\n" + "="*50)
    print("EXTRACTION SUMMARY")
    print("="*50)
    
    print(f"Title: {result.get('title', 'N/A')}")
    
    outline = result.get('outline', [])
    print(f"Total headings found: {len(outline)}")
    
    if outline:
        # Count by level
        level_counts = {'H1': 0, 'H2': 0, 'H3': 0}
        pages_with_headings = set()
        
        for heading in outline:
            level = heading.get('level', 'Unknown')
            if level in level_counts:
                level_counts[level] += 1
            pages_with_headings.add(heading.get('page', 0))
        
        print(f"H1 headings: {level_counts['H1']}")
        print(f"H2 headings: {level_counts['H2']}")
        print(f"H3 headings: {level_counts['H3']}")
        print(f"Pages with headings: {len(pages_with_headings)}")
        
        print("\nFirst few headings:")
        for i, heading in enumerate(outline[:5]):
            print(f"  {heading['level']} (p.{heading['page']}): {heading['text'][:60]}...")
    
    print("="*50)

def create_sample_output() -> Dict[str, Any]:
    """
    Create a sample output for testing
    
    Returns:
        Dict: Sample output structure
    """
    return {
        "title": "Understanding Artificial Intelligence",
        "outline": [
            {"level": "H1", "text": "Introduction", "page": 1},
            {"level": "H2", "text": "What is AI?", "page": 2},
            {"level": "H3", "text": "History of AI", "page": 3},
            {"level": "H3", "text": "Types of AI", "page": 4},
            {"level": "H2", "text": "Machine Learning", "page": 5},
            {"level": "H3", "text": "Supervised Learning", "page": 6},
            {"level": "H3", "text": "Unsupervised Learning", "page": 7},
            {"level": "H1", "text": "Applications", "page": 8},
            {"level": "H2", "text": "Healthcare", "page": 9},
            {"level": "H2", "text": "Finance", "page": 10},
            {"level": "H1", "text": "Conclusion", "page": 11}
        ]
    }