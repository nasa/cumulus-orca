#!/bin/bash
## =============================================================================
## NAME: build.sh
##
##
## DESCRIPTION
## -----------------------------------------------------------------------------
## Builds the zip file for extract_filepaths_for_granule lambda function.
##
##
## USAGE
## -----------------------------------------------------------------------------
## bin/build.sh
##
## This must be called from the (root) lambda directory /tasks/post_copy_request_to_queue
## =============================================================================

## Set this for Debugging only
#set -ex

## Make sure we are calling the script the correct way.
BASEDIR=$(dirname $0)
if [ "$BASEDIR" != "bin" ]; then
  >&2 echo "ERROR: This script must be called from the root directory of the task lambda [bin/build.sh]."
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
## Create the build directory. Remove it if it exists.
echo "INFO: Creating build directory ..."
if [ -d build ]; then
    rm -rf build
fi

mkdir build
let return_code=$?

check_rc $return_code "ERROR: Failed to create build directory."

## Create the virtual env. Remove it if it already exists.
echo "INFO: Creating virtual environment ..."
if [ -d venv ]; then
  rm -rf venv
  find . -type d -name "__pycache__" -exec rm -rf {} +
fi

python3 -m venv venv
source venv/bin/activate

## Install the requirements
pip install -q --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org
pip install -q -t build -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
let return_code=$?

check_rc $return_code "ERROR: pip install encountered an error."

## Copy the lambda files to build
echo "INFO: Creating the Lambda package ..."
cp *.py build/
let return_code=$?

check_rc $return_code "ERROR: Failed to copy lambda files to build directory."

## Copy the schema files to build
mkdir -p build/schemas
let return_code=$?
check_rc $return_code "ERROR: Unable to create build/schemas directory."
echo "INFO:  Copying the input, output and config schemas..."
cp -r schemas/ build/schemas/
let return_code=$?

check_rc $return_code "ERROR: Failed to copy schema files to build directory."
## Create the zip archive
cd build
zip -qr ../extract_filepaths_for_granule.zip .
let return_code=$?
cd -

check_rc $return_code "ERROR: Failed to create zip archive."

## Perform cleanup
echo "INFO: Cleaning up build ..."
deactivate
rm -rf build

exit 0