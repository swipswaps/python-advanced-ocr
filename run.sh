#!/bin/bash
# Helper script to run OCR with Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Show usage
if [ -z "$1" ]; then
    echo "Usage: ./run.sh <image-file> [engine] [output-file]"
    echo ""
    echo "Arguments:"
    echo "  image-file    Path to image (must be in images/ directory)"
    echo "  engine        OCR engine: paddleocr, easyocr, surya, tesseract, all (default: paddleocr)"
    echo "  output-file   Optional: Save results to JSON file"
    echo ""
    echo "Examples:"
    echo "  ./run.sh images/photo.jpg"
    echo "  ./run.sh images/photo.jpg paddleocr"
    echo "  ./run.sh images/photo.jpg all images/results.json"
    exit 1
fi

IMAGE_FILE="$1"
ENGINE="${2:-paddleocr}"
OUTPUT_FILE="$3"

# Validate image file exists
if [ ! -f "$IMAGE_FILE" ]; then
    echo -e "${RED}Error: Image file not found: $IMAGE_FILE${NC}"
    exit 1
fi

# Check if file is in images/ directory
if [[ ! "$IMAGE_FILE" =~ ^images/ ]]; then
    echo -e "${YELLOW}Warning: Image should be in images/ directory${NC}"
    echo -e "${YELLOW}Copying to images/ directory...${NC}"
    mkdir -p images
    cp "$IMAGE_FILE" images/
    IMAGE_FILE="images/$(basename "$IMAGE_FILE")"
fi

# Build if needed
if ! docker images | grep -q python-advanced-ocr; then
    echo -e "${YELLOW}Docker image not found. Building...${NC}"
    docker build -t python-advanced-ocr .
fi

# Prepare docker command
DOCKER_CMD="docker run --rm -v $(pwd)/images:/images python-advanced-ocr --engine $ENGINE --input /images/$(basename "$IMAGE_FILE")"

# Add output file if specified
if [ -n "$OUTPUT_FILE" ]; then
    DOCKER_CMD="$DOCKER_CMD --output /images/$(basename "$OUTPUT_FILE")"
fi

# Run OCR
echo -e "${GREEN}Running OCR with $ENGINE...${NC}"
echo ""
eval $DOCKER_CMD
