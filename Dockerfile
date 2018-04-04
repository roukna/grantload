FROM python:2.7-stretch
COPY requirements.txt UF_Grant.csv grantload/ /usr/src/grantload/ 
WORKDIR /usr/src/grantload
RUN pip install --no-cache-dir -r requirements.txt
RUN cd grantload
CMD ["load_grant_data_from_file.py", "../config.yaml", "../UF_Grant.csv"] 
