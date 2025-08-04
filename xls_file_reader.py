import pandas as pd

target_string = "Единица измерения: Метрическая тонна"
COLUMNS_TO_EXTRACT = {"exchange_product_id": 'Код\nИнструмента',
                      "exchange_product_name": "Наименование\nИнструмента",
                      "delivery_basis_name": "Базис\nпоставки",
                      "volume": "Объем\nДоговоров\nв единицах\nизмерения",
                      "total": "Обьем\nДоговоров,\nруб.",
                      "count": "Количество\nДоговоров,\nшт."}
end_markers = ["Итого:", "Итого по секции:", "Маклер АО Петербургская Биржа"]


def read_xls_file(file_bytes):
    sheet_df = pd.read_excel(file_bytes, header=None, dtype=str)

    header_row = None
    for i, row in sheet_df.iterrows():
        if row.astype(str).str.contains(target_string).any():
            header_row = i + 1
            break

    if header_row is None:
        raise ValueError(f"Строка '{target_string}' не найдена")

    data_start = header_row + 1
    data = []
    for i in range(data_start, len(sheet_df)):
        row = sheet_df.loc[i]
        row_text = " ".join(sheet_df.iloc[i].fillna("").astype(str))
        if row.isnull().all() or any(marker in row_text for marker in end_markers):
            break
        data.append(row.values)

    columns = sheet_df.loc[header_row].tolist()
    table_df = pd.DataFrame(data, columns=columns)

    filtered_df = table_df[COLUMNS_TO_EXTRACT.values()]

    filtered_df = filtered_df.dropna(how='all')

    count_column = COLUMNS_TO_EXTRACT["count"]
    filtered_df[count_column] = pd.to_numeric(
        filtered_df[count_column], errors="coerce"
    )

    filtered_df = filtered_df[filtered_df[count_column] > 0]

    return filtered_df
