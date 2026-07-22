import pandas as pd


def read_excel(file_path):

    sheets = []

    try:

        excel_file = pd.ExcelFile(file_path)

        for sheet_name in excel_file.sheet_names:

            df = pd.read_excel(
                excel_file,
                sheet_name=sheet_name,
                header=None
            )

            df = df.fillna("")

            sheets.append({
                "sheet_name": sheet_name,
                "rows": df.values.tolist()
            })

    except Exception as e:

        print("Excel Read Error:", e)

    return sheets


def process_excel(file_path):

    return read_excel(file_path)