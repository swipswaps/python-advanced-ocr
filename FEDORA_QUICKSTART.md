# Fedora Quick Start Guide

## Problem
PaddlePaddle doesn't have pre-built wheels for Fedora, so `pip install paddlepaddle` fails.

## Solution
Use Docker! It provides a consistent environment with all OCR engines pre-installed.

## Setup (One-time)

### 1. Ensure Docker is running
```bash
sudo systemctl start docker
sudo systemctl enable docker

# Add yourself to docker group (to avoid sudo)
sudo usermod -aG docker $USER
# Log out and back in for this to take effect
```

### 2. Build the Docker image
```bash
cd python-advanced-ocr
docker build -t python-advanced-ocr .
```

This will take 5-10 minutes the first time (downloads and installs all OCR engines).

## Usage

### Method 1: Using the helper script (easiest)

```bash
# Copy your image to the images/ directory
cp /path/to/IMG_0371.heic images/

# Run OCR with PaddleOCR (recommended)
./run.sh images/IMG_0371.heic paddleocr

# Or with EasyOCR
./run.sh images/IMG_0371.heic easyocr

# Or try all engines
./run.sh images/IMG_0371.heic all
```

### Method 2: Direct Docker command

```bash
# Place your image in images/ directory
cp ~/Pictures/IMG_0371.heic images/

# Run with PaddleOCR
docker run --rm \
    -v $(pwd)/images:/images \
    python-advanced-ocr \
    --engine paddleocr \
    --input /images/IMG_0371.heic

# Run with all engines and save results
docker run --rm \
    -v $(pwd)/images:/images \
    python-advanced-ocr \
    --engine all \
    --input /images/IMG_0371.heic \
    --output /images/results.json
```

### Method 3: Using docker-compose

```bash
# Edit docker-compose.yml to set your image path, then:
docker-compose run --rm ocr \
    --engine paddleocr \
    --input /images/IMG_0371.heic
```

## Example Output

```
Advanced OCR Tool
==================================================
✓ PaddleOCR available
✓ EasyOCR available
✓ Surya OCR available
✓ Tesseract available
==================================================

Processing: /images/IMG_0371.heic
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
```

## Tips

1. **Always use `/images/` prefix** for file paths inside Docker
2. **Results are saved to images/ directory** so you can access them on your host
3. **First run is slow** (downloads OCR models), subsequent runs are fast
4. **For best results with noisy images**: Use PaddleOCR

## Troubleshooting

### "permission denied" when running docker
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

### "Cannot connect to Docker daemon"
```bash
sudo systemctl start docker
```

### Image not found
Make sure:
- Your image is in the `images/` directory
- You use `/images/filename.heic` (not `images/filename.heic`)

### Out of memory
```bash
# Give Docker more memory
docker run --memory=4g --rm -v $(pwd)/images:/images python-advanced-ocr ...
```

## Comparison: Windows vs Fedora

| Platform | Installation | Command |
|----------|-------------|---------|
| **Windows** | `pip install paddleocr` | `python ocr_tool.py --input image.jpg` |
| **Fedora** | `docker build -t python-advanced-ocr .` | `./run.sh images/image.jpg` |

Both work the same, Docker just adds one extra step (building the image once).
