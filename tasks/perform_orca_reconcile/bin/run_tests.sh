#!/bin/bash
## =============================================================================
## NAME: run_tests.sh
##
##
## DESCRIPTION
## -----------------------------------------------------------------------------
## Tests the lambda (task) for perform_orca_reconcile using unit tests.
##
##
## USAGE
## -----------------------------------------------------------------------------
## bin/run_tests.sh
##
## This must be called from the (root) lambda directory /tasks/perform_orca_reconcile
## =============================================================================

## Set this for Debugging only
#set -ex

## Make sure we are calling the script the correct way.
BASEDIR=$(dirname $0)
if [ "$BASEDIR" != "bin" ]; then
  >&2 echo "ERROR: This script must be called from the root directory of the task lambda [bin/run_tests.sh]."
  exit 1
fi


source ../../bin/common/check_returncode.sh
source ../../bin/common/venv_management.sh


## MAIN
## -----------------------------------------------------------------------------
run_and_check_returncode "create_and_activate_venv"
trap 'deactivate_and_delete_venv' EXIT
run_and_check_returncode "pip install -q --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org"

## Install the requirements
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


## Run unit tests and check Coverage
echo "INFO: Running unit and coverage tests ..."

# Currently just running unit tests until we fix/support large tests
coverage run --source perform_orca_reconcile -m pytest
check_returncode $? "ERROR: Unit tests encountered failures."

# Unit tests expected to cover minimum of 80%.
coverage report --fail-under=80
check_returncode $? "ERROR: Unit tests coverage is less than 80%"
