#!/usr/bin/env python3
"""
Simple setup script to create folders and test the solution
"""

import os
from pathlib import Path

def create_folders():
    """Create the required input and output folders"""
    print("Creating required folders...")
    
    # Create input and output folders
    input_dir = Path("input")
    output_dir = Path("output")
    
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    
    print(f"✅ Created folder: {input_dir.absolute()}")
    print(f"✅ Created folder: {output_dir.absolute()}")
    
    # Check if folders exist
    if input_dir.exists() and output_dir.exists():
        print("✅ All folders created successfully!")
        return True
    else:
        print("❌ Failed to create folders")
        return False

def check_pdf_files():
    """Check if there are any PDF files in the input folder"""
    input_dir = Path("input")
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if pdf_files:
        print(f"✅ Found {len(pdf_files)} PDF file(s):")
        for pdf in pdf_files:
            print(f"   - {pdf.name}")
        return True
    else:
        print("⚠️  No PDF files found in 'input' folder")
        print("   Please add some PDF files to test the solution")
        return False

def create_test_structure():
    """Create the complete folder structure"""
    print("Setting up Adobe Hackathon Round 1A...")
    print("=" * 50)
    
    # Create folders
    if not create_folders():
        return False
    
    # Check for PDFs
    has_pdfs = check_pdf_files()
    
    print("\n" + "=" * 50)
    print("SETUP COMPLETE!")
    print("=" * 50)
    
    if has_pdfs:
        print("🎉 Ready to run the solution!")
        print("   Run: python main.py")
    else:
        print("📝 Next steps:")
        print("   1. Add PDF files to the 'input' folder")
        print("   2. Run: python main.py")
    
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    create_test_structure()