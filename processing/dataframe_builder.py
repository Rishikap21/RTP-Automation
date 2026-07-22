import pandas as pd


def build_dataframes(raw_tables):
    """
    Converts extracted raw tables into pandas DataFrames.

    Parameters
    ----------
    raw_tables : list
        Example:
        [
            [["A","B"],["1","2"]],
            [["X","Y"],["10","20"]]
        ]

    Returns
    -------
    list[pandas.DataFrame]
    """

    dataframes = []

    if not raw_tables:
        return dataframes

    for table in raw_tables:

        if not table:
            continue

        try:

            header = table[0]

            rows = table[1:]

            df = pd.DataFrame(rows, columns=header)

            # Remove completely empty rows
            df.dropna(how="all", inplace=True)

            # Remove completely empty columns
            df.dropna(axis=1, how="all", inplace=True)

            dataframes.append(df)

        except Exception:

            try:

                df = pd.DataFrame(table)

                df.dropna(how="all", inplace=True)

                df.dropna(axis=1, how="all", inplace=True)

                dataframes.append(df)

            except Exception:
                pass

    return dataframes