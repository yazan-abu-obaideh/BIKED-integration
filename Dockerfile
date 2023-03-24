# syntax=docker/dockerfile:1
FROM jyguru/biked-integration-resources-image:2023mar24
WORKDIR /app
COPY src/ src/
COPY test.sh test.sh
COPY run.sh run.sh