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


def extract_tables(file_path):

    raw_tables = []

    # -------------------------------
    # 1. Camelot Lattice
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

    except Exception as e:

        print("Lattice Error:", e)

    # -------------------------------
    # 2. Camelot Stream
    # -------------------------------
    if len(raw_tables) == 0:

        try:

            tables = camelot.read_pdf(
                file_path,
                pages="all",
                flavor="stream"
            )

            for table in tables:

                df = table.df

                if not df.empty:

                    raw_tables.append(df.values.tolist())

        except Exception as e:

            print("Stream Error:", e)

    # -------------------------------
    # 3. pdfplumber Fallback
    # -------------------------------
    if len(raw_tables) == 0:

        try:

            with pdfplumber.open(file_path) as pdf:

                for page in pdf.pages:

                    tables = page.extract_tables()

                    for table in tables:

                        if table:

                            raw_tables.append(table)

        except Exception as e:

            print("pdfplumber Error:", e)

    return raw_tables


def process_pdf(file_path):

    return {
        "text": extract_text(file_path),
        "tables": extract_tables(file_path)
    }