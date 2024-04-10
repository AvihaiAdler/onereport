FROM python:3.11-slim
WORKDIR /usr/onereport
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
COPY . /usr/onereport/
RUN mkdir -p /usr/onereport/log
RUN pip install -r requirements.txt --no-cache
