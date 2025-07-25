#!/usr/bin/env python3
"""
Test script for Adobe Hackathon Round 1A solution
"""

import os
import sys
import time
import json
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_parser import PDFParser
from heading_extractor import HeadingExtractor
from utils import validate_output, print_extraction_summary, create_sample_output

def test_components():
    """Test individual components"""
    print("Testing individual components...")
    
    # Test PDF Parser
    print("\n1. Testing PDF Parser...")
    try:
        parser = PDFParser()
        print("✓ PDF Parser initialized successfully")
    except Exception as e:
        print(f"✗ PDF Parser initialization failed: {e}")
        return False
    
    # Test Heading Extractor
    print("\n2. Testing Heading Extractor...")
    try:
        extractor = HeadingExtractor()
        print("✓ Heading Extractor initialized successfully")
    except Exception as e:
        print(f"✗ Heading Extractor initialization failed: {e}")
        return False
    
    # Test validation
    print("\n3. Testing Output Validation...")
    sample_output = create_sample_output()
    if validate_output(sample_output):
        print("✓ Output validation working correctly")
    else:
        print("✗ Output validation failed")
        return False
    
    return True

def test_with_sample_pdf(pdf_path):
    """Test with a sample PDF file"""
    print(f"\nTesting with PDF: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"✗ PDF file not found: {pdf_path}")
        return False
    
    try:
        start_time = time.time()
        
        # Initialize components
        parser = PDFParser()
        extractor = HeadingExtractor()
        
        # Parse PDF
        print("Parsing PDF...")
        pages_data = parser.parse_pdf(pdf_path)
        
        if not pages_data:
            print("✗ Failed to parse PDF")
            return False
        
        print(f"✓ Parsed {len(pages_data)} pages")
        
        # Extract title and headings
        print("Extracting title and headings...")
        title = extractor.extract_title(pages_data)
        headings = extractor.extract_headings(pages_data)
        
        # Create result
        result = {
            "title": title,
            "outline": headings
        }
        
        # Validate
        if not validate_output(result):
            print("✗ Output validation failed")
            return False
        
        # Print summary
        print_extraction_summary(result)
        
        # Check performance
        processing_time = time.time() - start_time
        print(f"\nProcessing time: {processing_time:.2f} seconds")
        
        if processing_time > 10:
            print("⚠️  Warning: Processing time exceeds 10 second limit")
        else:
            print("✓ Processing time within limits")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_docker_simulation():
    """Simulate Docker environment structure"""
    print("\nTesting Docker environment simulation...")
    
    # Create test directory structure
    test_dir = Path("test_docker_sim")
    input_dir = test_dir / "input"
    output_dir = test_dir / "output"
    
    try:
        # Create directories
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"✓ Created test directories:")
        print(f"  Input: {input_dir}")
        print(f"  Output: {output_dir}")
        
        # Create a sample output to test JSON saving
        sample_data = create_sample_output()
        output_file = output_dir / "test_output.json"
        
        with open(output_file, 'w') as f:
            json.dump(sample_data, f, indent=2)
        
        print(f"✓ Created sample output: {output_file}")
        
        # Verify file exists and is valid JSON
        if output_file.exists():
            with open(output_file, 'r') as f:
                loaded_data = json.load(f)
            
            if validate_output(loaded_data):
                print("✓ Docker environment simulation successful")
                return True
        
        return False
        
    except Exception as e:
        print(f"✗ Docker simulation failed: {e}")
        return False
    
    finally:
        # Clean up test directories
        import shutil
        if test_dir.exists():
            shutil.rmtree(test_dir)

def check_dependencies():
    """Check if all required dependencies are available"""
    print("Checking dependencies...")
    
    required_modules = [
        'fitz',  # PyMuPDF
        'pdfplumber',
        'json',
        'pathlib',
        're'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"✗ {module} - MISSING")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\nMissing modules: {missing_modules}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✓ All dependencies available")
        return True

def run_performance_test():
    """Test performance characteristics"""
    print("\nRunning performance tests...")
    
    # Test heading detection with various text samples
    extractor = HeadingExtractor()
    
    test_cases = [
        "1. Introduction",
        "Chapter 1: Getting Started", 
        "METHODOLOGY AND APPROACH",
        "2.1 Background Information",
        "This is regular paragraph text that should not be detected as a heading.",
        "3.2.1 Detailed Implementation"
    ]
    
    print("Testing heading detection patterns:")
    for text in test_cases:
        # Simulate a text block
        mock_block = {
            'text': text,
            'font_size': 14,
            'is_bold': True,
            'x_position': 50,
            'y_position': 100
        }
        
        doc_stats = {'avg_font_size': 12}
        score = extractor._calculate_heading_score(mock_block, doc_stats)
        
        print(f"  '{text[:30]}...' -> Score: {score:.2f}")
    
    print("✓ Performance test completed")

def main():
    """Main test function"""
    print("="*60)
    print("ADOBE HACKATHON ROUND 1A - SOLUTION TEST")
    print("="*60)
    
    all_tests_passed = True
    
    # Test 1: Dependencies
    if not check_dependencies():
        all_tests_passed = False
        print("\n⚠️  Install dependencies first: pip install -r requirements.txt")
    
    # Test 2: Components
    if not test_components():
        all_tests_passed = False
    
    # Test 3: Docker simulation
    if not test_docker_simulation():
        all_tests_passed = False
    
    # Test 4: Performance
    run_performance_test()
    
    # Test 5: Sample PDF (if available)
    sample_pdfs = [
        "sample.pdf",
        "test.pdf", 
        "input/sample.pdf"
    ]
    
    pdf_tested = False
    for pdf_path in sample_pdfs:
        if os.path.exists(pdf_path):
            if test_with_sample_pdf(pdf_path):
                pdf_tested = True
                break
            else:
                all_tests_passed = False
    
    if not pdf_tested:
        print(f"\n⚠️  No sample PDF found. Tested paths: {sample_pdfs}")
        print("   Place a sample PDF to test full functionality")
    
    # Final results
    print("\n" + "="*60)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED - Solution ready for submission!")
    else:
        print("❌ SOME TESTS FAILED - Check errors above")
    print("="*60)
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)