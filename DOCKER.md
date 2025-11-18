# Docker Setup for Fedora/Linux

Since PaddlePaddle doesn't have pre-built wheels for all Linux distributions,
use Docker for a consistent environment.

## Prerequisites

Install Docker:
```bash
# Fedora
sudo dnf install docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
# Log out and back in for group changes to take effect
```

## Quick Start

### 1. Build the Docker image
```bash
docker build -t python-advanced-ocr .
```

### 2. Create images directory
```bash
mkdir -p images
# Copy your images here
cp /path/to/IMG_0371.heic images/
```

### 3. Run OCR
```bash
# Using PaddleOCR (recommended)
docker run --rm -v $(pwd)/images:/images python-advanced-ocr \
    --engine paddleocr --input /images/IMG_0371.heic

# Using EasyOCR
docker run --rm -v $(pwd)/images:/images python-advanced-ocr \
    --engine easyocr --input /images/IMG_0371.heic

# Try all engines
docker run --rm -v $(pwd)/images:/images python-advanced-ocr \
    --engine all --input /images/IMG_0371.heic

# Save results to JSON
docker run --rm -v $(pwd)/images:/images python-advanced-ocr \
    --engine paddleocr --input /images/IMG_0371.heic --output /images/results.json
```

## Using the Helper Script

```bash
chmod +x run.sh

# Run with default engine (paddleocr)
./run.sh images/IMG_0371.heic

# Specify engine
./run.sh images/IMG_0371.heic easyocr
```

## Using Docker Compose

```bash
# Build
docker-compose build

# Run
docker-compose run --rm ocr --engine paddleocr --input /images/IMG_0371.heic
```

## Troubleshooting

### Permission denied
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

### Image not found
Make sure your image is in the `images/` directory and you're using the path `/images/filename.jpg`

### Out of memory
Docker might need more memory. Increase in Docker settings or use `--memory` flag.
