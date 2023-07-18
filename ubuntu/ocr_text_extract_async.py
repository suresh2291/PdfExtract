
from flask import Flask, request, jsonify
import asyncio
import subprocess
import time
import os

app = Flask(__name__)

@app.route('/extract_text', methods=['POST'])
async def extract_text():
    """
    Endpoint for extracting text from a PDF file using Tesseract OCR and asyncio for parallel processing.

    Returns:
        JSON response containing the extracted text and execution time.
    """
     
    # Measure overall execution time
    start_time = time.time()

    # Get the uploaded PDF file from the request
    file = request.files['file']

    # Create a directory to store extracted pages if it doesn't exist
    if not os.path.exists('extracted_pages'):
        os.makedirs('extracted_pages')

    # Save the PDF file
    pdf_path = os.path.join('extracted_pages', file.filename)
    file.save(pdf_path)

    # Create a directory to store images
    images_folder = os.path.join('extracted_pages', 'images')
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)

    # Convert the PDF to images using Ghostscript
    subprocess.call(['gs', '-dSAFER', '-dBATCH', '-dNOPAUSE', '-sDEVICE=png16m', '-r300', '-sOutputFile=' + images_folder + '/output-%03d.png', pdf_path])

    # Initialize dictionary to store extracted text and page-wise execution time
    extracted_text = {}
    loop = asyncio.get_event_loop()  # Get the current event loop
    tasks = []

    # Iterate through each page image and create a task for OCR processing
    for page_number, image_path in enumerate(get_image_paths(images_folder), start=1):
        task = loop.create_task(process_page(image_path))
        tasks.append((page_number, task))

    # Wait for all tasks to complete
    results = await asyncio.gather(*[task for _, task in tasks])

    # Process the OCR results
    for (page_number, _), result in zip(tasks, results):
        if result:
            text, page_time = result
            extracted_text[f'Page {page_number}'] = {
                'text': text,
                'time': page_time
            }

    # Calculate total execution time
    total_time = time.time() - start_time
    
    # Create response JSON with extracted text and execution time
    response = {
        'extracted_text': extracted_text,
        'execution_time': total_time
    }

    # Delete the PDF file and images
    os.remove(pdf_path)
    for filename in os.listdir(images_folder):
        file_path = os.path.join(images_folder, filename)
        os.remove(file_path)
    os.rmdir(images_folder)

    # Return response as JSON
    return jsonify(response)

def get_image_paths(images_folder):
    """
    Get the list of image paths sorted by page number.

    Args:
        images_folder: Folder containing the page images.

    Returns:
        List of image paths.
    """
    # Get the list of image paths sorted by page number
    image_paths = sorted([os.path.join(images_folder, filename) for filename in os.listdir(images_folder)])
    return image_paths

async def process_page(image_path):
    """
    Process a single page image using Tesseract OCR.

    Args:
        image_path: Path to the page image.

    Returns:
        Tuple containing the extracted text and page execution time.
    """
    try:
        # Perform OCR on the image using Tesseract OCR
        start_page_time = time.time()
        output = subprocess.check_output(['tesseract', image_path, 'stdout', '-l', 'deu', '--oem', '1', '--psm', '6', '-c', 'preserve_interword_spaces=1'])
        page_time = time.time() - start_page_time
        text = output.decode('utf-8').strip()

        # Perform text cleaning and formatting
        cleaned_text = clean_text(text)
        return cleaned_text, page_time
    except FileNotFoundError:
        return None

def clean_text(text):
    """
    Clean and format the extracted text.

    Args:
        text: Raw extracted text.

    Returns:
        Cleaned and formatted text.
    """
    # Remove consecutive newline characters and leading/trailing whitespace
    cleaned_text = ' '.join(text.splitlines()).strip()
    
    # Remove excessive whitespace between words
    cleaned_text = ' '.join(cleaned_text.split())
    return cleaned_text

if __name__ == '__main__':
    app.run(debug=True)
