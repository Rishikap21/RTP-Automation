import pandas as pd
from processing.table_classifier import classify_row


def detect_headers(rows):
    """
    Detects multi-level headers and creates clean column names.

    Returns:
    {
        "header_rows": [...],
        "combined_headers": [...]
    }
    """

    header_rows = []

    start_index = -1

    # ----------------------------
    # Find header start
    # ----------------------------
    for i, row in enumerate(rows):

        values = [
            str(cell).strip().lower()
            if cell is not None else ""
            for cell in row
        ]

        if "region" in values and "refinery" in values:
            start_index = i
            break

    if start_index == -1:
        return {
            "header_rows": [],
            "combined_headers": []
        }

    # ----------------------------
    # Collect header rows
    # ----------------------------
    for row in rows[start_index:]:

        row_type = classify_row(row)

        if row_type == "DATA":
            break

        if row_type == "HEADER":
            header_rows.append(row)

    df = pd.DataFrame(header_rows)

    # Fill ONLY merged fiscal year cells
    df.iloc[0] = df.iloc[0].ffill()

    combined_headers = []

    for col in df.columns:

        row1 = ""
        row2 = ""
        row3 = ""

        if len(df) > 0 and pd.notna(df.iloc[0, col]):
            row1 = str(df.iloc[0, col]).strip()

        if len(df) > 1 and pd.notna(df.iloc[1, col]):
            row2 = str(df.iloc[1, col]).strip()

        if len(df) > 2 and pd.notna(df.iloc[2, col]):
            row3 = str(df.iloc[2, col]).strip()

        # ----------------------------
        # Basic columns
        # ----------------------------
        if row1 in [
            "Region",
            "Refinery",
            "Product",
            "Grade / Spec",
            "Unit",
            "YoY Change (FY26 vs FY25)",
            "Analyst Notes"
        ]:
            combined_headers.append(row1)
            continue

        # ----------------------------
        # Fiscal Year columns
        # ----------------------------
        if row1.startswith("Fiscal Year"):

            year = row1.replace("Fiscal Year ", "FY")

            if row3 != "":
                header = f"{year}_{row3}"

            elif row2 != "":
                header = f"{year}_{row2.replace(' ', '_')}"

            else:
                header = year

            combined_headers.append(header)
            continue

        combined_headers.append(row1)

    # ----------------------------
    # Remove duplicate names
    # ----------------------------
    seen = {}

    unique_headers = []

    for header in combined_headers:

        if header not in seen:
            seen[header] = 1
            unique_headers.append(header)
        else:
            seen[header] += 1
            unique_headers.append(f"{header}_{seen[header]}")

    # ----------------------------
    # DEBUG
    # ----------------------------

    print("\n========== HEADER ROWS ==========")

    for row in header_rows:
        print(row)

    print("\n========== COMBINED HEADERS ==========")

    for header in unique_headers:
        print(header)

    print("=====================================\n")

    return {
        "header_rows": header_rows,
        "combined_headers": unique_headers
    }