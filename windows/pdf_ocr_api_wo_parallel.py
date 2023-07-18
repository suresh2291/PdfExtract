from flask import Flask, request, jsonify
from PyPDF2 import PdfFileReader
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
from google.cloud import vision
import concurrent.futures
import time
import os


# Set the path to the Tesseract OCR executable
pytesseract.pytesseract.tesseract_cmd = r'c:\Program Files\Tesseract-OCR\tesseract.exe'
app = Flask(__name__)


@app.route('/', methods=['GET'])
def welcome():
    print('Welcome')
    return jsonify({"title":"Welcome to Python API Backend Development"})

@app.route('/extract_text', methods=['POST'])
def ocr():
     # Check if 'file' is present in the request
    if 'file' not in request.files:
        return 'No file part in the request'
     # Get the uploaded PDF file from the request
    file = request.files['file']
    
    if file.filename == '':
        return 'No file selected'
     # Check if the file is a PDF
    if not file.filename.endswith('.pdf'):
        return 'Only PDF files are allowed'

    upload_folder = os.path.join(app.root_path, 'pdfs')
    
    file_path = os.path.join(upload_folder, file.filename)
    # Create the "pdfs" directory if it does not exist
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    selected_file = file.save(file_path)
   
    pages = convert_from_path(file_path)

    ocr_results = []
    total_time = 0

    for i, page in enumerate(pages):
        image_path = f'page_{i}.png'
        page.save(image_path, 'PNG')

        # Perform OCR with Tesseract
        start_time = time.time()
        tesseract_text = pytesseract.image_to_string(Image.open(image_path))
        cleaned_text = clean_text(tesseract_text)
        end_time = time.time()
        tesseract_time = end_time - start_time

        ocr_results.append({
            'page': i+1,
            'tesseract_text': cleaned_text,
            'tesseract_time': tesseract_time,
        })

        #total_time += (tesseract_time + google_vision_time)
        total_time += (tesseract_time)
        

    response = {
        'total_time': total_time,
        'per_page_time': total_time / len(pages),
        'ocr_results': ocr_results
    }

    return jsonify(response)
def clean_text(text):
    """
    Clean and format the extracted text.

    Args:
        text: Raw extracted text.

    Returns:
        Cleaned and formatted text.
    """
    
    lines = text.split('\n')

    #  Trim leading and trailing whitespaces from each line
    lines = [line.strip(' ') for line in lines]

    # Remove any empty lines
    lines = [line for line in lines if line]

    # Find the maximum line length
    #max_length = max(len(line) for line in lines)

    # Create the formatted output
    output = ' '.join(line for line in lines)
    return output.replace('neeeennnen', ' ')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    