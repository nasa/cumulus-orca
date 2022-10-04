#!/bin/bash
## =============================================================================
## NAME: run_tests.sh
##
##
## DESCRIPTION
## -----------------------------------------------------------------------------
## Tests the lambda (task) for post_to_catalog using unit tests.
##
##
## USAGE
## -----------------------------------------------------------------------------
## bin/run_tests.sh
##
## This must be called from the (root) lambda directory /tasks/post_to_catalog
## =============================================================================

## Set this for Debugging only
#set -ex

## Make sure we are calling the script the correct way.
BASEDIR=$(dirname $0)
if [ "$BASEDIR" != "bin" ]; then
  >&2 echo "ERROR: This script must be called from the root directory of the task lambda [bin/run_tests.sh]."
  exit 1
fi


source ../../bin/check_returncode.sh


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
trap 'deactivate' EXIT

## Install the requirements
pip install -q --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org
pip install -q -r requirements-dev.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
check_returncode $? "ERROR: pip install encountered an error."

## Check code formatting and styling
echo "INFO: Checking formatting and style of code ..."
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


echo "INFO: Checking lint rules ..."
flake8 \
    --max-line-length 99 \
    *.py test
check_returncode $? "ERROR: Linting issues found."


## Run code smell and security tests using bandit
echo "INFO: Running code smell security tests ..."
bandit -r *.py test
check_returncode $? "ERROR: Potential security or code issues found."


## Check code third party libraries for CVE issues
echo "INFO: Running checks on third party libraries ..."
safety check -r requirements.txt -r requirements-dev.txt
check_returncode $? "ERROR: Potential security issues third party libraries."


## Run unit tests and check Coverage
echo "INFO: Running unit and coverage tests ..."

# Currently just running unit tests until we fix/support large tests
coverage run --source=post_to_catalog -m pytest
check_returncode $? "ERROR: Unit tests encountered failures."

# Unit tests expected to cover minimum of 80%.
coverage report --fail-under=80
check_returncode $? "ERROR: Unit tests coverage is less than 80%"


## Deactivate and remove the virtual env
echo "INFO: Cleaning up the environment ..."
rm -rf venv
find . -type d -name "__pycache__" -exec rm -rf {} +

exit 0
