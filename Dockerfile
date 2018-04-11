FROM python:stretch
COPY requirements.txt grantload/ /usr/src/grantload/ 
WORKDIR /usr/src/grantload
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["python", "load_grant_data_from_file.py"]
