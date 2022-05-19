FROM python:3
USER root
ENV PYTHONIOENCODING utf-8

RUN apt-get update
RUN mkdir /app/
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app/
