#!/bin/bash
## =============================================================================
## NAME: run_tests.sh
##
##
## DESCRIPTION
## -----------------------------------------------------------------------------
## Tests the shared library for SQS queue using unit tests.
##
##
## USAGE
## -----------------------------------------------------------------------------
## shared_libraries/run_tests.sh
##
## This must be called from the directory /tasks/shared_libraries
## =============================================================================

## Set this for Debugging only
#set -ex

# Make sure we are calling the script the correct way.
BASEDIR=$(dirname $0)
if [ "$BASEDIR" != "bin" ]; then
  >&2 echo "ERROR: This script must be called from [bin]."
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
echo "Installing necessary requirement packages.........."
pip install -q --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org
pip install -q -r requirements-dev.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
let return_code=$?

check_rc $return_code "ERROR: pip install encountered an error."

## Copy shared libraries
echo "INFO: Copying ORCA shared libraries ..."
if [ -d orca_shared ]; then
    rm -rf orca_shared
fi

mkdir orca_shared
let return_code=$?
check_rc $return_code "ERROR: Unable to create orca_shared directory."

touch orca_shared/__init__.py
let return_code=$?
check_rc $return_code "ERROR: Unable to create [orca_shared/__init__.py] file"

cp ../shared_libraries/database/shared_recovery.py orca_shared/
let return_code=$?
check_rc $return_code "ERROR: Unable to copy shared library [orca_shared/shared_recovery.py]"

## Run unit tests and check Coverage
echo "INFO: Running unit and coverage tests ....................."

# Currently just running unit tests until we fix/support large tests
coverage run --source shared_recovery -m pytest
let return_code=$?
check_rc $return_code "ERROR: Unit tests encountered failures."

# Unit tests expected to cover minimum of 80%.
coverage report --fail-under=80
let return_code=$?
check_rc $return_code "ERROR: Unit tests coverage is less than 80%"

# Cleanup shared libraries
rm -rf orca_shared

## Deactivate and remove the virtual env
echo "INFO: Cleaning up the environment ..."
deactivate
rm -rf venv
find . -type d -name "__pycache__" -exec rm -rf {} +

echo "INFO: Unit testing complete."
exit 0
