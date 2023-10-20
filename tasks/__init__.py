import celeryconfig
from celery import Celery

celery = Celery('pdftoexcel.tasks')
celery.config_from_object(celeryconfig)
