from openpyxl import Workbook

def create_excel(tables, output_path):
    workbook = Workbook()

    # Remove default sheet
    workbook.remove(workbook.active)

    # If no tables are found, create one sheet with a message
    if not tables:
        sheet = workbook.create_sheet(title="No Tables")
        sheet["A1"] = "No tables were extracted from the PDF."
    else:
        for index, table in enumerate(tables):
            sheet = workbook.create_sheet(title=f"Table_{index + 1}")

            for row in table:
                sheet.append(row)

    workbook.save(output_path)