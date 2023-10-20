import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
from convertor import convert
from celery import Celery

load_dotenv()

app = Flask(__name__)

app.config.from_object('config.Config')

upload_folder = app.config['PDF_FILE_PATH']
download_folder = app.config['EXCEL_FILE_PATH']


@app.route('/')
def home():
    return render_template('pdftoexcel.html')


@app.route('/default/pdftoexcel', methods=['GET', 'POST'])
def pdftoexcel():
    filename = None

    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            file_path = os.path.join(upload_folder, file.filename)
            file.save(file_path)
            filename = file.filename.replace('.pdf', '')
            result = convert(file_path, filename)

            if result.status_code == 201:
                return f"{filename}"

    if filename:
        return "Failed to Convert file to Excel"
    else:
        return "No file uploaded"


def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        include=['tasks.tasks']
    )
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask

    return celery


celery = make_celery(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
