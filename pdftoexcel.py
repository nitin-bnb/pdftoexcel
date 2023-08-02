import json
import time
import datetime
import boto3
import tabula
import pandas as pd
from flask import Flask, render_template, request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create the Flask app
app = Flask(__name__)
app.debug = True

# Load configuration from config.py
app.config.from_object('config.Config')

s3 = boto3.resource(
        's3',
        region_name=app.config['AWS_REGION'],
        aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY']
    )


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

def convert(file, filename):

    data = tabula.read_pdf(file, stream=True, guess=True, pages='all', multiple_tables=True, pandas_options={'header': None})
    if data:
        
        # Add column names to the DataFrame
        if filename == "Natwest":
            df = readandcleandata(data)
            df.columns = ['Date', 'Narrative', 'Type', 'Debit', 'Credit', 'Ledger Balance']
            
        elif filename == "LLoyds Bank":
            df.columns = ['Date', 'Activity', 'Paid Out', 'Paid In', 'Balance']
        elif filename == "LLoyds Bank 2":
            df = readandcleandata(data)
            df.columns = ['Date', 'Description', 'Type','Paid In', 'Paid Out', 'Balance']
        elif filename == "HSBC":
            df.columns = ['Date', 'Description', 'Paid In', 'Paid Out', 'Balance']
        else:
            df = pd.concat(data, ignore_index=True)
            df.columns = ['Date', 'Description', 'Paid In', 'Paid Out', 'Balance']

        with pd.ExcelWriter(f"{filename}.xlsx", engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=f"{filename}", index=False)

            # Get the openpyxl workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets[f"{filename}"]

            # Iterate through each column and set the optimal width
            for column_cells in worksheet.columns:
                length = max(len(str(cell.value)) for cell in column_cells)
                worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2

    #     time_stamp = time.time()
    #     current_date = datetime.datetime.now()
    #     key = "{}{}/{}_{}, hope you're well!".format(current_date.year, current_date.month, str(time_stamp), filename)
    #     s3.Object(app.config['AWS_S3_BUCKET'], key).put(Body=open(filename, 'rb'))
    #     return {
    #         'statusCode': 200,
    #         'excel_file': '{}/{}'.format(app.config['AWS_S3_BUCKET'], key),
    #         'body': json.dumps('File converted successfully.')
    #     }
    # else:
    #     return {
    #         'statusCode': 400,
    #         'body': json.dumps('Failed to read PDF')
    #     }
    return ''


@app.route('/')
def home():
    return render_template('pdftoexcel.html')

@app.route('/default/pdftoexcel', methods=('GET', 'POST'))
def pdftoexcel():
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            filename = file.filename.replace('.pdf', '')
            converted_file = convert(file, filename)
            return converted_file
        else:
            return {
            'statusCode': 400,
            'body': json.dumps('Failed to read PDF')
        }
    else:
        return {
            'statusCode': 400,
            'body': json.dumps('Get method not allowed.')
        }