### Python

version 3.9

### pyenv

pyenv virtualenv 3.9.0 pdftoexcel

### setup

- git clone https://nitin-bnb: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@github.com/nitin-bnb/pdftoexcel.git
- pip install -r requirements.txt
- FLASK_APP=pdftoexcel FLASK_ENV=development FLASK_DEBUG=1 flask run

### deploy

- python -m pip freeze > requirements.txt

- zip -r pdftoexcel.zip /Users/nitin/.pyenv/versions/3.9.0/envs/pdftoexcel/lib/python3.9/site-packages

- zip pdftoexcel.zip lambda_function.py

aws configure

export AWS_ACCESS_KEY_ID=AKIA3VHINVSYSOGK5OTY
export AWS_SECRET_ACCESS_KEY=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
export AWS_REGION=ap-south-1

aws lambda list-functions

aws lambda update-function-code --function-name pdftoexcel --zip-file fileb://pdftoexcel.zip

### Gateway backend URL

https://7dvn2mrkf9.execute-api.ap-south-1.amazonaws.com/default/pdftoexcel

### aws lambda

cd /Users/nitin/.pyenv/versions/3.9.0/envs/pdftoexcel/lib/python3.9/site-packages
aws lambda publish-layer-version --layer-name pdftoexcel --zip-file fileb://pdftoexcel.zip --compatible-runtimes python3.9
