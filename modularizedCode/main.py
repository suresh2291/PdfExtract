from flask import Flask, request, jsonify
import os
import time
from pdf_processing import convert_pdf_to_images, perform_ocr, clean_text

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

    # Get the uploaded PDF file from the request
    file = request.files['file']

    # Create a directory to store extracted pages if it doesn't exist
    extracted_pages_folder = 'extracted_pages'
    os.makedirs(extracted_pages_folder, exist_ok=True)

    # Save the PDF file
    pdf_path = os.path.join(extracted_pages_folder, file.filename)
    file.save(pdf_path)

    # Create a directory to store images
    images_folder = os.path.join(extracted_pages_folder, 'images')
    image_paths = convert_pdf_to_images(pdf_path, images_folder)

    # Initialize dictionary to store extracted text and page-wise execution time
    extracted_text = {}

    # Iterate through each page image and perform OCR
    for page_number, image_path in enumerate(image_paths, start=1):
        try:
            # Perform OCR on the image using Tesseract OCR
            text, page_time = perform_ocr(image_path)
            # Perform text cleaning and formatting
            cleaned_text = clean_text(text)
            # Store the cleaned extracted text with page time
            extracted_text[f'Page {page_number}'] = {
                'text': cleaned_text,
                'time': f"{(page_time):.2f} seconds"
            }
        except FileNotFoundError:
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
    for image_path in image_paths:
        os.remove(image_path)
    os.rmdir(images_folder)

    # Return response as JSON
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
