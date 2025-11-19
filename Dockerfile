FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    tesseract-ocr \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python packages from requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application
COPY ocr_tool.py .

# Create directories
RUN mkdir -p /images /output

# Set environment variables
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python3", "ocr_tool.py"]
CMD ["--help"]
