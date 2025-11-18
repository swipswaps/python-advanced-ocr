#!/usr/bin/env python3
"""
Advanced OCR Tool - Supports PaddleOCR, EasyOCR, Surya, Tesseract
Handles HEIC images, provides confidence scores, and supports batch processing
"""
import argparse
import json
import os
import sys
from pathlib import Path
import time
from typing import Dict, List, Any, Optional

# Check available engines
engines_available = []
engine_modules = {}

try:
    from paddleocr import PaddleOCR
    engines_available.append("paddleocr")
    engine_modules["paddleocr"] = PaddleOCR
except ImportError:
    pass

try:
    import easyocr
    engines_available.append("easyocr")
    engine_modules["easyocr"] = easyocr
except ImportError:
    pass

try:
    from surya.ocr import run_ocr
    from surya.model.detection.model import load_model as load_det_model
    from surya.model.detection.processor import load_processor as load_det_processor
    from surya.model.recognition.model import load_model as load_rec_model
    from surya.model.recognition.processor import load_processor as load_rec_processor
    from surya.languages import CODE_TO_LANGUAGE
    from PIL import Image as PILImage
    engines_available.append("surya")
    engine_modules["surya"] = {
        "run_ocr": run_ocr,
        "load_det_model": load_det_model,
        "load_det_processor": load_det_processor,
        "load_rec_model": load_rec_model,
        "load_rec_processor": load_rec_processor,
    }
except ImportError:
    pass

try:
    import pytesseract
    from PIL import Image
    engines_available.append("tesseract")
    engine_modules["tesseract"] = pytesseract
except ImportError:
    pass

# HEIC support
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIC_SUPPORTED = True
except ImportError:
    HEIC_SUPPORTED = False


def convert_heic_if_needed(image_path: str) -> str:
    """Convert HEIC to JPEG if needed, return path to usable image"""
    if not HEIC_SUPPORTED:
        return image_path
    
    if image_path.lower().endswith(('.heic', '.heif')):
        try:
            from PIL import Image
            print(f"Converting HEIC image: {image_path}")
            img = Image.open(image_path)
            
            # Create temp JPEG path
            jpeg_path = image_path.rsplit('.', 1)[0] + '_converted.jpg'
            img.convert('RGB').save(jpeg_path, 'JPEG', quality=95)
            print(f"✓ Converted to: {jpeg_path}")
            return jpeg_path
        except Exception as e:
            print(f"Warning: HEIC conversion failed: {e}")
            return image_path
    
    return image_path


def process_paddleocr(image_path: str) -> Dict[str, Any]:
    """Process image with PaddleOCR"""
    start_time = time.time()
    
    try:
        ocr = engine_modules["paddleocr"](use_angle_cls=True, lang='en', show_log=False)
        result = ocr.ocr(image_path, cls=True)
        
        texts = []
        confidences = []
        
        if result and result[0]:
            for line in result[0]:
                texts.append(line[1][0])
                confidences.append(float(line[1][1]))
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            "engine": "PaddleOCR",
            "text": "\n".join(texts),
            "confidence": round(avg_confidence, 4),
            "lines": len(texts),
            "processing_time": round(time.time() - start_time, 2),
            "success": True
        }
    except Exception as e:
        return {
            "engine": "PaddleOCR",
            "error": str(e),
            "success": False,
            "processing_time": round(time.time() - start_time, 2)
        }


def process_easyocr(image_path: str) -> Dict[str, Any]:
    """Process image with EasyOCR"""
    start_time = time.time()
    
    try:
        reader = engine_modules["easyocr"].Reader(['en'], gpu=False, verbose=False)
        result = reader.readtext(image_path)
        
        texts = [item[1] for item in result]
        confidences = [float(item[2]) for item in result]
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            "engine": "EasyOCR",
            "text": "\n".join(texts),
            "confidence": round(avg_confidence, 4),
            "lines": len(texts),
            "processing_time": round(time.time() - start_time, 2),
            "success": True
        }
    except Exception as e:
        return {
            "engine": "EasyOCR",
            "error": str(e),
            "success": False,
            "processing_time": round(time.time() - start_time, 2)
        }


def process_surya(image_path: str) -> Dict[str, Any]:
    """Process image with Surya OCR"""
    start_time = time.time()
    
    try:
        from PIL import Image as PILImage
        
        # Load models
        det_model = engine_modules["surya"]["load_det_model"]()
        det_processor = engine_modules["surya"]["load_det_processor"]()
        rec_model = engine_modules["surya"]["load_rec_model"]()
        rec_processor = engine_modules["surya"]["load_rec_processor"]()
        
        # Load image
        image = PILImage.open(image_path)
        
        # Run OCR
        predictions = engine_modules["surya"]["run_ocr"](
            [image], 
            [["en"]], 
            det_model, 
            det_processor, 
            rec_model, 
            rec_processor
        )
        
        texts = []
        confidences = []
        
        if predictions and len(predictions) > 0:
            for text_line in predictions[0].text_lines:
                texts.append(text_line.text)
                confidences.append(float(text_line.confidence))
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            "engine": "Surya",
            "text": "\n".join(texts),
            "confidence": round(avg_confidence, 4),
            "lines": len(texts),
            "processing_time": round(time.time() - start_time, 2),
            "success": True
        }
    except Exception as e:
        return {
            "engine": "Surya",
            "error": str(e),
            "success": False,
            "processing_time": round(time.time() - start_time, 2)
        }


def process_tesseract(image_path: str) -> Dict[str, Any]:
    """Process image with Tesseract"""
    start_time = time.time()
    
    try:
        from PIL import Image
        img = Image.open(image_path)
        
        # Get text and confidence data
        text = engine_modules["tesseract"].image_to_string(img)
        data = engine_modules["tesseract"].image_to_data(img, output_type=engine_modules["tesseract"].Output.DICT)
        
        # Calculate average confidence (excluding -1 values)
        confidences = [float(conf) for conf in data['conf'] if conf != -1]
        avg_confidence = sum(confidences) / len(confidences) / 100.0 if confidences else 0.0
        
        return {
            "engine": "Tesseract",
            "text": text.strip(),
            "confidence": round(avg_confidence, 4),
            "lines": len(text.split("\n")),
            "processing_time": round(time.time() - start_time, 2),
            "success": True
        }
    except Exception as e:
        return {
            "engine": "Tesseract",
            "error": str(e),
            "success": False,
            "processing_time": round(time.time() - start_time, 2)
        }


def process_image(image_path: str, engines: List[str]) -> Dict[str, Any]:
    """Process a single image with specified engines"""
    
    # Convert HEIC if needed
    processed_path = convert_heic_if_needed(image_path)
    
    results = {}
    
    for engine in engines:
        if engine not in engines_available:
            results[engine] = {
                "engine": engine,
                "error": "Engine not installed",
                "success": False
            }
            continue
        
        print(f"Running {engine.upper()}...")
        
        if engine == "paddleocr":
            results[engine] = process_paddleocr(processed_path)
        elif engine == "easyocr":
            results[engine] = process_easyocr(processed_path)
        elif engine == "surya":
            results[engine] = process_surya(processed_path)
        elif engine == "tesseract":
            results[engine] = process_tesseract(processed_path)
        
        if results[engine]["success"]:
            print(f"✓ {engine.upper()}: Extracted {results[engine]['lines']} lines "
                  f"(confidence: {results[engine]['confidence']:.2%}, "
                  f"time: {results[engine]['processing_time']}s)")
        else:
            print(f"✗ {engine.upper()}: Failed - {results[engine].get('error', 'Unknown error')}")
        print()
    
    # Clean up converted file if created
    if processed_path != image_path and os.path.exists(processed_path):
        try:
            os.remove(processed_path)
        except:
            pass
    
    return results


def main():
    print("Advanced OCR Tool")
    print("=" * 70)
    
    # Show available engines
    if engines_available:
        print("Available engines:")
        for engine in engines_available:
            print(f"  ✓ {engine}")
    else:
        print("✗ No OCR engines installed!")
        print("\nInstall at least one engine:")
        print("  pip install paddleocr paddlepaddle")
        print("  pip install easyocr")
        print("  pip install surya-ocr")
        print("  pip install pytesseract")
        sys.exit(1)
    
    if HEIC_SUPPORTED:
        print("  ✓ HEIC support enabled")
    
    print("=" * 70)
    print()
    
    parser = argparse.ArgumentParser(
        description="Advanced OCR Tool with multiple engine support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input image.jpg --engine paddleocr
  %(prog)s --input photo.heic --engine all --output results.json
  %(prog)s --input-dir ./images/ --engine paddleocr --output-dir ./results/
        """
    )
    
    parser.add_argument("--engine", 
                       choices=["paddleocr", "easyocr", "surya", "tesseract", "all"], 
                       default="paddleocr", 
                       help="OCR engine to use (default: paddleocr)")
    
    parser.add_argument("--input", 
                       help="Input image file")
    
    parser.add_argument("--input-dir",
                       help="Input directory for batch processing")
    
    parser.add_argument("--output", 
                       help="Output JSON file")
    
    parser.add_argument("--output-dir",
                       help="Output directory for batch processing")
    
    args = parser.parse_args()
    
    # Validate input
    if not args.input and not args.input_dir:
        parser.error("Either --input or --input-dir is required")
    
    if args.input and args.input_dir:
        parser.error("Cannot use both --input and --input-dir")
    
    # Determine engines to use
    if args.engine == "all":
        engines_to_use = engines_available
    else:
        if args.engine not in engines_available:
            print(f"Error: {args.engine} is not installed!")
            print(f"Available engines: {', '.join(engines_available)}")
            sys.exit(1)
        engines_to_use = [args.engine]
    
    # Single file processing
    if args.input:
        if not os.path.exists(args.input):
            print(f"Error: Input file not found: {args.input}")
            sys.exit(1)
        
        print(f"Processing: {args.input}")
        print(f"Engines: {', '.join(engines_to_use)}")
        print()
        
        results = process_image(args.input, engines_to_use)
        
        # Print results
        print("=" * 70)
        print("RESULTS:")
        print("=" * 70)
        
        for engine_name, data in results.items():
            print(f"\n[{engine_name.upper()}]")
            if data["success"]:
                print(data["text"])
                print(f"\nConfidence: {data['confidence']:.2%}")
                print(f"Lines: {data['lines']}")
                print(f"Processing time: {data['processing_time']}s")
            else:
                print(f"ERROR: {data.get('error', 'Unknown error')}")
            print("-" * 70)
        
        # Save to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n✓ Results saved to: {args.output}")
    
    # Batch processing
    elif args.input_dir:
        if not os.path.isdir(args.input_dir):
            print(f"Error: Input directory not found: {args.input_dir}")
            sys.exit(1)
        
        # Find all image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.heic', '.heif'}
        image_files = []
        
        for root, dirs, files in os.walk(args.input_dir):
            for file in files:
                if Path(file).suffix.lower() in image_extensions:
                    image_files.append(os.path.join(root, file))
        
        if not image_files:
            print(f"Error: No image files found in {args.input_dir}")
            sys.exit(1)
        
        print(f"Found {len(image_files)} images in {args.input_dir}")
        print(f"Engines: {', '.join(engines_to_use)}")
        print()
        
        all_results = {}
        
        for i, image_path in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] Processing: {image_path}")
            print("-" * 70)
            
            results = process_image(image_path, engines_to_use)
            all_results[image_path] = results
        
        # Save results
        if args.output_dir:
            os.makedirs(args.output_dir, exist_ok=True)
            output_file = os.path.join(args.output_dir, "batch_results.json")
        else:
            output_file = "batch_results.json"
        
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\n✓ Batch results saved to: {output_file}")
        print(f"✓ Processed {len(image_files)} images")


if __name__ == "__main__":
    main()
