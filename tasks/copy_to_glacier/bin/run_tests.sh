#!/bin/bash
## =============================================================================
## NAME: run_tests.sh
##
##
## DESCRIPTION
## -----------------------------------------------------------------------------
## Tests the lambda (task) for copy_to_glacier using unit tests.
##
##
## USAGE
## -----------------------------------------------------------------------------
## bin/run_tests.sh
##
## This must be called from the (root) lambda directory /tasks/copy_to_glacier
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
pip install -q --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org
pip install -q -r requirements-dev.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
let return_code=$?

check_rc $return_code "ERROR: pip install encountered an error."


## Check code formatting and styling
echo "INFO: Checking formatting and style of code ..."
echo "INFO: Checking lint rules ..."
flake8 \
    --max-line-length 99 \
    *.py test
check_rc $return_code "ERROR: Linting issues found."

echo "INFO: Sorting imports ..."
isort \
    --trailing-comma \
    --ensure-newline-before-comments \
    --line-length 88 \
    --use-parentheses \
    --force-grid-wrap 0 \
    -m 3 \
    *.py test

echo "INFO: Formatting with black ..."
black *.py test


## Run code smell and security tests using bandit
echo "INFO: Running code smell security tests ..."
bandit -r copy_to_glacier.py test
let return_code=$?
check_rc $return_code "ERROR: Potential security or code issues found."


## Check code third party libraries for CVE issues
echo "INFO: Running checks on third party libraries ..."
safety check -r requirements.txt -r requirements-dev.txt
let return_code=$?
check_rc $return_code "ERROR: Potential security issues third party libraries."


## Run unit tests and check Coverage
echo "INFO: Running unit and coverage tests ..."

# Currently just running unit tests until we fix/support large tests
coverage run --source=copy_to_glacier -m pytest
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
