#!/bin/bash
## =============================================================================
## NAME: run_tests.sh
##
##
## DESCRIPTION
## -----------------------------------------------------------------------------
## Tests the shared library for shared_db using unit tests.
##
##
## USAGE
## -----------------------------------------------------------------------------
## bin/run_tests.sh
##
## This must be called from the (root) shared library directory
## tasks/shared_libraries
## =============================================================================

## Set this for Debugging only
#set -ex

## Make sure we are calling the script the correct way.
BASEDIR=$(dirname $0)
if [ "$BASEDIR" != "bin" ]; then
  >&2 echo "ERROR: This script must be called from the root directory of shared_libraries [bin/run_tests.sh]."
  exit 1
fi


source ../bin/common/check_returncode.sh
source ../bin/common/venv_management.sh


## MAIN
## -----------------------------------------------------------------------------
run_and_check_returncode "create_and_activate_venv"
trap 'deactivate_and_delete_venv' EXIT
run_and_check_returncode "pip install -q --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org"

## Install the requirements
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
    orca_shared


echo "INFO: Formatting with black ..."
black orca_shared


echo "INFO: Checking lint rules ..."
flake8 \
    --max-line-length 99 \
    --extend-ignore E203 \
    orca_shared
check_returncode $? "ERROR: Linting issues found."


## Run code smell and security tests using bandit
echo "INFO: Running code smell security tests ..."
bandit -r orca_shared
check_returncode $? "ERROR: Potential security or code issues found."


## Run unit tests and check Coverage
echo "INFO: Running unit and coverage tests ..."

# Export the AWS_REGION for the boto3 clients. Note that if you clear the
# environment for unit tests, you will need to add this environment variable back
# in to avoid a client error "botocore.exceptions.NoRegionError: You must specify
# a region." In real AWS, the AWS_REGION is set for you per the Lambda developer
# docs seen here https://docs.aws.amazon.com/lambda/latest/dg/lambda-dg.pdf
export AWS_REGION="us-west-2"

coverage run --source=orca_shared -m pytest
check_returncode $? "ERROR: Unit tests encountered failures."

# Unit tests expected to cover minimum of 80%.
coverage report --fail-under=80
check_returncode $? "ERROR: Unit tests coverage is less than 80%"
