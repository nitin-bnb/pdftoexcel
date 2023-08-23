import os, re, fitz, camelot
import pandas as pd
from config import Config

download_excel_path = Config.EXCEL_FILE_PATH

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

def processNetwest(data, filename):
    df = readandcleandata(data)
    df.columns = ['Date', 'Description', 'Type', 'Paid In', 'Paid Out', 'Ledger Balance']
    date_pattern = r'^\d{2}/\d{2}/\d{4}$'

    # Filter rows based on the date pattern
    valid_date_rows = df['Date'].str.match(date_pattern, na=False)
    df = df[valid_date_rows]

    df = df.drop(columns=['Ledger Balance'])
    df = df.drop(columns=['Type'])
    with pd.ExcelWriter(f"{download_excel_path}{filename}.xlsx", engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=f"{filename}", index=False)

        # Get the openpyxl workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets[f"{filename}"]

        # Iterate through each column and set the optimal width
        for column_cells in worksheet.columns:
            length = max(len(str(cell.value)) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2
    return df

def processLLoyds(file, filename):
    words = ''
    dates = []
    descriptions = []
    paid_out = []
    paid_in = []

    doc = fitz.open(file)
    for page in doc:
        words += page.get_text("Date", sort=True)

    pattern = r'(\d{2}[A-Za-z]{3}\d{2})\s+([A-Za-z]{2,3})\s+(.+)'
    pattern = pattern + r'|(\d{2}[A-Za-z]{3}\d{2})\s+RETURNED\s+'
    matches = re.finditer(pattern, words)
    match_positions = []

    for match in matches:
        start = match.start()
        end = match.end()
        match_positions.append((start, end))

    for num in range(len(match_positions)):
        if num == len(match_positions) - 1:
            data = words[match_positions[num][0]:match_positions[num][1]+20]
            data = data.split('\n')
            for i in range(len(data)):
                data[i] = re.sub(r'\s+', '', data[i])
            dates.append(data[0][:7])
            if len(data)> 5 and not data[5] == '' and data[4] == '':
                descriptions.append(data[0][7:])
                paid_out.append(data[1])
                paid_in.append(data[2])
            elif data[1] == "RETURNEDDD":
                descriptions.append(data[1])
                paid_out.append(data[3])
                paid_in.append(data[4])
            elif '.' in data[1]:
                descriptions.append(data[0][7:])
                paid_out.append(data[1])
                paid_in.append(data[2])
            elif data[1]:
                descriptions.append(data[1])
                paid_out.append(data[2])
                paid_in.append(data[3])
            else:
                descriptions.append(data[0][7:])
                paid_out.append(data[2])
                paid_in.append(data[3])
        else:
            data = words[match_positions[num][0]:match_positions[num + 1][0]]
            data = data.split('\n')
            for i in range(len(data)):
                data[i] = re.sub(r'\s+', '', data[i])
            dates.append(data[0][:7])
            if len(data)> 5 and not data[5] == '' and data[4] == '':
                descriptions.append(data[0][7:])
                paid_out.append(data[1])
                paid_in.append(data[2])
            elif data[1] == "RETURNEDDD":
                descriptions.append(data[1])
                paid_out.append(data[3])
                paid_in.append(data[4])
            elif '.' in data[1]:
                descriptions.append(data[0][7:])
                paid_out.append(data[1])
                paid_in.append(data[2])
            elif data[1]:
                descriptions.append(data[1])
                paid_out.append(data[2])
                paid_in.append(data[3])
            else:
                descriptions.append(data[0][7:])
                paid_out.append(data[2])
                paid_in.append(data[3])

    df = pd.DataFrame({"Date": dates,"Description":descriptions, "Paid Out": paid_out, "Paid In": paid_in})

    with pd.ExcelWriter(f"{download_excel_path}{filename}.xlsx", engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=f"{filename}", index=False)

            # Get the openpyxl workbook and worksheet objects
            writer.book
            worksheet = writer.sheets[f"{filename}"]

            # Iterate through each column and set the optimal width
            for column_cells in worksheet.columns:
                length = max(len(str(cell.value)) for cell in column_cells)
                worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2

def processLLoyds2(data, filename):
    df = readandcleandata(data)
    df.columns = ['Date', 'Description', 'Type', 'Paid In', 'Paid Out', 'Balance']
    date_pattern = r'^\d{2} \w{3} \d{2}$'

    # Filter rows based on the date pattern
    valid_date_rows = df['Date'].str.match(date_pattern, na=False)
    df = df[valid_date_rows]

    df = df.drop(columns=['Balance'])
    df = df.drop(columns=['Type'])
    with pd.ExcelWriter(f"{download_excel_path}{filename}.xlsx", engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=f"{filename}", index=False)

        # Get the openpyxl workbook and worksheet objects
        writer.book
        worksheet = writer.sheets[f"{filename}"]

        # Iterate through each column and set the optimal width
        for column_cells in worksheet.columns:
            length = max(len(str(cell.value)) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2
    return df

def processHSBC(file, filename):
    date_pattern = r"\d{2} \w{3} \d{2}"
    tables = camelot.read_pdf(file, pages="all", flavor="stream")
    structured_data = pd.DataFrame()

    for table in tables:
        df = table.df
        if len((df.columns)) == 4:
            df = df.iloc[2:]
            structured_data = pd.concat([structured_data, df], ignore_index=True)
        elif len((df.columns)) == 5:
            parsed_df = df.copy()
            parsed_df.columns = [0, 'blank', 1, 2, 3]
            parsed_df = parsed_df.drop(columns=parsed_df.columns[1])
            structured_data = pd.concat([structured_data, parsed_df], ignore_index=True)

    structured_data = structured_data.drop(columns=3)

    # Filtering rows based on specific details
    details_to_drop = ["BALANCE BROUGHT FORWARD", "BALANCE CARRIED FORWARD"]
    structured_data = structured_data[~structured_data[0].str.contains('|'.join(details_to_drop)) |
                                    (structured_data.index == 0) |
                                    (structured_data.index == len(structured_data) - 1)]

    column_header = ['Details', 'Paid Out', 'Paid In']
    structured_data.columns = column_header

    # Drop first three rows
    structured_data = structured_data.iloc[3:-1]

    # Format Excel file
    with pd.ExcelWriter(f"{download_excel_path}{filename}.xlsx", engine="openpyxl") as writer:
        structured_data.to_excel(writer, sheet_name=f"{filename}", index=False)
        writer.book
        worksheet = writer.sheets[f"{filename}"]
        date_column_header = "Date"
        worksheet.insert_cols(0)
        worksheet.cell(row=1, column=1, value=date_column_header)
        for index, rows_cells in enumerate(worksheet.rows):
            length = max(len(str(cell.value)) for cell in rows_cells)
            worksheet.row_dimensions[rows_cells[1].row].height = length + 15
            worksheet.row_dimensions[rows_cells[1].row].width = length + 15
            matches = re.findall(date_pattern, str(rows_cells[1].value))
            if matches:
                worksheet.row_dimensions[rows_cells[1].row].width = length + 15
                rows_cells[1].value = rows_cells[1].value.replace(matches[0], "")
                worksheet.cell(row=index + 1, column=1, value=matches[0])
        for column_cells in worksheet.columns:
            length = max(len(str(cell.value)) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2

def processBarclays(data, filename):
    df = pd.concat(data, ignore_index=True)
    df.columns = ['Date', 'Description', 'Paid In', 'Paid Out', 'Balance']
    df.drop(columns=['Balance'])
    df.drop(0, inplace=True)

    with pd.ExcelWriter(f"{download_excel_path}{filename}.xlsx", engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=f"{filename}", index=False)

        # Get the openpyxl workbook and worksheet objects
        writer.book
        worksheet = writer.sheets[f"{filename}"]

        # Iterate through each column and set the optimal width
        for column_cells in worksheet.columns:
            length = max(len(str(cell.value)) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2
    return df