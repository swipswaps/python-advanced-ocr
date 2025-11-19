#!/bin/bash
# OCR Custom Directory Helper Script
# Process images from any directory on your system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENGINE="paddleocr"
INPUT_DIR=""
OUTPUT_DIR=""

# Function to show usage
show_usage() {
    echo -e "${BLUE}OCR Custom Directory Helper${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -i, --input DIR      Input directory (required)"
    echo "  -o, --output DIR     Output directory (default: INPUT_DIR/ocr-results)"
    echo "  -e, --engine ENGINE  OCR engine: paddleocr, easyocr, surya, tesseract, all (default: paddleocr)"
    echo "  -h, --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  # Process all images in Downloads folder"
    echo "  $0 -i ~/Downloads"
    echo ""
    echo "  # Process with specific output directory"
    echo "  $0 -i ~/Downloads -o ~/Documents/ocr-results"
    echo ""
    echo "  # Use different OCR engine"
    echo "  $0 -i ~/Pictures -e easyocr"
    echo ""
    echo "  # Compare all engines"
    echo "  $0 -i ~/Downloads -e all"
    exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--input)
            INPUT_DIR="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -e|--engine)
            ENGINE="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            ;;
        *)
            echo -e "${RED}Error: Unknown option: $1${NC}"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Validate input directory
if [ -z "$INPUT_DIR" ]; then
    echo -e "${RED}Error: Input directory is required${NC}"
    echo "Use -h or --help for usage information"
    exit 1
fi

# Expand tilde in paths
INPUT_DIR="${INPUT_DIR/#\~/$HOME}"
if [ -n "$OUTPUT_DIR" ]; then
    OUTPUT_DIR="${OUTPUT_DIR/#\~/$HOME}"
fi

# Check if input directory exists
if [ ! -d "$INPUT_DIR" ]; then
    echo -e "${RED}Error: Input directory does not exist: $INPUT_DIR${NC}"
    exit 1
fi

# Set default output directory if not specified
if [ -z "$OUTPUT_DIR" ]; then
    OUTPUT_DIR="$INPUT_DIR/ocr-results"
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Validate engine
case $ENGINE in
    paddleocr|easyocr|surya|tesseract|all)
        ;;
    *)
        echo -e "${RED}Error: Invalid engine: $ENGINE${NC}"
        echo "Valid engines: paddleocr, easyocr, surya, tesseract, all"
        exit 1
        ;;
esac

# Show configuration
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}🚀 OCR Custom Directory Processing${NC}"
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}Input Directory:${NC}  $INPUT_DIR"
echo -e "${GREEN}Output Directory:${NC} $OUTPUT_DIR"
echo -e "${GREEN}OCR Engine:${NC}       $ENGINE"
echo -e "${BLUE}============================================================${NC}"
echo ""

# Count images
IMAGE_COUNT=$(find "$INPUT_DIR" -maxdepth 1 -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.pdf" -o -iname "*.heic" -o -iname "*.heif" \) 2>/dev/null | wc -l)

if [ "$IMAGE_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}Warning: No images found in $INPUT_DIR${NC}"
    echo "Supported formats: JPG, JPEG, PNG, PDF, HEIC, HEIF"
    exit 0
fi

echo -e "${GREEN}Found $IMAGE_COUNT image(s) to process${NC}"
echo ""

# Run Docker with custom volumes
echo -e "${BLUE}Starting OCR processing...${NC}"
echo ""

INPUT_DIR="$INPUT_DIR" OUTPUT_DIR="$OUTPUT_DIR" docker compose run --rm ocr-batch-custom \
    --engine "$ENGINE" \
    --input-dir /input \
    --output-dir /output

echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}✅ Processing complete!${NC}"
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}Results saved to:${NC} $OUTPUT_DIR"
echo ""

