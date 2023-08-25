#! /bin/bash
docker build -f gateway.dockerfile . -t jyguru/biked-integration-gateway:25aug2023
docker build -f service-resources.dockerfile . -t jyguru/biked-integration-resources-image:25aug2023
docker build -f service.dockerfile . -t jyguru/biked-integration-beta:25aug2023