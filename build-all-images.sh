#! /bin/bash
docker build -f gateway.dockerfile . -t jyguru/biked-integration-gateway:12oct2023
docker build -f service-resources.dockerfile . -t jyguru/biked-integration-resources-image:12oct2023
docker build -f service.dockerfile . -t jyguru/biked-integration-beta:12oct2023