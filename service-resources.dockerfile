# syntax=docker/dockerfile:1
FROM python:3.10-slim
WORKDIR /app
RUN apt-get update -y && apt-get upgrade -y && apt-get install libgomp1 -y
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY service_resources/ service_resources/
