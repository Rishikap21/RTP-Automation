def classify_row(row):
    """
    Classifies every row extracted from Excel.
    """

    cells = [
        "" if cell is None else str(cell).strip()
        for cell in row
    ]

    values = [c.upper() for c in cells]

    # -------------------------
    # Empty row
    # -------------------------
    if all(cell == "" for cell in cells):
        return "EMPTY"

    first = values[0]

    # -------------------------
    # Ignore metadata
    # -------------------------
    ignore_keywords = [
        "PREPARED BY",
        "APPROVED BY",
        "DATE",
        "STATUS",
        "CONFIDENTIAL",
        "LEGEND"
    ]

    for keyword in ignore_keywords:
        if keyword in first:
            return "OTHER"

    # -------------------------
    # Notes / Sections
    # -------------------------
    if first.startswith("SECTION"):
        return "SECTION"

    if first.startswith("NOTE"):
        return "NOTE"

    if "COMPANY-WIDE GRAND TOTAL" in first:
        return "GRAND_TOTAL"

    if "REGION SUBTOTAL" in first:
        return "REGION_TOTAL"

    # -------------------------
    # HEADER ROW 1
    # -------------------------
    if "REGION" in values and "REFINERY" in values:
        return "HEADER"

    # -------------------------
    # HEADER ROW 2
    # Fiscal Years
    # -------------------------
    if any("FISCAL YEAR" in v for v in values):
        return "HEADER"

    # -------------------------
    # HEADER ROW 3
    # Quarter names
    # -------------------------
    header_keywords = {
        "Q1",
        "Q2",
        "Q3",
        "Q4",
        "H1 AVG",
        "H2 AVG",
        "FY AVG",
        "YOY CHANGE",
        "ANALYST NOTES"
    }

    count = 0

    for v in values:
        for h in header_keywords:
            if h in v:
                count += 1

    if count >= 2:
        return "HEADER"

    # -------------------------
    # DATA ROW
    # -------------------------
    if len(cells) >= 5:

        has_product = cells[2] != ""

        has_grade = cells[3] != ""

        has_numbers = any(
            isinstance(x, (int, float))
            for x in row
        )

        if (has_product or has_grade) and has_numbers:
            return "DATA"

    return "OTHER"