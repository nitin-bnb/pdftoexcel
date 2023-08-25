### Python

version 3.9

### pyenv

pyenv virtualenv 3.9.0 pdftoexcel

### setup

- git clone https://nitin-bnb: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@github.com/nitin-bnb/pdftoexcel.git
- pip install -r requirements.txt
- FLASK_APP=pdftoexcel FLASK_ENV=development FLASK_DEBUG=1 flask run

### server

chmod 400 /Users/nitin/.ssh/bnb-ec2.pem

ssh -i /Users/nitin/.ssh/bnb-ec2.pem ec2-user@3.84.246.34

cd /srv/projects/pdftoexcel
source ~/.bashrc
pyenv activate pdftoexcel

uwsgi --socket 0.0.0.0:5000 --protocol=http -w wsgi:app &

http://ec2-3-84-246-34.compute-1.amazonaws.com:5000/

### deploy

- python -m pip freeze > requirements.txt

- zip -r pdftoexcel.zip /Users/nitin/.pyenv/versions/3.9.0/envs/pdftoexcel/lib/python3.9/site-packages

- zip pdftoexcel.zip lambda_function.py

aws lambda list-functions

aws lambda update-function-code --function-name pdftoexcel --zip-file fileb://pdftoexcel.zip

### Gateway backend URL

https://7dvn2mrkf9.execute-api.ap-south-1.amazonaws.com/default/pdftoexcel

### aws lambda

cd /Users/nitin/.pyenv/versions/3.9.0/envs/pdftoexcel/lib/python3.9/site-packages
aws lambda publish-layer-version --layer-name pdftoexcel --zip-file fileb://pdftoexcel.zip --compatible-runtimes python3.9
