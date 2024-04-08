FROM python:3.13-rc-slim
WORKDIR /usr/onereport
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt /usr/onereport/requirements.txt
RUN pip install -r requirements.txt
COPY . /usr/onereport/
RUN mkdir -p /usr/onereport/log