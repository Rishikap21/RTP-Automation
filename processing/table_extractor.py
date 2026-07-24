from processing.pdf_processor import extract_tables
from processing.excel_processor import read_excel
from processing.ocr_processor import extract_text_from_image


def extract_tables_from_file(file_path, extension):

    extension = extension.lower()

    if extension == ".pdf":

        tables = extract_tables(file_path)

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

        text = extract_text_from_image(file_path)

        rows = []

        for line in text.split("\n"):

            if line.strip():

                rows.append([line])

        return [rows], ["Image_Text"]

    return [], []