# syntax=docker/dockerfile:1
FROM jyguru/biked-integration-resources-image:2023mar22
WORKDIR /app
COPY src/ src/
COPY test.sh test.sh