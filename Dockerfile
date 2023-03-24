# syntax=docker/dockerfile:1
FROM jyguru/biked-integration-resources-image:2023mar24

RUN apt install curl -y

WORKDIR /app
COPY src/ src/
COPY test.sh test.sh
COPY run.sh run.sh

HEALTHCHECK CMD curl --fail localhost:80/health || exit 1
ENTRYPOINT ["/bin/sh", "./run.sh"]