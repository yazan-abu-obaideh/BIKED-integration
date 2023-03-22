#! /bin/bash
echo "Running resources tests..."
python -m unittest discover -s service_resources -t service_resources
echo "Running unit tests"
python -m unittest discover -s src/test -t src/test
echo "Running e2e tests"
python -m unittest discover -s src/app_tests -t src/app_tests
