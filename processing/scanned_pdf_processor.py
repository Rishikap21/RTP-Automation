from pdf2image import convert_from_path
import os
from processing.ocr_processor import extract_text_from_image

POPPLER_PATH = os.path.join(
    os.getcwd(),
    "poppler-26.02.0",
    "Library",
    "bin"
)

def process_scanned_pdf(pdf_path, output_folder="uploads/scanned_pages"):
    os.makedirs(output_folder, exist_ok=True)

    images = convert_from_path(
        pdf_path,
        poppler_path=POPPLER_PATH
    )

    extracted_text = ""

    for i, image in enumerate(images):
        image_path = os.path.join(output_folder, f"page_{i+1}.png")
        image.save(image_path, "PNG")

        text = extract_text_from_image(image_path)
        extracted_text += f"\n----- Page {i+1} -----\n"
        extracted_text += text

    return extracted_text