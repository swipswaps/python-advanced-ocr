# Quick Start Guide

## 1. Clone and Setup

```bash
git clone https://github.com/swipswaps/python-advanced-ocr.git
cd python-advanced-ocr
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## 2. Install OCR Engines

### Option A: Install PaddleOCR (Recommended for noisy images)

```bash
pip install paddleocr paddlepaddle opencv-python Pillow numpy
```

### Option B: Install EasyOCR

```bash
pip install easyocr opencv-python Pillow numpy
```

### Option C: Install Tesseract (Fastest, requires binary)

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
pip install pytesseract Pillow
```

**macOS:**
```bash
brew install tesseract
pip install pytesseract Pillow
```

**Windows:**
1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install it
3. Run: `pip install pytesseract Pillow`

## 3. Test with Your Image

```bash
# Copy your HEIC or image file to the directory
# For example: IMG_0371.heic

# Run OCR with PaddleOCR
python3 ocr_tool.py --engine paddleocr --input IMG_0371.heic

# Or try all available engines
python3 ocr_tool.py --engine all --input IMG_0371.heic

# Save results to JSON
python3 ocr_tool.py --engine paddleocr --input IMG_0371.heic --output results.json
```

## 4. Compare Results

The tool will show you the extracted text from each engine. Compare them to see which works best for your images.

## Expected Output

```
Advanced OCR Tool
==================================================
✓ PaddleOCR available
==================================================

Processing: IMG_0371.heic
Engine: paddleocr

Running PaddleOCR...
✓ PaddleOCR: Extracted 15 lines

==================================================
RESULTS:
==================================================

[PADDLEOCR]
Canadian Solar 370-395W Solar
Panels (90,284 Units)
...

(15 lines extracted)
--------------------------------------------------
```

## Tips for Best Results

1. **For noisy/grainy images**: Use PaddleOCR
2. **For low contrast**: Try EasyOCR
3. **For clean scans**: Tesseract is fastest
4. **Not sure?**: Use `--engine all` to compare

## Troubleshooting

### "No module named 'paddleocr'"
```bash
pip install paddleocr paddlepaddle
```

### "Tesseract not found"
Install the Tesseract binary (see Option C above)

### Out of memory
Process one image at a time, or use Tesseract (uses less memory)

## Next Steps

- See `README.md` for full documentation
- See `INSTALL.md` for detailed installation instructions
- Try different engines to find what works best for your images
