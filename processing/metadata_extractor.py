import os
from datetime import datetime


def extract_metadata(file_path, extension, dataframes):
    """
    Creates generic metadata for any uploaded document.
    """

    metadata = {}

    metadata["File Name"] = os.path.basename(file_path)

    metadata["File Type"] = extension.upper().replace(".", "")

    metadata["Processed Time"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    metadata["Tables Extracted"] = len(dataframes)

    total_rows = 0

    total_columns = 0

    for df in dataframes:

        total_rows += len(df)

        total_columns = max(total_columns, len(df.columns))

    metadata["Total Rows"] = total_rows

    metadata["Maximum Columns"] = total_columns

    return metadata