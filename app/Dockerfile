FROM python:3.7-slim
MAINTAINER Maaz Bin Tahir Saeed

ENV PYTHONUNBUFFERED 1

COPY ./requirements-docker.txt /requirements.txt

RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY . /app
