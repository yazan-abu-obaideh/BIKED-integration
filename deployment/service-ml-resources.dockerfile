# syntax=docker/dockerfile:1
FROM python:3.10-slim
WORKDIR /app
RUN apt-get update -y && apt install curl libgomp1 -y
COPY service_resources/ service_resources/
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt