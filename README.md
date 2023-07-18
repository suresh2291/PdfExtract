# PdfExtract

PDF-Extraction-Tool
This repository contains a Python-based PDF extraction tool that allows users to extract text from PDF files in both Windows and Ubuntu environments. The tool utilizes Tesseract-OCR for optical character recognition and Ghostscript for PDF processing.
# Installation

Installation Guide:

Install Python (if not already installed) - Download Python
Install pip - Pip Installation Guide
Install Tesseract-OCR with language data - Tesseract Installation


For Windows, 
download the installer from the Tesseract website.
Install Ghostscript - Ghostscript Installation

For Ubuntu:
Copy code
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install ghostscript


3 for testing the codes individually go the respective folder ubuntu or windows and try out the python files
  Example:
  /ubuntu$ python3 ocr_text_extract.py 
  /ubuntu$ocr_text_extract_parallel.py
  /ubuntu$ocr_text_extract_async.py

4. Docker build also works, written the docker file and build the app but facing minor issue, when test API from postman its not accessing..
     docker build -t my_ocr_image .
     docker run -it my_ocr_image
     docker run -it -p 5000:5000 my_ocr_image


Response time:
    based on system information:
    Linux-Ubuntu 
       Intel(R) Core(TM) i5-10210U CPU @ 1.60GH, 15GiB RAM 
       NVIDIA GeForce MX230
       16 GB RAM DDR4

 API response time
      - with out parallel 
       approx 20 secs
      
     - with parallel
       lessthan 22 secs 
    
Windows Desktop
      Processor	Intel(R) Core(TM) i5-10400F CPU @ 2.90GHz, 2904 Mhz, 6 Core(s), 12 Logical Processor(s)
      Name	NVIDIA GeForce GTX 1050 Ti
      16 GB RAM DDR 4