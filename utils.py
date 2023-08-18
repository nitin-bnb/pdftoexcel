import fitz
import re
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

    with pd.ExcelWriter(f"{filename}.xlsx", engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name={filename}, index=False)

            # Get the openpyxl workbook and worksheet objects
            writer.book
            worksheet = writer.sheets["LL"]

            # Iterate through each column and set the optimal width
            for column_cells in worksheet.columns:
                length = max(len(str(cell.value)) for cell in column_cells)
                worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2

def processLLoyds2(df, filename):
    date_pattern = r'^\d{2} \w{3} \d{2}$'

    # Filter rows based on the date pattern
    valid_date_rows = df['Date'].str.match(date_pattern, na=False)
    df = df[valid_date_rows]

    df = df.drop(columns=['Balance'])
    df = df.drop(columns=['Type'])
    with pd.ExcelWriter(f"{filename}.xlsx", engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=f"{filename}", index=False)

        # Get the openpyxl workbook and worksheet objects
        writer.book
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
        writer.book
        worksheet = writer.sheets[f"{filename}"]

        # Iterate through each column and set the optimal width
        for column_cells in worksheet.columns:
            length = max(len(str(cell.value)) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2
    return df