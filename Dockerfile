FROM python:3.6-alpine3.6
FROM centos

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .


CMD [ "python", "./app.py" ]
