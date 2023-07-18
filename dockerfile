FROM python:3.9

WORKDIR /app

# Copy the Ubuntu files
COPY modularizedCode/pdf_processing.py ubuntu/main.py 

# Copy the Ubuntu files
COPY ubuntu/ocr_text_extract_async.py ubuntu/ocr_text_extract_parallel.py ubuntu/ocr_text_extract.py /app/

# Copy the Windows files
COPY windows/pdf_ocr_map.py windows/pdf_ocr_optimise.py /app/

# Install dependencies
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Set the command to run your code
CMD ["python", "ocr_text_extract_async.py"]
