"""
Table extraction using Gemini's vision capability (free tier).

Used ONLY for the hard cases:
  - scanned PDF pages (no text layer)
  - blurry / low-quality pages
  - image screenshots (.png/.jpg/.jpeg)
  - any PDF page where Camelot/pdfplumber came back empty

Normal, text-based PDF pages are handled entirely by pdf_processor.py
(Camelot/pdfplumber) with zero API cost -- this module is only called
as a per-page fallback from document_understanding.py.

Requires:
    pip install google-genai pdf2image
    export GEMINI_API_KEY=your-key-from-aistudio.google.com
"""

import os
import json
import time

import pandas as pd
from google import genai
from google.genai import types
from pdf2image import convert_from_path

# processing/ sits at the repo root (see backend/main.py's own comment
# about this), so the root is just this file's parent directory.
_PROCESSING_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_PROCESSING_DIR)

# -----------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------

# Free-tier eligible. gemini-2.5-flash-lite has the highest free-tier
# request quota if you're processing lots of pages; gemini-2.5-flash is
# slightly more accurate. Swap as needed.
DEFAULT_MODEL = "gemini-3.5-flash"

_client = None


def _get_client():
    """
    Created on first actual use, not at import time -- so the whole
    app (including plain xlsx uploads that never touch Gemini) can
    still start even if GEMINI_API_KEY isn't set yet. You'll only see
    an error when a scanned page/image is actually processed.
    """
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set.")

        _client = genai.Client(api_key=api_key)
    return _client

EXTRACTION_SYSTEM_PROMPT = """You are a document data-extraction engine.

You will be shown one page of a scanned PDF or an image screenshot. Extract
every piece of information on the page that can be organized into a table.

- If the page already contains a real table, reproduce it faithfully:
  same column headers (or your best reading of them), same rows, same
  values. Do not skip rows.
- If the page is NOT a table (e.g. a letter, an invoice, a form, a list of
  facts, a spec sheet), organize the meaningful information yourself into
  a clean table -- commonly a two-column "Field" / "Value" table, or
  multiple small tables if the page has distinct sections.
- If the page has no extractable information at all (blank, purely
  decorative), return an empty "tables" list.

Respond with STRICT JSON ONLY. No markdown code fences, no commentary,
no text before or after the JSON. Use exactly this schema:

{
  "tables": [
    {
      "title": "short descriptive title for this table",
      "headers": ["Column1", "Column2", "..."],
      "rows": [
        ["cell", "cell", "..."],
        ["cell", "cell", "..."]
      ]
    }
  ]
}

Rules:
- Every row array must have the same number of elements as "headers".
- Use "" for a missing/blank cell -- never omit a cell or shorten a row.
- Keep numbers as plain strings, no thousands separators (e.g. "1234.5",
  not "1,234.50"), unless the value is clearly an ID, code, or date.
- Do not invent data that is not visible on the page.
"""


# -----------------------------------------------------------------------
# Response parsing
# -----------------------------------------------------------------------

def _parse_json_response(raw_text):
    cleaned = (raw_text or "").strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print("Gemini extraction JSON parse error:", e)
        print("Raw response was:", raw_text[:500] if raw_text else "<empty>")
        return []

    return data.get("tables", [])


# -----------------------------------------------------------------------
# Gemini call (with basic retry for free-tier rate limits)
# -----------------------------------------------------------------------

def extract_tables_with_gemini(image_path, model=DEFAULT_MODEL, max_retries=3):
    """
    Sends a single page image to Gemini and returns a list of tables:
    [{"title": ..., "headers": [...], "rows": [[...], ...]}, ...]
    """

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    ext = os.path.splitext(image_path)[1].lower().replace(".", "")

    if ext in ("jpg", "jpeg"):
        mime_type = "image/jpeg"
    elif ext == "webp":
        mime_type = "image/webp"
    else:
        mime_type = "image/png"

    last_error = None

    for attempt in range(max_retries):

        try:

            response = _get_client().models.generate_content(
                model=model,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    types.Part.from_text(
                        text="Extract the table(s) from this page as JSON per the schema in your instructions."
                    ),
                ],
                config=types.GenerateContentConfig(
                    system_instruction=EXTRACTION_SYSTEM_PROMPT,
                    temperature=0,
                ),
            )

            return _parse_json_response(response.text)

        except Exception as e:

            last_error = e

            # Free tier RPM limit -- back off and retry
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                wait = (attempt + 1) * 15
                print(f"Gemini rate limited, waiting {wait}s (attempt {attempt + 1}/{max_retries})...")
                time.sleep(wait)
                continue

            print("Gemini extraction error:", e)
            break

    print("Gemini extraction failed after retries:", last_error)
    return []


def gemini_tables_to_dataframes(gemini_tables):
    dataframes = []
    names = []

    for t in gemini_tables:
        headers = t.get("headers") or None
        rows = t.get("rows", [])

        try:
            df = pd.DataFrame(rows, columns=headers)
        except Exception:
            df = pd.DataFrame(rows)

        dataframes.append(df)
        names.append((t.get("title") or "Table")[:31])

    return dataframes, names


# -----------------------------------------------------------------------
# Public entry points used by document_understanding.py
# -----------------------------------------------------------------------

def extract_image_with_gemini(image_path, model=DEFAULT_MODEL):
    """
    For .png/.jpg/.jpeg uploads -- always routed here directly,
    no local-OCR attempt first.
    """

    tables = extract_tables_with_gemini(image_path, model=model)

    return gemini_tables_to_dataframes(tables)


def _rasterize_pdf_page(pdf_path, page_number, dpi=200, output_folder=None):

    if output_folder is None:
        output_folder = os.path.join(_PROJECT_ROOT, "uploads", "gemini_pages")

    os.makedirs(output_folder, exist_ok=True)

    images = convert_from_path(
        pdf_path,
        dpi=dpi,
        first_page=page_number,
        last_page=page_number,
    )

    if not images:
        return None

    image_path = os.path.join(output_folder, f"gemini_page_{page_number}.png")
    images[0].save(image_path, "PNG")

    return image_path


def extract_pages_with_gemini(pdf_path, page_numbers, model=DEFAULT_MODEL):
    """
    Rasterizes and sends ONLY the given page numbers to Gemini -- these
    are the pages pdf_processor.py already tried Camelot/pdfplumber on
    and got nothing back from (scanned, blurry, image-only, etc).
    """

    all_dataframes = []
    all_names = []

    for page_number in page_numbers:

        image_path = _rasterize_pdf_page(pdf_path, page_number)

        if not image_path:
            continue

        tables = extract_tables_with_gemini(image_path, model=model)

        dfs, names = gemini_tables_to_dataframes(tables)

        for df, name in zip(dfs, names):
            all_dataframes.append(df)
            all_names.append(f"Page{page_number}_{name}"[:31])

    return all_dataframes, all_names
