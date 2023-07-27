import json
import time
import datetime
import boto3
import PyPDF2
from flask import Flask, render_template, request

app = Flask(__name__)
app.debug = True

AWS_S3_BUCKET = 'pdftoexcel'
AWS_S3_DOMAIN = 'https://ss-pdftoexcel.s3.ap-south-1.amazonaws.com'
AWS_ACCESS_KEY_ID = 'AKIA3VHINVSYSOGK5OTY'
AWS_SECRET_ACCESS_KEY = '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'
AWS_REGION = 'ap-south-1'

@app.route('/')
def home():
    return render_template('pdftoexcel.html')

@app.route('/default/pdftoexcel', methods=('GET', 'POST'))
def pdftoexcel():
    if request.method == 'POST':
        file = request.form['file']
        filename = request.form['filename']
        with open(file, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text_content = ""
            for page in pdf_reader.pages:
                lines = page.extract_text().split("\n")
                for line in lines:
                    text_content += line + "\n"
            s3 = boto3.resource(
                's3',
                region_name=AWS_REGION,
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
            time_stamp = time.time()
            current_date = datetime.datetime.now()
            key = "{}{}/{}_{}, hope you're well!".format(current_date.year, current_date.month, str(time_stamp), filename)
            s3.Object(AWS_S3_BUCKET, key).put(Body=text_content)
            return {
                'statusCode': 200,
                'excel_file': '{}/{}'.format(AWS_S3_DOMAIN, key),
                'body': json.dumps('File converted successfully.')
            }
    else:
        return {
            'statusCode': 400,
            'body': json.dumps('Get method not allowed.')
        }