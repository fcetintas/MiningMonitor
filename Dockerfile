FROM python:3.7.0-stretch

MAINTAINER Furkan Cetintas

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN python3 -m pip install -r /requirements.txt

RUN mkdir app
WORKDIR /app
COPY ./app /app
