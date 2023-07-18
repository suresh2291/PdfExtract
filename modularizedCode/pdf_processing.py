import subprocess
import os
import time


def convert_pdf_to_images(pdf_path, images_folder):
    """
    Convert a PDF to images using Ghostscript.

    Args:
        pdf_path: Path to the PDF file.
        images_folder: Path to the folder to store the images.

    Returns:
        List of image paths.
    """
    os.makedirs(images_folder, exist_ok=True)
    subprocess.call(['gs', '-dSAFER', '-dBATCH', '-dNOPAUSE', '-sDEVICE=png16m', '-r300', '-sOutputFile=' + images_folder + '/output-%03d.png', pdf_path])
    image_paths = sorted([os.path.join(images_folder, filename) for filename in os.listdir(images_folder)])
    return image_paths


def perform_ocr(image_path):
    """
    Perform OCR on an image using Tesseract OCR.

    Args:
        image_path: Path to the image file.

    Returns:
        Extracted text and page execution time.
    """
    start_time = time.time()
    output = subprocess.check_output(['tesseract', image_path, 'stdout', '-l', 'deu', '--oem', '1', '--psm', '6', '-c', 'preserve_interword_spaces=1'])
    page_time = time.time() - start_time
    text = output.decode('utf-8').strip()
    return text, page_time


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
