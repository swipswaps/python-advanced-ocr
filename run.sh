#!/bin/bash
# Helper script to run OCR with Docker

if [ -z "$1" ]; then
    echo "Usage: ./run.sh <image-file> [engine]"
    echo "Example: ./run.sh images/photo.jpg paddleocr"
    exit 1
fi

IMAGE_FILE="$1"
ENGINE="${2:-paddleocr}"

# Build if needed
if ! docker images | grep -q python-advanced-ocr; then
    echo "Building Docker image..."
    docker build -t python-advanced-ocr .
fi

# Run OCR
docker run --rm \
    -v "$(pwd)/images:/images" \
    python-advanced-ocr \
    --engine "$ENGINE" \
    --input "/images/$(basename "$IMAGE_FILE")"
