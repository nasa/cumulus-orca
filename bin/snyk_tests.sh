#!/bin/bash
## =============================================================================
## NAME: snyk_tests.sh
##
##
## DESCRIPTION
## -----------------------------------------------------------------------------
## Scans the ORCA project with snyk for vulnerabilities.
## Install snyk in Mac using:
## brew tap snyk/tap
## brew install snyk
##
## Run "pip install -r requirements-dev.txt" before running snyk test in order to install all packages first.
##
## ENVIRONMENT SETTINGS
## -----------------------------------------------------------------------------
## SNYK_AUTHENTICATION_TOKEN (str) - snyk authentication token found from Snyk UI browser https://app.snyk.io/account.
## export locally first using:
## export SNYK_AUTHENTICATION_TOKEN=<YOUR_TOKEN>
## -----------------------------------------------------------------------------

source bin/common/check_returncode.sh

# authenticate snyk CLI locally
run_and_check_returncode "snyk auth $SNYK_AUTHENTICATION_TOKEN"

# Scan orca website
echo "Scanning open-source code with Snyk for potential vulnerabilities..."
cd website
snyk test -d --severity-threshold=high || true
cd -

function run_snyk_tests_lambda() {
  echo
  echo "Running snyk test in $1"
  echo

  cd $1
  # remove shared library from the requirement files since snyk cannot scan through it
  grep -v '../../shared_libraries' requirements-dev.txt >> test-requirements-dev.txt
  grep -v '../../shared_libraries' requirements.txt >> test-requirements.txt
  snyk test --severity-threshold=high --file=test-requirements-dev.txt --package-manager=pip || true
  snyk test --severity-threshold=high --file=test-requirements.txt --package-manager=pip || true
  # remove test files
  rm test-requirements*.txt
}
export -f run_snyk_tests_lambda

function run_snyk_tests_others() {
  echo
  echo "Running snyk test in $1"
  echo
  cd $1
  # remove shared library from the requirement files since snyk cannot scan through it
  grep -v '../shared_libraries' requirements-dev.txt >> test-requirements-dev.txt
  grep -v '../shared_libraries' requirements.txt >> test-requirements.txt
  snyk test --severity-threshold=high --file=test-requirements-dev.txt --package-manager=pip || true
  snyk test --severity-threshold=high --file=test-requirements.txt --package-manager=pip || true
  # remove test files
  rm test-requirements*.txt
}
export -f run_snyk_tests_others

other_dirs="shared_libraries graphql"
lambda_task_dirs=$(ls -d tasks/*)

# Run snyk for other directories
parallel --jobs 0 -n 1 -X --halt now,fail=1 run_snyk_tests_others ::: $other_dirs

# Call each task's snyk test suite
echo "Running snyk for lambdas"
echo $pwd
parallel --jobs 0 -n 1 -X --halt now,fail=1 run_snyk_tests_lambda ::: $lambda_task_dirs