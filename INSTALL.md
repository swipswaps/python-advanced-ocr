# Installation Guide

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/python-advanced-ocr.git
cd python-advanced-ocr
```

### 2. Create virtual environment (recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

#### Option A: Install all engines (recommended)
```bash
pip install -r requirements.txt
```

#### Option B: Install specific engines only

**PaddleOCR only** (best for noisy images):
```bash
pip install paddleocr paddlepaddle opencv-python Pillow numpy
```

**EasyOCR only**:
```bash
pip install easyocr opencv-python Pillow numpy
```

**Tesseract only** (fastest, but less accurate):
```bash
# Install Tesseract binary first
# Ubuntu/Debian: sudo apt-get install tesseract-ocr
# macOS: brew install tesseract
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki

pip install pytesseract Pillow
```

### 4. Test installation
```bash
python3 ocr_tool.py --help
```

## Platform-Specific Instructions

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-venv tesseract-ocr
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### macOS
```bash
brew install python tesseract
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows
1. Install Python 3.8+ from python.org
2. Install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki
3. Open Command Prompt:
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## GPU Support (Optional, for faster processing)

### CUDA (NVIDIA GPUs)
```bash
# Install CUDA toolkit first (https://developer.nvidia.com/cuda-downloads)
pip install paddlepaddle-gpu
```

## Troubleshooting

### "No module named 'paddleocr'"
```bash
pip install paddleocr paddlepaddle
```

### "Tesseract not found"
Make sure Tesseract binary is installed and in your PATH.

### Memory errors
Reduce batch size or process images one at a time.

### Import errors
Make sure you're in the virtual environment:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
