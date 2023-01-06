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
## ENVIRONMENT SETTINGS
## -----------------------------------------------------------------------------
## SNYK_AUTHENTICATION_TOKEN (str) - snyk authentication token found from Snyk UI browser https://app.snyk.io/account.
## export locally first using:
## export SNYK_AUTHENTICATION_TOKEN=<YOUR_TOKEN>
## -----------------------------------------------------------------------------

source bin/common/check_returncode.sh

# authenticate snyk CLI locally
run_and_check_returncode "snyk auth $SNYK_AUTHENTICATION_TOKEN"

# Iac run limited to 20 runs a month. TBD Discuss with Jon Velapondi.
# echo "Scanning Infrastructure as code with Snyk for potential vulnerabilities..."
# snyk iac test || true

# scan orca website
echo "Scanning open-source code with Snyk for potential vulnerabilities..."
cd website
snyk test -d --severity-threshold=high || true
cd -

function run_snyk_tests() {
  echo
  echo "Running tests in $1"
  echo

  cd $1
  snyk test --severity-threshold=high || true
  return_code=$?
}
export -f run_snyk_tests

task_dirs=$(ls -d tasks/* | egrep -v "package")

## Call each task's testing suite
echo "Running snyk for lambdas"
echo $pwd
parallel --jobs 0 -n 1 -X --halt now,fail=1 run_snyk_tests ::: $task_dirs
