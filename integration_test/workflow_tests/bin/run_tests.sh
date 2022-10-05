#!/bin/bash
## =============================================================================
## NAME: run_tests.sh
##
##
## DESCRIPTION
## -----------------------------------------------------------------------------
## Tests the runs the integration tests.
##
##
## USAGE
## -----------------------------------------------------------------------------
## bin/run_tests.sh
##
## This must be called from the (root) directory /workflow_tests
## =============================================================================

## Set this for Debugging only
#set -ex

## Make sure we are calling the script the correct way.
BASEDIR=$(dirname $0)
if [ "$BASEDIR" != "bin" ]; then
  >&2 echo "ERROR: This script must be called from the root directory of workflow_tests[bin/run_tests.sh]."
  exit 1
fi


source ../../bin/common/check_returncode.sh


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
pip install -q -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
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
    *.py test_packages

echo "INFO: Formatting with black ..."
black *.py test_packages


echo "INFO: Checking lint rules ..."
flake8 \
    --max-line-length 99 \
    *.py
check_returncode $? "ERROR: Linting issues found."


## Run code smell and security tests using bandit
echo "INFO: Running code smell security tests ..."
bandit -r *.py test_packages
check_returncode $? "ERROR: Potential security or code issues found."


## Check code third party libraries for CVE issues
echo "INFO: Running checks on third party libraries ..."
safety check -r requirements.txt
check_returncode $? "ERROR: Potential security issues third party libraries."


## Run tests
echo "INFO: Running integration tests ..."

python run_tests.py
check_returncode $? "ERROR: Unit tests encountered failures."


## Deactivate and remove the virtual env
echo "INFO: Cleaning up the environment ..."
rm -rf venv
find . -type d -name "__pycache__" -exec rm -rf {} +

exit 0
