#!/bin/bash
## =============================================================================
## NAME: run_tests.sh
##
##
## DESCRIPTION
## -----------------------------------------------------------------------------
## Tests the lambda (task) for request_status_for_job using unit tests.
##
##
## USAGE
## -----------------------------------------------------------------------------
## bin/run_tests.sh
##
## This must be called from the (root) lambda directory /tasks/request_status_for_job
## =============================================================================

## Set this for Debugging only
#set -ex

## Make sure we are calling the script the correct way.
BASEDIR=$(dirname $0)
if [ "$BASEDIR" != "bin" ]; then
  >&2 echo "ERROR: This script must be called from the root directory of the task lambda [bin/run_tests.sh]."
  exit 1
fi


## FUNCTIONS
## -----------------------------------------------------------------------------
function check_rc () {
  ## Checks the return code of call and if not equal to 0, emits an error and
  ## exits the script with a failure.
  ##
  ## Args:
  ##   $1 - Return Code from command
  ##   $2 - Error message if failure occurs.

  let RC=$1
  MESSAGE=$2

  if [ $RC -ne 0 ]; then
      >&2 echo "$MESSAGE"
      deactivate
      exit 1
  fi
}


## MAIN
## -----------------------------------------------------------------------------
## Create the virtual env. Remove it if it exists.
echo "INFO: Creating virtual environment ..."
if [ -d venv ]; then
  rm -rf venv
  find . -type d -name "__pycache__" -exec rm -rf {} +
fi

python3 -m venv venv
source venv/bin/activate

## Install the requirements
pip install -q --upgrade pip
pip install -q -r requirements-dev.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
let return_code=$?

check_rc $return_code "ERROR: pip install encountered an error."


## Run unit tests and check Coverage
echo "INFO: Running unit and coverage tests ..."

# Currently just running unit tests until we fix/support large tests
coverage run --source request_status_for_job -m pytest
let return_code=$?
check_rc $return_code "ERROR: Unit tests encountered failures."

# Unit tests expected to cover minimum of 80%.
coverage report --fail-under=80
let return_code=$?
check_rc $return_code "ERROR: Unit tests coverage is less than 80%"

## Deactivate and remove the virtual env
echo "INFO: Cleaning up the environment ..."
deactivate
rm -rf venv
find . -type d -name "__pycache__" -exec rm -rf {} +

exit 0

