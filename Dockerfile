FROM python:3.10-slim

RUN apt-get update && apt-get install -y libgomp1 libglib2.0-0 libsm6 libxext6 libxrender-dev libgl1-mesa-glx tesseract-ocr wget && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir paddlepaddle==2.6.0 paddleocr==2.7.3 easyocr==1.7.1 opencv-python-headless==4.8.1.78 Pillow==10.1.0 numpy==1.24.3 pytesseract==0.3.10 pillow-heif==0.13.1

COPY ocr_tool.py .
RUN mkdir -p /images

ENTRYPOINT ["python3", "ocr_tool.py"]
CMD ["--help"]
