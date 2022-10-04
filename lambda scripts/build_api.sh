#!/bin/bash
## =============================================================================
## NAME: build_api.sh
##
##
## DESCRIPTION
## -----------------------------------------------------------------------------
## Builds the lambda_name API documentation.
##
##
## USAGE
## -----------------------------------------------------------------------------
## bin/build_api.sh
##
## This must be called from the (root) lambda directory /tasks/lambda_name
## =============================================================================

## Set this for Debugging only
#set -ex

## Make sure we are calling the script the correct way.
BASEDIR=$(dirname $0)
if [ "$BASEDIR" != "bin" ]; then
  >&2 echo "ERROR: This script must be called from the root directory lambda_name [bin/build_api.sh]."
  exit 1
fi


source ../../bin/check_returncode.sh


## MAIN
## -----------------------------------------------------------------------------
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
pip install -q "pydoc-markdown>=4.0.0,<5.0.0" --trusted-host pypi.org --trusted-host files.pythonhosted.org
check_returncode $? "ERROR: pip install encountered an error."

## Run the documentation command
echo "INFO: Creating API documentation ..."
pydoc-markdown -I . -m lambda_name --render-toc > API.md
check_returncode $? "ERROR: Failed to create API.md file."

## Perform cleanup
echo "INFO: Cleaning up environment ..."
rm -rf venv
find . -type d -name "__pycache__" -exec rm -rf {} +

exit 0
