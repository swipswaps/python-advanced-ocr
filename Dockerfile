FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    tesseract-ocr \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python packages with specific versions
RUN pip install --no-cache-dir \
    paddlepaddle==2.6.0 \
    paddleocr==2.7.3 \
    easyocr==1.7.1 \
    surya-ocr==0.4.14 \
    opencv-python-headless==4.8.1.78 \
    Pillow==10.1.0 \
    numpy==1.24.3 \
    pytesseract==0.3.10 \
    pillow-heif==0.13.1 \
    tqdm==4.66.1 \
    torch==2.1.0

# Copy application
COPY ocr_tool.py .

# Create directories
RUN mkdir -p /images /output

# Set environment variables
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python3", "ocr_tool.py"]
CMD ["--help"]
