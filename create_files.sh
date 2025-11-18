#!/bin/bash

# Create ocr_tool.py
cat > ocr_tool.py << "EOFPY"
#!/usr/bin/env python3
"""
Advanced OCR Tool - Supports PaddleOCR, EasyOCR, Surya, Tesseract
"""
import argparse
import json
import os
import sys
from pathlib import Path
import time

print("Advanced OCR Tool")
print("=" * 50)

# Check available engines
engines_available = []

try:
    from paddleocr import PaddleOCR
    engines_available.append("paddleocr")
    print("✓ PaddleOCR available")
except ImportError:
    print("✗ PaddleOCR not installed")

try:
    import easyocr
    engines_available.append("easyocr")
    print("✓ EasyOCR available")
except ImportError:
    print("✗ EasyOCR not installed")

try:
    from surya.ocr import run_ocr
    engines_available.append("surya")
    print("✓ Surya OCR available")
except ImportError:
    print("✗ Surya OCR not installed")

try:
    import pytesseract
    engines_available.append("tesseract")
    print("✓ Tesseract available")
except ImportError:
    print("✗ Tesseract not installed")

print("=" * 50)

def main():
    parser = argparse.ArgumentParser(description="Advanced OCR Tool")
    parser.add_argument("--engine", choices=["paddleocr", "easyocr", "surya", "tesseract", "all"], 
                       default="paddleocr", help="OCR engine to use")
    parser.add_argument("--input", required=True, help="Input image file")
    parser.add_argument("--output", help="Output file (JSON)")
    
    args = parser.parse_args()
    
    if args.engine not in engines_available and args.engine != "all":
        print(f"Error: {args.engine} is not installed!")
        print(f"Available engines: {,
