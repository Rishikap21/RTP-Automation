import pandas as pd


def clean_excel_data(excel_data):

    cleaned_data = []

    for sheet in excel_data:

        rows = sheet["rows"]

        df = pd.DataFrame(rows)

        # Remove completely empty rows
        df = df.dropna(how="all")

        # Remove completely empty columns
        df = df.dropna(axis=1, how="all")

        # Fill merged-cell values downward
        df = df.ffill()

        # Replace remaining NaN with empty string
        df = df.fillna("")

        cleaned_data.append({
            "sheet_name": sheet["sheet_name"],
            "rows": df.values.tolist()
        })

    return cleaned_data