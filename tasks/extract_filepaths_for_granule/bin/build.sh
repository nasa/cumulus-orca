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


source ../../bin/common/check_returncode.sh

## MAIN
## -----------------------------------------------------------------------------
## Create the build directory. Remove it if it exists.
echo "INFO: Creating build directory ..."
if [ -d build ]; then
    rm -rf build
fi

mkdir build
check_returncode $? "ERROR: Failed to create build directory."

## Create the virtual env. Remove it if it already exists.
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
pip install -q -t build -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
check_returncode $? "ERROR: pip install encountered an error."

## Copy the lambda files to build
echo "INFO: Creating the Lambda package ..."
cp *.py build/
check_returncode $? "ERROR: Failed to copy lambda files to build directory."

## Copy the schema files to build
echo "INFO:  Copying the input, output and config schemas..."
cp -r schemas/ build/
check_returncode $? "ERROR: Failed to copy schema files to build directory."
## Create the zip archive
echo "INFO: Creating zip archive ..."
cd build
zip -qr ../extract_filepaths_for_granule.zip .
let return_code=$?
cd -

check_returncode $return_code "ERROR: Failed to create zip archive."

## Perform cleanup
echo "INFO: Cleaning up build ..."
rm -rf build
