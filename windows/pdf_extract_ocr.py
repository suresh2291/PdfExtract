
from flask import Flask, request, jsonify
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image
import concurrent.futures
import time
import re

app = Flask(__name__)

# Set the path to the Tesseract OCR executable
pytesseract.pytesseract.tesseract_cmd = r'c:\Program Files\Tesseract-OCR\tesseract.exe'


@app.route('/extract_text', methods=['POST'])
def ocr():
    """
    Endpoint for extracting text from a PDF file using Tesseract OCR.

    Returns:
        JSON response containing OCR results and execution time.
    """
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

    # Read the PDF file as bytes
    file_bytes = file.read()

    # Convert PDF pages to images
    pages = convert_from_bytes(file_bytes, dpi=100)
    print(f"Pages:  %s" % pages)
    ocr_results = []
    total_time = 0

    # Use ThreadPoolExecutor for concurrent OCR processing
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        # Process each page with Tesseract OCR asynchronously
        for i, page in enumerate(pages):
            future = executor.submit(process_ocr, page)
            futures.append((i + 1, future))

        # Collect OCR results and calculate total time
        for i, future in futures:
            tesseract_text, tesseract_time = future.result()
            #cleaned_text = clean_text(tesseract_text)
            ocr_results.append({
                'page': i,
                'tesseract_text':  tesseract_text.replace("\\n", "\n"),#tesseract_text.translate(str.maketrans("\\n", "\n")),
                'tesseract_time': tesseract_time,
            })

            total_time += tesseract_time

    # Prepare the response JSON
    response = {
        'total_time': total_time * 1000,  # Convert to milliseconds
        'avg_per_page_time': (total_time / len(pages)) * 1000,  # Convert to milliseconds
        'ocr_results': ocr_results
    }

    # Print Sequential Pipeline Timings
    print("Sequential Pipeline Timings:")
    print(f"Total time: {total_time * 1000} milliseconds")
    print(f"Average time per page: {(total_time / len(pages)) * 1000} milliseconds")

    return jsonify(response)


def process_ocr(page):
    """
    Process OCR on a single image page using Tesseract.

    Args:
        page (PIL.Image): The image page to process.

    Returns:
        tuple: A tuple containing the extracted text and OCR processing time.
    """
    start_time = time.time()
    print(f"start time: {start_time}")

    # Convert the image to grayscale
    image_data = page.convert('L')

    # Perform OCR on the image using Tesseract
    tesseract_text = pytesseract.image_to_string(image_data)
    print(f"Process Text from image:   ", tesseract_text)
    end_time = time.time()
    print(f"end time: ", end_time)

    # Calculate OCR processing time(continued):
    ocr_time = end_time - start_time

    return tesseract_text, ocr_time

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
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
