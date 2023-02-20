# syntax=docker/dockerfile:1
FROM jyguru/biked-integration:resources-image

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt-get update -y && apt-get upgrade -y && apt-get install libgomp1 -y
RUN pip3 install -r requirements.txt
COPY . .

CMD [ "python3", "main-production.py"]