import re, fitz, camelot
import pandas as pd
from config import Config
from flask import Response
from pdf2image import convert_from_path
import pytesseract
import openpyxl
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows  # Import the function

download_excel_path = Config.EXCEL_FILE_PATH


def remove_extra_headers(df):
    header_row = df.iloc[0]
    if header_row[0] == 'Date' and header_row[1] == 'Narrative' or (header_row[0] == 'Date' and header_row[1] == 'Description'):
        return df[df.index != 0].dropna(subset=[0], how='all')
    return df.dropna(subset=[0], how='all')


def readandcleandata(data):
    cleaned_data = []
    for df in data:
        df_cleaned = remove_extra_headers(df)
        if len(cleaned_data) > 0:
            df_cleaned = df_cleaned.iloc[1:]

        cleaned_data.append(df_cleaned)

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

    try:
        with pd.ExcelWriter(f"{download_excel_path}{filename}.xlsx", engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=f"{filename}", index=False)
            workbook = writer.book
            worksheet = writer.sheets[f"{filename}"]
            for column_cells in worksheet.columns:
                length = max(len(str(cell.value)) for cell in column_cells)
                worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2

        return Response(status=201)
    except Exception as e:
        return Response(status=404)


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

    try:
        with pd.ExcelWriter(f"{download_excel_path}{filename}.xlsx", engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name=f"{filename}", index=False)
                writer.book
                worksheet = writer.sheets[f"{filename}"]
                for column_cells in worksheet.columns:
                    length = max(len(str(cell.value)) for cell in column_cells)
                    worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2

        return Response(status=201)
    except Exception as e:
        return Response(status=404)


def processLLoyds2(data, filename):
    df = readandcleandata(data)
    df.columns = ['Date', 'Description', 'Type', 'Paid In', 'Paid Out', 'Balance']
    date_pattern = r'^\d{2} \w{3} \d{2}$'
    valid_date_rows = df['Date'].str.match(date_pattern, na=False)
    df = df[valid_date_rows]
    df = df.drop(columns=['Balance'])
    df = df.drop(columns=['Type'])

    try:
        with pd.ExcelWriter(f"{download_excel_path}{filename}.xlsx", engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=f"{filename}", index=False)
            writer.book
            worksheet = writer.sheets[f"{filename}"]

            for column_cells in worksheet.columns:
                length = max(len(str(cell.value)) for cell in column_cells)
                worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2

        return Response(status=201)
    except Exception as e:
        return Response(status=404)


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
    details_to_drop = ["BALANCE BROUGHT FORWARD", "BALANCE CARRIED FORWARD"]
    structured_data = structured_data[~structured_data[0].str.contains('|'.join(details_to_drop)) |
                                    (structured_data.index == 0) |
                                    (structured_data.index == len(structured_data) - 1)]

    column_header = ['Details', 'Paid Out', 'Paid In']
    structured_data.columns = column_header
    structured_data = structured_data.iloc[3:-1]

    try:
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

        return Response(status=201)
    except Exception as e:
        return Response(status=404)


def processBarclays(data, filename):
    df = pd.concat(data, ignore_index=True)
    df.columns = ['Date', 'Description', 'Paid In', 'Paid Out', 'Balance']
    df.drop(columns=['Balance'])
    df.drop(0, inplace=True)

    try:
        with pd.ExcelWriter(f"{download_excel_path}{filename}.xlsx", engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=f"{filename}", index=False)
            writer.book
            worksheet = writer.sheets[f"{filename}"]

            for column_cells in worksheet.columns:
                length = max(len(str(cell.value)) for cell in column_cells)
                worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2

        return Response(status=201)
    except Exception as e:
        return Response(status=404)


def processHSBC_Scanned(file, filename):
    Data_Objects = []
    combined_list = []
    formatted_list = []

    def convert_pdf_to_text(file):
        extracted_text = ''
        # Convert PDF pages to images
        images = convert_from_path(file, dpi=300)
        # Perform OCR on each image
        for img in images:
            text = pytesseract.image_to_string(img)
            extracted_text += text
        return extracted_text

    # Your existing PDF processing code
    extracted_text = convert_pdf_to_text(file)
    column_headers = ['Date', 'Type', 'Details', 'Paid Out', 'Paid In', 'Balance']
    # Create a DataFrame to store the data
    df = pd.DataFrame(columns=column_headers)
    lines = extracted_text.split('\n')

    for index, line in enumerate(lines):
        if line != '':
            if index < len(lines) - 1 and bool(re.match(r'\d', line)):
                combined_string = line + ' ' + lines[index + 1]
                Data_Objects.append(combined_string)
            else:
                Data_Objects.append(line)

    i = 0
    while i < len(Data_Objects) - 1:
        combined_string = Data_Objects[i] + "" + Data_Objects[i + 1]
        combined_list.append(combined_string)
        i += 2  # Move to the next pair of strings

    if len(Data_Objects) % 2 != 0:
        combined_list.append(Data_Objects[-1])

    for data in combined_list:
        parts = data.split()
        if parts[1] == 'DR' or parts[1] == 'BP':
            if len(parts) == 7:
                formatted_data = [
                    parts[0],
                    parts[1],
                    ' '.join(parts[2:-1]),
                    parts[-1],
                    '',
                    '',
                ]
            else:
                formatted_data = [
                    parts[0],
                    parts[1],
                    ' '.join(parts[2:-2]),
                    parts[-2],
                    '',
                    parts[-1],
                ]
            formatted_list.append(formatted_data)
        elif parts[1] == 'TFR':
            formatted_data = [
                parts[0],
                parts[1],
                ' '.join(parts[2:-3]),
                '',
                ''.join(parts[-3:-1]),
                parts[-1],
            ]
            formatted_list.append(formatted_data)

    # Add the formatted data to the DataFrame
    for data in formatted_list:
        df.loc[len(df)] = data

    # Replace ":" with "." in all columns
    df = df.apply(lambda x: x.str.replace(":", "."))

    try:
        # Create a new Excel workbook
        workbook = Workbook()
        worksheet = workbook.active
        # Convert the DataFrame to an Excel sheet
        for row in dataframe_to_rows(df, index=False, header=True):
            worksheet.append(row)
        # Adjust column widths based on the content
        for column_cells in worksheet.columns:
            max_length = 0
            column = column_cells[0].column_letter  # Get the column name
            for cell in column_cells:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet.column_dimensions[column].width = adjusted_width
        # Save the Excel file
        workbook.save(f"{download_excel_path}{filename}.xlsx")
        return Response(status=201)
    except Exception as e:
        return Response(status=404)


def processNatwest_Large_Scanned(file, filename):
    rows_to_skip = {
        1: (22, 7),
        2: (7, 4),
    }

    def convert_pdf_to_text(file, rows_to_skip):
        extracted_text = ''
        page_number = 1
        images = convert_from_path(file, dpi=300)

        for img in images:
            text = pytesseract.image_to_string(img)
            lines = text.split('\n')
            start_skip, end_skip = rows_to_skip.get(page_number, (0, 0))
            lines = lines[start_skip:-end_skip] if end_skip > 0 else lines[start_skip:]
            page_text = '\n'.join(lines)
            extracted_text += page_text
            page_number += 1
        return extracted_text

    def process_row(row):
        date = ''
        detail = ''
        withdrawn = ''
        paid_in = ''
        balance = ''

        all_words = row.split()
        if len(all_words) > 1 and all_words[1][-1] == 'N':
            all_words[0] = all_words[0] + all_words[1]
            del all_words[1]
            row = " ".join(all_words)

        if all_words:
            first_word = all_words[0]
            if 'Bill Payment' in row:
                date_detail_parts = row.split('Bill Payment', 1)
                if len(date_detail_parts) == 2:
                    date = date_detail_parts[0].strip()
                    detail = 'Bill Payment ' + date_detail_parts[1].strip()
                    date_match = re.search(r'\d{2}/\d{2}/\d{4}', date)
                    if date_match:
                        date = date_match.group()
                    else:
                        date = ''
                else:
                    detail = row
            elif len(first_word) == 18:
                row_items = re.split(r'\s+', row)
                if len(row_items) >= 3:
                    detail = row_items[0]
                    withdrawn = row_items[1]
                    balance = row_items[2]
                else:
                    detail = row
            elif '.' in row:
                floatItems = re.findall("\d+\.\d+", row)
                for f in floatItems:
                    row = row.replace(f, "")
                row = row.strip()
                detail = row
                paid_in = floatItems[0]
                balance = floatItems[1]
            else:
                date = ''
                detail = row
                paid_in = ''
                balance = ''
                withdrawn = ''
        return date, detail, withdrawn, paid_in, balance

    extracted_text = convert_pdf_to_text(file, rows_to_skip)

    data = []
    lines = extracted_text.split('\n')

    for line in lines:
        date, detail, withdrawn, paid_in, balance = process_row(line)
        if any([date, detail, withdrawn, paid_in, balance]):
            data.append([date, detail, withdrawn, paid_in, balance])

    try:
        df = pd.DataFrame(data)
        workbook = Workbook()
        sheet = workbook.active
        # Add column headers
        column_headers = ['Date', 'Details', 'Withdrawn', 'Paid In', 'Balance']
        sheet.append(column_headers)

        # Add data from the DataFrame to the worksheet
        for row in dataframe_to_rows(df, index=False, header=False):
            sheet.append(row)

        # Adjust column widths based on the content
        for column_cells in sheet.columns:
            max_length = 0
            column = column_cells[0].column_letter  # Get the column name
            for cell in column_cells:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            sheet.column_dimensions[column].width = adjusted_width

        df = f"{download_excel_path}{filename}.xlsx"
        workbook.save(df)

        return Response(status=201)
    except Exception as e:
        return Response(status=404)