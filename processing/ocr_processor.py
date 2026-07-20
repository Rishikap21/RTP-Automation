import easyocr

# Initialize OCR reader only once
reader = easyocr.Reader(['en'])

def extract_text_from_image(image_path):
    results = reader.readtext(image_path)

    extracted_text = ""

    for result in results:
        extracted_text += result[1] + "\n"

    return extracted_text