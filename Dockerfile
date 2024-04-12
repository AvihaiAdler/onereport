FROM python:3.11-slim
WORKDIR /usr/onereport
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
RUN mkdir -p /usr/onereport/log
# give docker the chance to use the cached layer of dependencies
COPY ./onereport/requirements.txt /usr/onereport/requirements.txt 
RUN pip install -r requirements.txt
# copy the rest of the files
COPY . /usr/onereport/
