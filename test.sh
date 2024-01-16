#!/bin/bash

run_tests() {
    echo "Running $1 tests..."
    python -m unittest discover -s $2 -t $2 || exit 1
}

run_tests "resources" "service_resources"
run_tests "unit" "service/test"
run_tests "e2e" "service/app_tests"
