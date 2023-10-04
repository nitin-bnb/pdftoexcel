import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
from convertor import convert

load_dotenv()

app = Flask(__name__)

app.config.from_object('config.Config')

upload_folder = app.config['PDF_FILE_PATH']
Download_folder = app.config['EXCEL_FILE_PATH']

@app.route('/')
def home():
    return render_template('pdftoexcel.html')

@app.route('/default/pdftoexcel', methods=('GET', 'POST'))
def pdftoexcel():
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            file_path = os.path.join(upload_folder, file.filename)
            file.save(file_path)
            filename = file.filename.replace('.pdf', '')
            result =  convert(file_path, filename)

        if result.status_code == 201 :
            return f"{filename}"
        else:
            return "Failed to Convert file to Excel"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)