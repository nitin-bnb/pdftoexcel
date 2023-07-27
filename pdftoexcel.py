import json
import PyPDF2
from flask import Flask, render_template, request

app = Flask(__name__)
app.debug = True

@app.route('/')
def home():
    return render_template('pdftoexcel.html')

@app.route('/default/pdftoexcel', methods=('GET', 'POST'))
def pdftoexcel():
    if request.method == 'POST':
        file = request.form['file']
        with open(file, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text_content = ""
            for page in pdf_reader.pages:
                lines = page.extract_text().split("\n")
                for line in lines:
                    text_content += line + "\n"
        return {
            'statusCode': 200,
            'body': json.dumps('File converted successfully.')
        }
    else:
        return {
            'statusCode': 400,
            'body': json.dumps('Get method not allowed.')
        }