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
        print(f"Available engines: {', '.join(engines_available)}")
        sys.exit(1)
    
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    print(f"\nProcessing: {args.input}")
    print(f"Engine: {args.engine}\n")
    
    results = {}
    
    # Process with PaddleOCR
    if args.engine == "paddleocr" or args.engine == "all":
        if "paddleocr" in engines_available:
            print("Running PaddleOCR...")
            from paddleocr import PaddleOCR
            ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
            result = ocr.ocr(args.input, cls=True)
            
            texts = []
            for line in result[0] if result[0] else []:
                texts.append(line[1][0])
            
            results["paddleocr"] = {
                "text": "\n".join(texts),
                "lines": len(texts)
            }
            print(f"✓ PaddleOCR: Extracted {len(texts)} lines\n")
    
    # Process with EasyOCR
    if args.engine == "easyocr" or args.engine == "all":
        if "easyocr" in engines_available:
            print("Running EasyOCR...")
            import easyocr
            reader = easyocr.Reader(['en'], gpu=False)
            result = reader.readtext(args.input)
            
            texts = [item[1] for item in result]
            results["easyocr"] = {
                "text": "\n".join(texts),
                "lines": len(texts)
            }
            print(f"✓ EasyOCR: Extracted {len(texts)} lines\n")
    
    # Process with Tesseract
    if args.engine == "tesseract" or args.engine == "all":
        if "tesseract" in engines_available:
            print("Running Tesseract...")
            import pytesseract
            from PIL import Image
            img = Image.open(args.input)
            text = pytesseract.image_to_string(img)
            
            results["tesseract"] = {
                "text": text,
                "lines": len(text.split("\n"))
            }
            print(f"✓ Tesseract: Extracted text\n")
    
    # Print results
    print("=" * 50)
    print("RESULTS:")
    print("=" * 50)
    
    for engine_name, data in results.items():
        print(f"\n[{engine_name.upper()}]")
        print(data["text"])
        print(f"\n({data['lines']} lines extracted)")
        print("-" * 50)
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Results saved to: {args.output}")

if __name__ == "__main__":
    main()
