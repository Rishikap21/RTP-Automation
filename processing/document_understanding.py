from processing.pdf_processor import extract_tables as extract_pdf_tables
from processing.table_extractor import extract_tables_from_file
from processing.dataframe_builder import build_dataframes
from processing.metadata_extractor import extract_metadata
from processing.gemini_extractor import (
    extract_image_with_gemini,
    extract_pages_with_gemini,
)


def understand_document(file_path, extension):
    """
    Routing rule for this project:

      .xlsx / .xls  -> always the classic reader (already structured,
                        no extraction ambiguity, no reason to spend
                        an API call on it).

      .pdf          -> per page: try Camelot/pdfplumber first (free,
                        local, python libraries). Any page that comes
                        back with NOTHING (scanned, blurry, an image
                        pasted into an otherwise-normal PDF, etc.)
                        gets rasterized and sent to Gemini -- but only
                        that specific page, not the whole document.
                        A "normal" PDF costs $0 in API calls. A fully
                        scanned PDF costs one Gemini call per page.

      .png/.jpg/.jpeg -> always Gemini. A raw image has no text layer
                        to try locally in the first place, so there's
                        no free-tier-first step to attempt.
    """

    extension_lower = extension.lower()

    if extension_lower in [".xlsx", ".xls"]:

        raw_tables, sheet_names = extract_tables_from_file(
            file_path,
            extension_lower
        )

        dataframes = build_dataframes(raw_tables)

    elif extension_lower == ".pdf":

        dataframes, sheet_names = _process_pdf_hybrid(file_path)

    elif extension_lower in [".png", ".jpg", ".jpeg"]:

        dataframes, sheet_names = extract_image_with_gemini(file_path)

    else:

        dataframes, sheet_names = [], []

    metadata = extract_metadata(
        file_path=file_path,
        extension=extension,
        dataframes=dataframes
    )

    if sheet_names is None:
        sheet_names = []

    return {
        "metadata": metadata,
        "dataframes": dataframes,
        "sheet_names": sheet_names
    }


def _process_pdf_hybrid(file_path):

    raw_tables, missing_pages = extract_pdf_tables(file_path)

    dataframes = build_dataframes(raw_tables)

    sheet_names = [f"Table_{i + 1}" for i in range(len(dataframes))]

    if missing_pages:

        print(f"Pages with no local extraction, routing to Gemini: {missing_pages}")

        gemini_dataframes, gemini_names = extract_pages_with_gemini(
            file_path,
            missing_pages
        )

        dataframes.extend(gemini_dataframes)
        sheet_names.extend(gemini_names)

    return dataframes, sheet_names
