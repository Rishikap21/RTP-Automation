from processing.table_classifier import classify_row
from processing.header_detector import detect_headers


def safe_float(value):
    """
    Convert value to float if possible.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def avg(*values):
    """
    Average only valid numeric values.
    """
    nums = [v for v in values if isinstance(v, (int, float))]

    if not nums:
        return None

    return round(sum(nums) / len(nums), 2)


def normalize_table(rows):
    """
    Converts extracted Excel rows into AI-ready structured records.
    """

    header_info = detect_headers(rows)
    headers = header_info["combined_headers"]

    records = []

    current_region = None
    current_refinery = None
    current_product = None
    current_unit = None

    for row in rows:

        if classify_row(row) != "DATA":
            continue

        values = list(row)

        while len(values) < len(headers):
            values.append(None)

        values = values[:len(headers)]

        record = {}

        for h, v in zip(headers, values):
            if h != "":
                record[h] = v

        # -----------------------------------
        # Forward Fill
        # -----------------------------------

        if record.get("Region"):
            current_region = record["Region"]
        else:
            record["Region"] = current_region

        if record.get("Refinery"):
            current_refinery = record["Refinery"]
        else:
            record["Refinery"] = current_refinery

        if record.get("Product"):
            current_product = record["Product"]
        else:
            record["Product"] = current_product

        if record.get("Unit"):
            current_unit = record["Unit"]
        else:
            record["Unit"] = current_unit

        # -----------------------------------
        # Convert Quarter Values
        # -----------------------------------

        fy25_q1 = safe_float(record.get("FY2025_Q1"))
        fy25_q2 = safe_float(record.get("FY2025_Q2"))
        fy25_q3 = safe_float(record.get("FY2025_Q3"))
        fy25_q4 = safe_float(record.get("FY2025_Q4"))

        fy26_q1 = safe_float(record.get("FY2026_Q1"))
        fy26_q2 = safe_float(record.get("FY2026_Q2"))
        fy26_q3 = safe_float(record.get("FY2026_Q3"))
        fy26_q4 = safe_float(record.get("FY2026_Q4"))

        # -----------------------------------
        # Calculate FY2025 averages
        # -----------------------------------

        record["FY2025_H1_Avg"] = avg(fy25_q1, fy25_q2)
        record["FY2025_H2_Avg"] = avg(fy25_q3, fy25_q4)
        record["FY2025_FY_Avg"] = avg(
            fy25_q1,
            fy25_q2,
            fy25_q3,
            fy25_q4
        )

        # -----------------------------------
        # Calculate FY2026 averages
        # -----------------------------------

        record["FY2026_H1_Avg"] = avg(fy26_q1, fy26_q2)
        record["FY2026_H2_Avg"] = avg(fy26_q3, fy26_q4)
        record["FY2026_FY_Avg"] = avg(
            fy26_q1,
            fy26_q2,
            fy26_q3,
            fy26_q4
        )

        # -----------------------------------
        # Calculate YoY %
        # -----------------------------------

        fy25 = record["FY2025_FY_Avg"]
        fy26 = record["FY2026_FY_Avg"]

        if fy25 not in (None, 0) and fy26 is not None:
            record["YoY Change (FY26 vs FY25)"] = round(
                ((fy26 - fy25) / fy25) * 100,
                2
            )
        else:
            record["YoY Change (FY26 vs FY25)"] = None

        records.append(record)

    return records