#!/usr/bin/env python3
"""
Advanced OCR Tool v2.1 - Performance Optimized
Supports PaddleOCR, EasyOCR, Surya, Tesseract with singleton pattern

KEY IMPROVEMENTS (v2.1):
- Singleton pattern: Initialize engines ONCE, reuse forever (10-100x faster for batch)
- Lazy loading: Only load engines when first used
- GPU auto-detection and support
- Based on official PaddleOCR recommendation: https://github.com/PaddlePaddle/PaddleOCR/discussions/14699
- Better error handling and progress indication
- Tesseract PSM configuration for improved accuracy
- Verbose/quiet modes for better UX
"""
__version__ = "2.1.0"

import argparse
import json
import os
import sys
from pathlib import Path
import time
from typing import Dict, List, Any, Optional
import tempfile
import atexit

# Progress bar
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

# HEIC support
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIC_SUPPORTED = True
except ImportError:
    HEIC_SUPPORTED = False

# Track temporary files for cleanup
temp_files = []

# Global verbose flag
VERBOSE = True

def cleanup_temp_files():
    """Clean up temporary converted files"""
    for f in temp_files:
        try:
            if os.path.exists(f):
                os.remove(f)
        except:
            pass

atexit.register(cleanup_temp_files)


def detect_gpu():
    """Detect if GPU/CUDA is available"""
    try:
        import torch
        has_cuda = torch.cuda.is_available()
        if has_cuda and VERBOSE:
            print(f"✓ GPU detected: {torch.cuda.get_device_name(0)}")
        return has_cuda
    except ImportError:
        return False
    except Exception:
        return False


def vprint(*args, **kwargs):
    """Print only if verbose mode is enabled"""
    if VERBOSE:
        print(*args, **kwargs)


class OCREngineManager:
    """
    Singleton manager for OCR engines.
    Based on PaddleOCR official recommendation:
    https://github.com/PaddlePaddle/PaddleOCR/discussions/14699

    Initialize engines ONCE and reuse them for all subsequent calls.
    This dramatically improves performance (10-100x faster for batch processing).
    """
    _instances = {}
    _available_engines = []

    @classmethod
    def get_available_engines(cls):
        """Get list of available engines"""
        return cls._available_engines.copy()

    @classmethod
    def get_paddleocr(cls):
        """Get or create PaddleOCR instance (singleton)"""
        if 'paddleocr' not in cls._instances:
            try:
                from paddleocr import PaddleOCR
                use_gpu = detect_gpu()
                vprint(f"🔧 Initializing PaddleOCR (one-time setup, GPU: {use_gpu})...")
                cls._instances['paddleocr'] = PaddleOCR(
                    use_angle_cls=True,
                    lang='en',
                    show_log=False,
                    use_gpu=use_gpu,
                    enable_mkldnn=True if not use_gpu else False,  # CPU optimization
                    use_mp=False,  # Disable multiprocessing for stability
                )
                if 'paddleocr' not in cls._available_engines:
                    cls._available_engines.append("paddleocr")
                vprint("✓ PaddleOCR ready")
            except ImportError:
                vprint("❌ PaddleOCR not available (pip install paddleocr paddlepaddle)")
                return None
            except Exception as e:
                vprint(f"❌ PaddleOCR initialization failed: {e}")
                return None
        return cls._instances.get('paddleocr')

    @classmethod
    def get_easyocr(cls):
        """Get or create EasyOCR instance (singleton)"""
        if 'easyocr' not in cls._instances:
            try:
                import easyocr
                use_gpu = detect_gpu()
                vprint(f"🔧 Initializing EasyOCR (one-time setup, GPU: {use_gpu})...")
                cls._instances['easyocr'] = easyocr.Reader(
                    ['en'],
                    gpu=use_gpu,
                    verbose=False,
                    download_enabled=True,
                    model_storage_directory=os.path.expanduser('~/.EasyOCR/model')
                )
                if 'easyocr' not in cls._available_engines:
                    cls._available_engines.append("easyocr")
                vprint("✓ EasyOCR ready")
            except ImportError:
                vprint("❌ EasyOCR not available (pip install easyocr)")
                return None
            except Exception as e:
                vprint(f"❌ EasyOCR initialization failed: {e}")
                return None
        return cls._instances.get('easyocr')

    @classmethod
    def get_surya(cls):
        """Get or create Surya OCR models (singleton)"""
        if 'surya' not in cls._instances:
            try:
                from surya.ocr import run_ocr
                from surya.model.detection.model import load_model as load_det_model
                from surya.model.detection.processor import load_processor as load_det_processor
                from surya.model.recognition.model import load_model as load_rec_model
                from surya.model.recognition.processor import load_processor as load_rec_processor

                vprint("🔧 Initializing Surya OCR (one-time setup, may take 1-2 minutes)...")
                cls._instances['surya'] = {
                    'run_ocr': run_ocr,
                    'det_model': load_det_model(),
                    'det_processor': load_det_processor(),
                    'rec_model': load_rec_model(),
                    'rec_processor': load_rec_processor(),
                }
                if 'surya' not in cls._available_engines:
                    cls._available_engines.append("surya")
                vprint("✓ Surya OCR ready")
            except ImportError:
                vprint("❌ Surya OCR not available (pip install surya-ocr)")
                return None
            except Exception as e:
                vprint(f"❌ Surya OCR initialization failed: {e}")
                return None
        return cls._instances.get('surya')

    @classmethod
    def get_tesseract(cls):
        """Get or verify Tesseract availability"""
        if 'tesseract' not in cls._instances:
            try:
                import pytesseract
                from PIL import Image
                # Test if tesseract is installed
                version = pytesseract.get_tesseract_version()
                cls._instances['tesseract'] = pytesseract
                if 'tesseract' not in cls._available_engines:
                    cls._available_engines.append("tesseract")
                vprint(f"✓ Tesseract {version} ready")
            except ImportError:
                vprint("❌ Tesseract not available (pip install pytesseract)")
                return None
            except Exception as e:
                vprint(f"❌ Tesseract not available: {e}")
                return None
        return cls._instances.get('tesseract')


def convert_heic_if_needed(image_path: str) -> str:
    """Convert HEIC to JPEG if needed, return path to usable image"""
    if not HEIC_SUPPORTED:
        return image_path

    if image_path.lower().endswith(('.heic', '.heif')):
        try:
            from PIL import Image
            vprint(f"📸 Converting HEIC: {os.path.basename(image_path)}")
            img = Image.open(image_path)

            # Create temp JPEG file
            temp_fd, jpeg_path = tempfile.mkstemp(suffix='.jpg', prefix='ocr_')
            os.close(temp_fd)

            img.convert('RGB').save(jpeg_path, 'JPEG', quality=95)
            temp_files.append(jpeg_path)
            vprint(f"✓ Converted to JPEG")
            return jpeg_path
        except Exception as e:
            vprint(f"⚠️  HEIC conversion failed: {e}")
            return image_path

    return image_path


def process_paddleocr(image_path: str) -> Dict[str, Any]:
    """Process image with PaddleOCR (singleton instance)"""
    start_time = time.time()

    try:
        ocr = OCREngineManager.get_paddleocr()
        if ocr is None:
            raise Exception("PaddleOCR not available")

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
    """Process image with EasyOCR (singleton instance)"""
    start_time = time.time()

    try:
        reader = OCREngineManager.get_easyocr()
        if reader is None:
            raise Exception("EasyOCR not available")

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
    """Process image with Surya OCR (singleton instance)"""
    start_time = time.time()

    try:
        from PIL import Image as PILImage

        surya = OCREngineManager.get_surya()
        if surya is None:
            raise Exception("Surya OCR not available")

        # Load image
        image = PILImage.open(image_path)

        # Run OCR with pre-loaded models
        predictions = surya['run_ocr'](
            [image],
            [["en"]],
            surya['det_model'],
            surya['det_processor'],
            surya['rec_model'],
            surya['rec_processor']
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
    """
    Process image with Tesseract
    Uses PSM 3 (automatic page segmentation) for best results
    Based on: https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html
    """
    start_time = time.time()

    try:
        pytesseract = OCREngineManager.get_tesseract()
        if pytesseract is None:
            raise Exception("Tesseract not available")

        from PIL import Image
        image = Image.open(image_path)

        # PSM 3 = Fully automatic page segmentation (default, best for most cases)
        # PSM 6 = Assume a single uniform block of text
        # PSM 11 = Sparse text. Find as much text as possible in no particular order
        custom_config = r'--oem 3 --psm 3'

        # Get text and confidence data
        text = pytesseract.image_to_string(image, config=custom_config)
        data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)

        # Calculate average confidence (filter out -1 values)
        confidences = [float(conf) / 100.0 for conf in data['conf'] if conf != -1]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        lines = [line for line in text.split('\n') if line.strip()]

        return {
            "engine": "Tesseract",
            "text": text.strip(),
            "confidence": round(avg_confidence, 4),
            "lines": len(lines),
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

    results = {
        "image": os.path.basename(image_path),
        "image_path": image_path,
        "engines": {}
    }

    engine_functions = {
        "paddleocr": process_paddleocr,
        "easyocr": process_easyocr,
        "surya": process_surya,
        "tesseract": process_tesseract,
    }

    for engine in engines:
        # Check if engine is available
        available = OCREngineManager.get_available_engines()
        if engine not in engine_functions:
            results["engines"][engine] = {
                "engine": engine,
                "error": "Unknown engine",
                "success": False
            }
            continue

        vprint(f"\n🔍 Processing with {engine}...")
        results["engines"][engine] = engine_functions[engine](processed_path)

        if results["engines"][engine]["success"]:
            vprint(f"✓ {engine}: {results['engines'][engine]['lines']} lines, "
                   f"{results['engines'][engine]['confidence']:.2%} confidence, "
                   f"{results['engines'][engine]['processing_time']}s")
        else:
            vprint(f"❌ {engine}: {results['engines'][engine].get('error', 'Unknown error')}")

    return results


def main():
    global VERBOSE

    parser = argparse.ArgumentParser(
        description=f'Advanced OCR Tool v{__version__} - Performance Optimized',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Single image with PaddleOCR (best for noisy images)
  %(prog)s --engine paddleocr --input photo.jpg

  # Compare all engines
  %(prog)s --engine all --input photo.jpg --output results.json

  # Batch processing
  %(prog)s --engine paddleocr --input-dir ./images/ --output-dir ./results/

  # HEIC image
  %(prog)s --engine paddleocr --input IMG_0371.heic

  # Quiet mode (no progress output)
  %(prog)s --quiet --engine paddleocr --input photo.jpg

Engines:
  paddleocr  - Best for noisy/grainy images (recommended)
  easyocr    - Good with challenging backgrounds
  surya      - Modern, handles noise well
  tesseract  - Fast, good for clean images
  all        - Run all available engines
        '''
    )

    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('--engine',
                        choices=['paddleocr', 'easyocr', 'surya', 'tesseract', 'all'],
                        default='paddleocr',
                        help='OCR engine to use (default: paddleocr)')
    parser.add_argument('--input', help='Input image file')
    parser.add_argument('--input-dir', help='Input directory for batch processing')
    parser.add_argument('--output', help='Output JSON file')
    parser.add_argument('--output-dir', help='Output directory for batch processing')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output (default)')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode (minimal output)')

    args = parser.parse_args()

    # Set verbose mode
    if args.quiet:
        VERBOSE = False
    elif args.verbose:
        VERBOSE = True

    vprint(f"\n{'='*60}")
    vprint(f"🚀 Advanced OCR Tool v{__version__} - Performance Optimized")
    vprint(f"{'='*60}")

    # Determine which engines to use
    if args.engine == 'all':
        # Try to initialize all engines
        OCREngineManager.get_paddleocr()
        OCREngineManager.get_easyocr()
        OCREngineManager.get_surya()
        OCREngineManager.get_tesseract()
        engines = OCREngineManager.get_available_engines()

        if not engines:
            print("❌ No OCR engines available!")
            print("\nInstall at least one engine:")
            print("  Docker: docker build -t python-advanced-ocr .")
            print("  Or pip: pip install paddleocr easyocr surya-ocr pytesseract")
            sys.exit(1)
    else:
        engines = [args.engine]

    if HEIC_SUPPORTED:
        vprint("✓ HEIC support enabled")
    if HAS_TQDM:
        vprint("✓ Progress bars enabled")

    # Batch processing
    if args.input_dir:
        if not args.output_dir:
            args.output_dir = './output'

        if not os.path.isdir(args.input_dir):
            print(f"❌ Input directory not found: {args.input_dir}")
            sys.exit(1)

        # Find all image files
        input_path = Path(args.input_dir)
        output_path = Path(args.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.heic', '.heif'}
        image_files = [f for f in input_path.rglob('*')
                       if f.is_file() and f.suffix.lower() in image_extensions]

        if not image_files:
            print(f"❌ No images found in {args.input_dir}")
            sys.exit(1)

        vprint(f"\n📁 Found {len(image_files)} images in {args.input_dir}")
        vprint(f"🎯 Processing with engines: {', '.join(engines)}\n")

        results = []

        # Use tqdm if available and not in quiet mode
        iterator = tqdm(image_files, desc="Processing images", disable=not VERBOSE) if HAS_TQDM else image_files

        for image_file in iterator:
            if not HAS_TQDM and VERBOSE:
                vprint(f"\n{'='*60}")
                vprint(f"📸 Processing: {image_file.name}")

            result = process_image(str(image_file), engines)
            results.append(result)

            # Save individual result
            result_file = output_path / f"{image_file.stem}_result.json"
            with open(result_file, 'w') as f:
                json.dump(result, f, indent=2)

        # Save combined results
        combined_file = output_path / "batch_results.json"
        with open(combined_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n✅ Batch processing complete!")
        print(f"📊 Results saved to: {combined_file}")

    # Single image processing
    elif args.input:
        if not os.path.exists(args.input):
            print(f"❌ Image not found: {args.input}")
            sys.exit(1)

        result = process_image(args.input, engines)

        # Print results (always show results even in quiet mode)
        print(f"\n{'='*60}")
        print(f"📊 RESULTS")
        print(f"{'='*60}")

        for engine, data in result["engines"].items():
            if data["success"]:
                print(f"\n{engine.upper()}:")
                print(f"  Confidence: {data['confidence']:.2%}")
                print(f"  Lines: {data['lines']}")
                print(f"  Time: {data['processing_time']}s")
                print(f"  Text preview: {data['text'][:100]}...")
            else:
                print(f"\n{engine.upper()}: FAILED - {data.get('error', 'Unknown error')}")

        # Save to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Results saved to: {args.output}")

    else:
        parser.print_help()
        sys.exit(1)

    vprint(f"\n{'='*60}")
    vprint("✅ Done!")
    vprint(f"{'='*60}\n")


if __name__ == "__main__":
    main()
