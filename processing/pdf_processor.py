

import pdfplumber
import camelot
import tabula


def extract_text(pdf_path):
    text = ""

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

    except Exception:
        return None

    return text


def extract_tables(pdf_path):
    extracted_tables = []

    # Try extracting tables using Camelot
    try:
        tables = camelot.read_pdf(pdf_path, pages="all")

        if len(tables) > 0:
            for table in tables:
                extracted_tables.append(table.df.values.tolist())

    except Exception:
        pass

    # If Camelot didn't find any tables, use Tabula
    if len(extracted_tables) == 0:
        try:
            tables = tabula.read_pdf(pdf_path, pages="all", multiple_tables=True)

            for table in tables:
                extracted_tables.append(table.values.tolist())

        except Exception:
            pass

    return extracted_tables