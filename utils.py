import pandas as pd

def remove_extra_headers(df):
    header_row = df.iloc[0]
    if header_row[0] == 'Date' and header_row[1] == 'Narrative' or (header_row[0] == 'Date' and header_row[1] == 'Description'):
        return df[df.index != 0].dropna(subset=[0], how='all')
    return df.dropna(subset=[0], how='all')

def readandcleandata(data):

# Assuming 'data' contains the extracted tables from each page
# data is a list of DataFrames representing tables from each page
# You can create a new list to store the cleaned dataframes after removing header rows.

    cleaned_data = []

    # Loop through each DataFrame from the 'data' list
    for df in data:

        # Remove rows with NaN values in the 'Date' column to get rid of headers
        df_cleaned = remove_extra_headers(df)
        
        # Assuming the header is present only on the first page, drop it from subsequent pages
        if len(cleaned_data) > 0:
            df_cleaned = df_cleaned.iloc[1:]
        
        # Append the cleaned DataFrame to the new list
        cleaned_data.append(df_cleaned)

    # Concatenate all cleaned DataFrames into a single DataFrame
    df_concatenated = pd.concat(cleaned_data, ignore_index=True)

    return df_concatenated

def processNetwest(df, filename):
    date_pattern = r'^\d{2}/\d{2}/\d{4}$'

    # Filter rows based on the date pattern
    valid_date_rows = df['Date'].str.match(date_pattern, na=False)
    df = df[valid_date_rows]

    df = df.drop(columns=['Ledger Balance'])
    df = df.drop(columns=['Type'])
    with pd.ExcelWriter(f"{filename}.xlsx", engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=f"{filename}", index=False)

        # Get the openpyxl workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets[f"{filename}"]

        # Iterate through each column and set the optimal width
        for column_cells in worksheet.columns:
            length = max(len(str(cell.value)) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2
    return df

def processLLoyds(df, filename):
    date_pattern = r'^\d{2}/\w{3}/\d{2}$'


    # Filter rows based on the date pattern
    valid_date_rows = df['Date'].str.match(date_pattern, na=False)
    df = df[valid_date_rows]

    df = df.drop(columns=['Balance'])
    with pd.ExcelWriter(f"{filename}.xlsx", engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=f"{filename}", index=False)

        # Get the openpyxl workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets[f"{filename}"]

        # Iterate through each column and set the optimal width
        for column_cells in worksheet.columns:
            length = max(len(str(cell.value)) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2
    return df

def processLLoyds2(df, filename):
    # df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    # df = df.dropna(subset=['Date'])
    # Regular expression to match the expected date format 'dd/mm/yyyy'
    date_pattern = r'^\d{2} \w{3} \d{2}$'

    # Filter rows based on the date pattern
    valid_date_rows = df['Date'].str.match(date_pattern, na=False)
    df = df[valid_date_rows]

    df = df.drop(columns=['Balance'])
    df = df.drop(columns=['Type'])
    with pd.ExcelWriter(f"{filename}.xlsx", engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=f"{filename}", index=False)

        # Get the openpyxl workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets[f"{filename}"]

        # Iterate through each column and set the optimal width
        for column_cells in worksheet.columns:
            length = max(len(str(cell.value)) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2
    return df

def processHSBC(df, filename):
    # date_pattern = r'^\d{2} \w{3} \d{2}$'

    # # Filter rows based on the date pattern
    # valid_date_rows = df['Date'].str.match(date_pattern, na=False)
    # df = df[valid_date_rows]

    # df = df.drop(columns=['Balance'])
    # df = df.drop(columns=['Type'])
    with pd.ExcelWriter(f"{filename}.xlsx", engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=f"{filename}", index=False)

        # Get the openpyxl workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets[f"{filename}"]

        # Iterate through each column and set the optimal width
        for column_cells in worksheet.columns:
            length = max(len(str(cell.value)) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2
    return df