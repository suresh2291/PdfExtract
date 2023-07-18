from flask import Flask, request, jsonify
import subprocess
import time
from PIL import Image
import os
app = Flask(__name__)


@app.route('/extract_text', methods=['POST'])
def extract_text():
    """
    Endpoint for extracting text from a PDF file using Tesseract OCR.

    Returns:
        JSON response containing the extracted text and execution time.
    """

    # Measure overall execution time
    start_time = time.time()
    if 'file' not in request.files:
        return 'No file part in the request'
    
    # Get the uploaded PDF file from the request
    file = request.files['file']

    if file.filename == '':
        return 'No file selected'

    if not file.filename.endswith('.pdf'):
        return 'Only PDF files are allowed'
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

    # Iterate through each page image and perform OCR
    page_number = 1
    while True:

        # Define the image file path for the current page
        image_path = os.path.join(images_folder, f'output-{page_number:03d}.png')
        if os.path.exists(image_path):
            try:
                #print(f" image path:  ", image_path)
                # Perform OCR on the image using Tesseract OCR
                start_page_time = time.time()
                output = output = subprocess.check_output(['tesseract', image_path, 'stdout', '-l', 'deu', '--oem', '1', '--psm', '6', '-c', 'preserve_interword_spaces=1'])
                page_time = time.time() - start_page_time
                print(f"page timr: {page_time}")
                text = output.decode('utf-8').strip('\n') #.decode("unicode-escape")
                print(f"type of text:  ",type(text))
                # Perform text cleaning and formatting
                cleaned_text = clean_text(text)
            
                # Store the cleaned extracted text with page time
                extracted_text[f'Page {page_number}'] = {
                    'text': cleaned_text,
                    'time':f"{(page_time):.2f} seconds"
                }

                # Increment the page number
                page_number += 1

            except FileNotFoundError:

                # Break the loop when all pages have been processed
                break
        else:

            # Break the loop when all pages have been processed
            break

    # Calculate total execution time
    total_time = time.time() - start_time

    # Create response JSON with extracted text and execution time
    response = {
        'extracted_text': extracted_text,
        'execution_time': f"{(total_time):.2f} seconds"
    }

    # Delete the PDF file and images
    os.remove(pdf_path)
    for filename in os.listdir(images_folder):
        file_path = os.path.join(images_folder, filename)
        os.remove(file_path)
    os.rmdir(images_folder)

    # Return response as JSON
    return jsonify(response)

def clean_text(text):
    """
    Clean and format the extracted text.

    Args:
        text: Raw extracted text.

    Returns:
        Cleaned and formatted text.
    """
    # Split the input into lines
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
    app.run(debug=True)
