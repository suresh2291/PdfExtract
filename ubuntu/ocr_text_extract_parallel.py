from flask import Flask, request, jsonify
import subprocess
import pytesseract
import time
import os
from joblib import Parallel, delayed

app = Flask(__name__)

@app.route('/extract_text', methods=['POST'])
def extract_text():
    """
    Endpoint for extracting text from a PDF file using Tesseract OCR and joblib for parallel processing.

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

    # Get the list of image paths
    image_paths = get_image_paths(images_folder)

    # Initialize dictionary to store extracted text and page-wise execution time
    extracted_text = {}
    page_times = {}

    # Process pages using parallel processing
    results = Parallel(n_jobs=3)(delayed(process_page)(page_number, image_path) for page_number, image_path in enumerate(image_paths, start=1))
    for result in results:
        page_number = result['page']
        extracted_text[page_number] = result['text']
        page_times[page_number] = result['time']

    # Calculate total execution time
    total_time = time.time() - start_time

     # Benchmark per page time
    page_times_list = [result['time'] for result in results]
    page_times = {
        f'Page {page_number}': time for page_number, time in enumerate(page_times_list, start=1)
    }

     # Print out the time taken by the parallel / multi-threaded pipeline
    parallel_time = total_time
    print(f"Time taken by the parallel/multi-threaded pipeline: {parallel_time} seconds")


    # Create response JSON with extracted text, page times, and execution time
    response = {
        'extracted_text': extracted_text,
        'page_times': page_times,
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

def process_page(page_number, image_path):
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

        # Return the page result as a dictionary
        return {
            'page': f'Page {page_number}',
            'text': cleaned_text,
            'time': page_time
        }
    except FileNotFoundError:

        # Return an empty result if the page image is not found
        return {
            'page': f'Page {page_number}',
            'text': '',
            'time': 0.0
        }

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
