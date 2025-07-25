#!/usr/bin/env python3
"""
Adobe Hackathon - Round 1A: Document Outline Extraction
LOCAL TESTING VERSION - Works on Windows/Mac/Linux
"""

import os
import sys
import json
import time
from pathlib import Path

# Import our custom modules
from pdf_parser import PDFParser
from heading_extractor import HeadingExtractor
from utils import save_json_output, validate_output

def process_pdf(input_path, output_path):
    """
    Process a single PDF and extract its outline
    
    Args:
        input_path (str): Path to input PDF
        output_path (str): Path to save output JSON
    
    Returns:
        bool: Success status
    """
    try:
        start_time = time.time()
        
        print(f"📄 Processing: {input_path}")
        
        # Initialize components
        parser = PDFParser()
        extractor = HeadingExtractor()
        
        # Parse PDF and extract text with formatting info
        print("   📖 Parsing PDF...")
        pages_data = parser.parse_pdf(input_path)
        
        if not pages_data:
            print(f"❌ Error: Could not parse PDF {input_path}")
            return False
        
        print(f"   ✅ Parsed {len(pages_data)} pages")
        
        # Extract document title
        print("   🏷️  Extracting title...")
        title = extractor.extract_title(pages_data)
        print(f"   📝 Title: {title}")
        
        # Extract headings
        print("   🔍 Extracting headings...")
        headings = extractor.extract_headings(pages_data)
        print(f"   📋 Found {len(headings)} headings")
        
        # Create output structure
        result = {
            "title": title,
            "outline": headings
        }
        
        # Validate output format
        print("   ✅ Validating output...")
        if not validate_output(result):
            print("❌ Error: Output validation failed")
            return False
        
        # Save to JSON
        print("   💾 Saving results...")
        success = save_json_output(result, output_path)
        
        processing_time = time.time() - start_time
        print(f"   ⏱️  Processed in {processing_time:.2f} seconds")
        
        if processing_time > 10:
            print("   ⚠️  Warning: Processing took longer than 10 seconds")
        
        return success
        
    except Exception as e:
        print(f"❌ Error processing {input_path}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to process all PDFs in input directory"""
    
    print("🚀 Adobe Hackathon Round 1A - Document Outline Extraction")
    print("=" * 60)
    
    # Define paths (local folders)
    input_dir = Path("input")
    output_dir = Path("output")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory: {output_dir.absolute()}")
    
    # Check if input directory exists
    if not input_dir.exists():
        print("❌ Error: Input directory not found!")
        print(f"📁 Expected location: {input_dir.absolute()}")
        print("\n🛠️  SOLUTION:")
        print("1. Create an 'input' folder in the current directory")
        print("2. Put your PDF files inside the 'input' folder")
        print("3. Run this script again")
        print("\nOr run: python setup_folders.py")
        sys.exit(1)
    
    print(f"📁 Input directory: {input_dir.absolute()}")
    
    # Find all PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ Error: No PDF files found in input directory")
        print(f"📁 Looking in: {input_dir.absolute()}")
        print("\n🛠️  SOLUTION:")
        print("1. Add PDF files to the 'input' folder")
        print("2. Make sure files have .pdf extension")
        print("3. Run this script again")
        sys.exit(1)
    
    print(f"📚 Found {len(pdf_files)} PDF file(s) to process:")
    for pdf in pdf_files:
        print(f"   - {pdf.name}")
    
    print("\n" + "="*60)
    print("PROCESSING STARTED")
    print("="*60)
    
    # Process each PDF
    success_count = 0
    total_files = len(pdf_files)
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n📄 [{i}/{total_files}] Processing: {pdf_file.name}")
        
        # Generate output filename
        output_filename = pdf_file.stem + ".json"
        output_path = output_dir / output_filename
        
        # Process the PDF
        if process_pdf(str(pdf_file), str(output_path)):
            success_count += 1
            print(f"✅ Successfully processed: {pdf_file.name}")
            print(f"💾 Output saved: {output_path.name}")
        else:
            print(f"❌ Failed to process: {pdf_file.name}")
    
    # Summary
    print("\n" + "="*60)
    print("PROCESSING COMPLETE")
    print("="*60)
    
    print(f"📊 Results: {success_count}/{total_files} files processed successfully")
    
    if success_count > 0:
        print(f"📁 Output files saved in: {output_dir.absolute()}")
        
        # Show output files
        json_files = list(output_dir.glob("*.json"))
        print(f"📋 Generated {len(json_files)} JSON file(s):")
        for json_file in json_files:
            print(f"   - {json_file.name}")
    
    if success_count == total_files:
        print("🎉 All files processed successfully!")
        sys.exit(0)
    else:
        print("⚠️  Some files failed to process. Check error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()