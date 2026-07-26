from processing.pdf_processor import extract_tables
from processing.excel_processor import read_excel
from processing.ocr_processor import extract_text_from_image


def extract_tables_from_file(file_path, extension):
    """
    NOTE: document_understanding.py no longer calls this for .pdf or
    image uploads -- it calls pdf_processor.extract_tables() and
    gemini_extractor directly instead, so it can route individual hard
    pages to Gemini. This function is kept working (and still used for
    .xlsx/.xls) so nothing breaks if something else calls it directly.
    """

    extension = extension.lower()

    if extension == ".pdf":

        # extract_tables() returns (raw_tables, missing_pages) --
        # missing_pages is unused here since this path doesn't do the
        # Gemini fallback (document_understanding.py does that itself
        # via pdf_processor.extract_tables() directly).
        tables, _missing_pages = extract_tables(file_path)

        return tables, None

    elif extension in [".xlsx", ".xls"]:

        sheets = read_excel(file_path)

        tables = []
        names = []

        for sheet in sheets:
            tables.append(sheet["rows"])
            names.append(sheet["sheet_name"])

        return tables, names

    elif extension in [".png", ".jpg", ".jpeg"]:

        # Superseded: images are routed to Gemini directly by
        # document_understanding.py (extract_image_with_gemini), not
        # used in the main flow. Kept only as a simple leftover
        # fallback -- your current ocr_processor.py only exposes
        # extract_text_from_image (no bounding boxes), so this can't
        # do column alignment, just line-by-line text.
        text = extract_text_from_image(file_path)

        rows = [[line] for line in text.split("\n") if line.strip()]

        if not rows:
            return [], []

        return [rows], ["Image_Text"]

    return [], []
