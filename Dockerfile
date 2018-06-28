FROM docker.io/centos/python-36-centos7:latest

#COPY requirements.txt ./
#RUN pip install --no-cache-dir -r requirements.txt
#COPY . .
ADD app.py /
ADD requirements.txt /
RUN pip install -r /requirements.txt

CMD [ "python", "/app.py" ]
