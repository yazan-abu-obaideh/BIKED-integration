# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt-get update -y && apt-get upgrade -y && apt-get install libgomp1 -y
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "main.py"]