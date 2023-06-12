#! /bin/bash
echo "Running resources tests..."
python -m unittest discover -s service_resources -t service_resources
echo "Running unit tests..."
python -m unittest discover -s service/test -t service/test
echo "Running e2e tests..."
python -m unittest discover -s service/app_tests -t service/app_tests
