# import boto3
import os
from flask import Flask, render_template, request, send_file
from dotenv import load_dotenv
from convertor import convert

load_dotenv()

app = Flask(__name__)

app.config.from_object('config.Config')

# s3 = boto3.resource(
#         's3',
#         region_name=app.config['AWS_REGION'],
#         aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
#         aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY']
#     )

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