# syntax=docker/dockerfile:1
FROM python:3.10-slim
WORKDIR /app
RUN apt-get update -y && apt-get upgrade -y && apt-get install libgomp1 -y
COPY service_resources/ service_resources/
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN apt install curl -y

COPY service/ service/
COPY test.sh test.sh
COPY run.sh run.sh

HEALTHCHECK CMD curl --fail localhost:80/health || exit 1
ENTRYPOINT ["/bin/sh", "./run.sh"]