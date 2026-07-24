import easyocr
import cv2

# Initialize the OCR reader only once
reader = easyocr.Reader(['en'], gpu=False)


def extract_text_from_image(file_path):
    """
    Extract text from an image using EasyOCR.

    Parameters
    ----------
    file_path : str

    Returns
    -------
    str
    """

    try:

        image = cv2.imread(file_path)

        if image is None:
            return ""

        results = reader.readtext(image)

        text = []

        for result in results:
            text.append(result[1])

        return "\n".join(text)

    except Exception as e:

        print("OCR Error:", e)

        return ""


def process_image(file_path):
    """
    Process an image and return extracted text.

    Returns
    -------
    dict
    """

    text = extract_text_from_image(file_path)

    return {
        "text": text,
        "tables": []
    }