import os
import logging
from celery import Celery
from config import Config

logger = logging.getLogger(__name__)

celery = Celery('pdftoexcel.tasks')


@celery.task
def delete_files_in_folder():
    for filename in os.listdir(Config.EXCEL_FILE_PATH):
        file_path = os.path.join(Config.EXCEL_FILE_PATH, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                logger.error(f'"<<<<<<<<<< Deleted file >>>>>>>>>> {file_path}')
            except Exception as e:
                logger.error(f'"<<<<<<<<<< Error deleting file >>>>>>>>>> {file_path} - {str(e)}')
