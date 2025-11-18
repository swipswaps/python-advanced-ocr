#!/bin/bash
# Batch OCR processing script

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ -z "$1" ]; then
    echo "Usage: ./batch_ocr.sh [engine]"
    echo ""
    echo "Processes all images in the images/ directory"
    echo "Engine: paddleocr, easyocr, surya, tesseract, all (default: paddleocr)"
    echo ""
    echo "Example: ./batch_ocr.sh paddleocr"
    exit 1
fi

ENGINE="${1:-paddleocr}"

# Build if needed
if ! docker images | grep -q python-advanced-ocr; then
    echo -e "${YELLOW}Building Docker image...${NC}"
    docker build -t python-advanced-ocr .
fi

# Run batch processing
echo -e "${GREEN}Running batch OCR with $ENGINE...${NC}"
echo ""

docker run --rm \
    -v $(pwd)/images:/images \
    -v $(pwd)/output:/output \
    python-advanced-ocr \
    --engine "$ENGINE" \
    --input-dir /images \
    --output-dir /output

echo ""
echo -e "${GREEN}✓ Batch processing complete!${NC}"
echo -e "Results saved to: output/batch_results.json"
