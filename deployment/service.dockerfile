# syntax=docker/dockerfile:1
FROM jyguru/biked-integration-service-resources:2024jan21
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY service/ service/
COPY test.sh .
COPY run.sh .

HEALTHCHECK CMD curl --fail localhost:80/health || exit 1
ENTRYPOINT ["/bin/sh", "./run.sh"]