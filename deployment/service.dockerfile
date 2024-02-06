# syntax=docker/dockerfile:1
FROM jyguru/biked-integration-service-resources:2023oct16 as modelImage

FROM python:3.10-slim
WORKDIR /app
RUN apt-get update -y && apt install curl libgomp1 -y
COPY --from=modelImage /app/service_resources /app/service_resources
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY service/ service/
COPY test.sh .
COPY run.sh .

HEALTHCHECK CMD curl --fail localhost:80/health || exit 1
ENTRYPOINT ["/bin/sh", "./run.sh"]