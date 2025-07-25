# Adobe Hackathon Round 1A - Document Outline Extraction

## 🎯 Overview

This solution extracts structured outlines from PDF documents using **font-based analysis** (no ML models required). It identifies the document title and hierarchical headings (H1, H2, H3) with their corresponding page numbers.

## 🏗️ Architecture

### **No ML Models Used** ✅
- **Pure algorithmic approach** using font size, weight, and positioning analysis
- **Zero model size** - well under the 200MB constraint
- **Fast execution** - no model loading overhead
- **Fully offline** - no external dependencies

### Core Components

```
round-1a/
├── main.py                 # Entry point and orchestration
├── pdf_parser.py          # PDF text extraction with formatting (PyMuPDF)
├── heading_extractor.py   # Font-based heading detection algorithm
├── utils.py               # JSON formatting, validation, utilities
├── requirements.txt       # Python dependencies (~15-20MB total)
├── Dockerfile            # Container configuration
└── README.md             # This documentation
├──
```

## 🔧 Technical Approach

### Font-Based Heading Detection

1. **PDF Parsing**: Extract text with complete formatting information (font size, weight, position)
2. **Statistical Analysis**: Calculate document-wide font statistics
3. **Heading Scoring**: Multi-factor scoring system:
   - Font size relative to document average
   - Bold formatting detection
   - Position analysis (left-alignment)
   - Pattern matching (numbering schemes)
   - Keyword recognition
   - Text length and case analysis

4. **Hierarchical Classification**: 
   - Font size hierarchy mapping
   - Numbering pattern refinement (1., 1.1., 1.1.1.)
   - Context-aware level assignment

### Title Extraction Strategy

- Analyzes first page for largest, prominently positioned text
- Filters out headers, footers, and page numbers
- Applies text cleaning and formatting

## 🚀 Usage

### Docker Execution (Competition Format)

```bash
# Build the container
docker build -t adobe-1a .

# Run with mounted volumes (no network access)
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  adobe-1a
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run directly
python main.py
```

## 📊 Performance Characteristics

- **Execution Time**: ~2-5 seconds for 50-page PDF (well under 10s limit)
- **Memory Usage**: ~50-100MB peak memory
- **Model Size**: 0MB (rule-based approach)
- **Accuracy**: High precision on structured documents with clear font hierarchies

## 📝 Input/Output Format

### Input
- PDF files in `/app/input/` directory
- Up to 50 pages per document

### Output Format
```json
{
  "title": "Document Title",
  "outline": [
    {"level": "H1", "text": "Chapter 1: Introduction", "page": 1},
    {"level": "H2", "text": "Background", "page": 2},
    {"level": "H3", "text": "Historical Context", "page": 3}
  ]
}
```

## 🎯 Algorithm Details

### Heading Detection Scoring

Each text block receives a score (0-1) based on:

- **Font Size Factor** (0.3): Larger fonts score higher
- **Bold Factor** (0.2): Bold text increases score
- **Position Factor** (0.1): Left-aligned text preferred
- **Pattern Factor** (0.25): Matches numbering patterns
- **Keyword Factor** (0.15): Contains heading keywords
- **Length Factor** (0.1): Appropriate length for headings
- **Case Factor** (0.1): Title case or ALL CAPS

### Classification Rules

1. **Font Size Hierarchy**: Largest fonts → H1, smaller → H2, H3
2. **Pattern Override**: Numbering patterns can override font-based classification
   - `1.` patterns → H1
   - `1.1.` patterns → H2  
   - `1.1.1.` patterns → H3

## 🔍 Supported Document Types

Works best with:
- ✅ Academic papers and research documents
- ✅ Technical manuals and guides
- ✅ Business reports and presentations
- ✅ Books and chapters with clear hierarchies
- ✅ Multi-language documents (font analysis is language-agnostic)

## 🛠️ Dependencies

```
PyMuPDF==1.23.26    # Primary PDF processing (~10MB)
pdfplumber==0.10.0  # Backup PDF processing (~5MB)  
regex==2023.10.3    # Enhanced pattern matching (~2MB)
```

**Total Size**: ~15-20MB (well under 200MB limit)

## 🚨 Constraints Compliance

- ✅ **Execution Time**: ≤10 seconds for 50-page PDF
- ✅ **Model Size**: 0MB (<200MB limit)  
- ✅ **CPU Only**: No GPU dependencies
- ✅ **Offline**: No internet access required
- ✅ **AMD64**: Compatible with competition environment
- ✅ **Docker**: Full containerization support

## 🔧 Troubleshooting

### Common Issues

1. **No headings detected**: Document may lack clear font hierarchies
2. **Incorrect classification**: Adjust scoring thresholds in `heading_extractor.py`
3. **Missing title**: Check first page for prominent text
4. **Docker build fails**: Ensure system dependencies are available

### Debug Mode

Enable verbose logging by setting environment variable:
```bash
export DEBUG=1
python main.py
```

## 📈 Performance Optimization

- **Early filtering**: Skip obvious non-headings quickly
- **Efficient font analysis**: Cache document statistics
- **Memory management**: Process pages sequentially
- **Minimal dependencies**: Only essential libraries

---

