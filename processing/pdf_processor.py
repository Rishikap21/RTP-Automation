import pdfplumber
import camelot
import pandas as pd


def extract_text(file_path):

    text = ""

    with pdfplumber.open(file_path) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


def _get_page_count(file_path):

    with pdfplumber.open(file_path) as pdf:
        return len(pdf.pages)


def extract_tables(file_path):
    """
    Extracts tables from a PDF using a PER-PAGE fallback chain:
    Camelot lattice -> Camelot stream -> pdfplumber.

    Returns
    -------
    (raw_tables, missing_pages)
        raw_tables: list of tables successfully extracted locally.
        missing_pages: page numbers (1-indexed) where NONE of the three
        local methods found anything -- these are the pages document_
        understanding.py should route to Gemini, since they're likely
        scanned, blurry, or otherwise not text-extractable.
    """

    raw_tables = []
    pages_with_tables = set()

    total_pages = _get_page_count(file_path)

    # -------------------------------
    # 1. Camelot Lattice (all pages)
    # -------------------------------
    try:

        tables = camelot.read_pdf(
            file_path,
            pages="all",
            flavor="lattice"
        )

        for table in tables:

            df = table.df

            if not df.empty:

                raw_tables.append(df.values.tolist())
                pages_with_tables.add(int(table.page))

    except Exception as e:

        print("Lattice Error:", e)

    missing_pages = [
        p for p in range(1, total_pages + 1)
        if p not in pages_with_tables
    ]

    # -------------------------------
    # 2. Camelot Stream (only pages lattice missed)
    # -------------------------------
    if missing_pages:

        try:

            pages_str = ",".join(str(p) for p in missing_pages)

            tables = camelot.read_pdf(
                file_path,
                pages=pages_str,
                flavor="stream"
            )

            for table in tables:

                df = table.df

                if not df.empty:

                    raw_tables.append(df.values.tolist())
                    pages_with_tables.add(int(table.page))

        except Exception as e:

            print("Stream Error:", e)

    missing_pages = [
        p for p in range(1, total_pages + 1)
        if p not in pages_with_tables
    ]

    # -------------------------------
    # 3. pdfplumber (only pages still missing)
    # -------------------------------
    if missing_pages:

        try:

            with pdfplumber.open(file_path) as pdf:

                for p in missing_pages:

                    page = pdf.pages[p - 1]

                    tables = page.extract_tables()

                    for table in tables:

                        if table:

                            raw_tables.append(table)
                            pages_with_tables.add(p)

        except Exception as e:

            print("pdfplumber Error:", e)

    missing_pages = [
        p for p in range(1, total_pages + 1)
        if p not in pages_with_tables
    ]

    return raw_tables, missing_pages


def process_pdf(file_path):

    tables, missing_pages = extract_tables(file_path)

    return {
        "text": extract_text(file_path),
        "tables": tables,
        "missing_pages": missing_pages
    }
