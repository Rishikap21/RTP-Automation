from processing.table_extractor import extract_tables_from_file
from processing.dataframe_builder import build_dataframes
from processing.metadata_extractor import extract_metadata


def understand_document(file_path, extension):

    raw_tables, sheet_names = extract_tables_from_file(
        file_path,
        extension
    )

    dataframes = build_dataframes(raw_tables)

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