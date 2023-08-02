import os

class Config:

    # AWS credentials
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', 'AKIA3VHINVSYSOGK5OTY')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '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')
    AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET', 'pdftoexcel')
    AWS_S3_DOMAIN = os.environ.get('AWS_S3_DOMAIN', 'https://ss-pdftoexcel.s3.ap-south-1.amazonaws.com')
    AWS_REGION = os.environ.get('AWS_REGION', 'ap-south-1')