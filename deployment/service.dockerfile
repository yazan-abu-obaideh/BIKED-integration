# syntax=docker/dockerfile:1
FROM jyguru/biked-integration-service-resources:2023oct16
WORKDIR /app

COPY service/ service/
COPY test.sh test.sh
COPY run.sh run.sh

HEALTHCHECK CMD curl --fail localhost:80/health || exit 1
ENTRYPOINT ["/bin/sh", "./run.sh"]