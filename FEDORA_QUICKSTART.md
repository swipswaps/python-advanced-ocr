# Fedora 42/43 Quick Start Guide

## Problem
PaddlePaddle doesn't have pre-built wheels for Fedora, so `pip install paddlepaddle` fails with:
```
ERROR: No matching distribution found for paddlepaddle
```

## Solution
Use Docker! It provides a consistent environment with all OCR engines pre-installed.

---

## 🚀 Quick Setup (One-time)

### 1. Ensure Docker is running
```bash
# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add yourself to docker group (to avoid sudo)
sudo usermod -aG docker $USER

# IMPORTANT: Log out and back in for group changes to take effect
# Or run: newgrp docker
```

### 2. Clone the repository (if not already done)
```bash
cd ~/Documents/sunelec
git clone https://github.com/swipswaps/python-advanced-ocr.git
cd python-advanced-ocr
```

### 3. Build the Docker image
```bash
docker build -t python-advanced-ocr .
```

**This will take 5-10 minutes the first time** (downloads and installs all OCR engines).

---

## 📖 Usage - Three Methods

### ⭐ Method 1: Helper Scripts (EASIEST - Recommended for Fedora)

The helper scripts automatically handle Docker for you:

```bash
# 1. Copy your image to images/ directory
cp /path/to/photo.jpg images/
# Or for HEIC files:
cp ~/Pictures/IMG_0371.heic images/

# 2. Run OCR with PaddleOCR (best for noisy images)
./run.sh images/photo.jpg paddleocr

# 3. Or try all engines and compare
./run.sh images/photo.jpg all

# 4. Save results to JSON file
./run.sh images/photo.jpg paddleocr images/results.json

# 5. Batch process all images in images/ directory
./batch_ocr.sh paddleocr
```

**The helper scripts will:**
- ✅ Automatically build Docker image if needed
- ✅ Handle file paths correctly
- ✅ Show you the results immediately
- ✅ Work exactly like the Windows version

---

### Method 2: Direct Docker Commands

For more control, use Docker directly:

```bash
# Single image with PaddleOCR
docker run --rm \
    -v $(pwd)/images:/images \
    python-advanced-ocr \
    --engine paddleocr \
    --input /images/photo.jpg

# All engines with JSON output
docker run --rm \
    -v $(pwd)/images:/images \
    python-advanced-ocr \
    --engine all \
    --input /images/photo.jpg \
    --output /images/results.json

# Batch processing
docker run --rm \
    -v $(pwd)/images:/images \
    -v $(pwd)/output:/output \
    python-advanced-ocr \
    --engine paddleocr \
    --input-dir /images \
    --output-dir /output

# Quiet mode (minimal output)
docker run --rm \
    -v $(pwd)/images:/images \
    python-advanced-ocr \
    --quiet \
    --engine paddleocr \
    --input /images/photo.jpg
```

---

### Method 3: Docker Compose

**Note**: Fedora uses Docker Compose v2, so the command is `docker compose` (with space), not `docker-compose` (with hyphen).

```bash
# First, edit docker-compose.yml to set your image filename
# Change line 17: command: --engine paddleocr --input /images/YOUR_IMAGE.jpg

# Then run:
docker compose run --rm ocr-single

# Or for batch processing:
docker compose run --rm ocr-batch

# Or just use the helper scripts instead (easier):
./run.sh images/photo.jpg paddleocr
```

---

## 📊 Example Output

When you run `./run.sh images/photo.jpg paddleocr`, you'll see:

```
============================================================
🚀 Advanced OCR Tool v2.1.0 - Performance Optimized
============================================================
✓ HEIC support enabled
✓ Progress bars enabled
🔧 Initializing PaddleOCR (one-time setup, GPU: False)...
✓ PaddleOCR ready

🔍 Processing with paddleocr...
✓ paddleocr: 15 lines, 92.34% confidence, 2.3s

============================================================
📊 RESULTS
============================================================

PADDLEOCR:
  Confidence: 92.34%
  Lines: 15
  Time: 2.3s
  Text preview: Canadian Solar 370-395W Solar Panels (90,284 Units)...

============================================================
✅ Done!
============================================================
```

---

## 💡 Tips for Fedora Users

1. **Use helper scripts** - `./run.sh` and `./batch_ocr.sh` are the easiest way
2. **First run is slow** - Downloads OCR models (1-2 minutes), subsequent runs are fast
3. **For noisy images** - Use PaddleOCR (best accuracy on grainy/noisy images)
4. **HEIC files work** - Automatically converted to JPEG
5. **Results location** - Saved to `images/` or `output/` directory on your host
6. **GPU support** - If you have NVIDIA GPU with CUDA, it will auto-detect and use it (3x faster)

---

## 🔧 Troubleshooting

### ❌ "docker-compose: command not found"

**Problem**: Fedora 42/43 uses Docker Compose v2 (plugin version).

**Solution**: Use `docker compose` (with space) instead of `docker-compose` (with hyphen):
```bash
# ❌ Old way (doesn't work on Fedora 42/43)
docker-compose run ocr-single

# ✅ New way (works on Fedora 42/43)
docker compose run ocr-single

# ✅ Or just use helper scripts (easiest)
./run.sh images/photo.jpg paddleocr
```

### ❌ "permission denied" when running docker

**Problem**: Your user is not in the docker group.

**Solution**:
```bash
sudo usermod -aG docker $USER
# Log out and back in, or run:
newgrp docker
```

### ❌ "Cannot connect to Docker daemon"

**Problem**: Docker service is not running.

**Solution**:
```bash
sudo systemctl start docker
sudo systemctl enable docker  # Start on boot
```

### ❌ "Image not found" or "No such file"

**Problem**: File path is incorrect.

**Solution**:
- Make sure your image is in the `images/` directory
- When using helper scripts: `./run.sh images/photo.jpg`
- When using Docker directly: Use `/images/photo.jpg` (with leading slash)

### ❌ Out of memory errors

**Problem**: Large images or multiple engines use too much RAM.

**Solution**:
```bash
# Give Docker more memory (4GB)
docker run --memory=4g --rm \
    -v $(pwd)/images:/images \
    python-advanced-ocr \
    --engine paddleocr \
    --input /images/photo.jpg

# Or process one engine at a time
./run.sh images/photo.jpg paddleocr
```

### ❌ "bash: ./run.sh: Permission denied"

**Problem**: Script is not executable.

**Solution**:
```bash
chmod +x run.sh batch_ocr.sh
./run.sh images/photo.jpg paddleocr
```

---

## 📊 Comparison: Windows vs Fedora

| Aspect | Windows | Fedora 42/43 |
|--------|---------|--------------|
| **Installation** | `pip install paddleocr` | `docker build -t python-advanced-ocr .` |
| **Command** | `python ocr_tool.py --input image.jpg` | `./run.sh images/image.jpg paddleocr` |
| **Setup Time** | 2 minutes | 10 minutes (first time only) |
| **Performance** | Same | Same |
| **Ease of Use** | Direct Python | Docker wrapper |
| **Updates** | `pip install --upgrade` | `git pull && docker build` |

**Both work identically** - Docker just adds one extra setup step (building the image once).

---

## 🎯 Complete Example Workflow

Here's a complete example from start to finish:

```bash
# 1. One-time setup (if not done already)
cd ~/Documents/sunelec/python-advanced-ocr
docker build -t python-advanced-ocr .

# 2. Copy your image
cp ~/Pictures/solar_panel.jpg images/

# 3. Run OCR
./run.sh images/solar_panel.jpg paddleocr

# 4. Check results (displayed on screen)

# 5. Save to JSON for later
./run.sh images/solar_panel.jpg paddleocr images/results.json

# 6. View JSON results
cat images/results.json | python3 -m json.tool

# 7. Process multiple images
cp ~/Pictures/*.jpg images/
./batch_ocr.sh paddleocr

# 8. Check batch results
cat output/batch_results.json | python3 -m json.tool
```

---

## 🚀 Advanced Usage

### Check version
```bash
docker run --rm python-advanced-ocr --version
```

### Quiet mode (for scripts)
```bash
docker run --rm \
    -v $(pwd)/images:/images \
    python-advanced-ocr \
    --quiet \
    --engine paddleocr \
    --input /images/photo.jpg \
    --output /images/results.json
```

### Compare all engines
```bash
./run.sh images/photo.jpg all images/comparison.json
cat images/comparison.json | python3 -m json.tool
```

### Use specific engine for specific image types
```bash
# Noisy/grainy images (solar panels, labels)
./run.sh images/noisy.jpg paddleocr

# Clean documents
./run.sh images/document.jpg tesseract

# Complex backgrounds
./run.sh images/complex.jpg easyocr

# Modern/mixed content
./run.sh images/mixed.jpg surya
```

---

## 📚 Additional Resources

- **Main README**: See `README.md` for full documentation
- **Docker Guide**: See `DOCKER.md` for Docker-specific details
- **Changelog**: See `CHANGELOG.md` for version history
- **GitHub**: https://github.com/swipswaps/python-advanced-ocr

---

## ✅ Summary for Fedora Users

**TL;DR - Just use the helper scripts:**

```bash
# One-time setup
docker build -t python-advanced-ocr .

# Every time you want to OCR an image
./run.sh images/your-image.jpg paddleocr
```

That's it! The helper scripts handle all the Docker complexity for you.
