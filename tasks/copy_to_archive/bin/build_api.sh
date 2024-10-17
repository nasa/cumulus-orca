#!/bin/bash
## =============================================================================
## NAME: build_api.sh
##
##
## DESCRIPTION
## -----------------------------------------------------------------------------
## Builds the copy_to_archive API documentation.
##
##
## USAGE
## -----------------------------------------------------------------------------
## bin/build_api.sh
##
## This must be called from the (root) lambda directory /tasks/copy_to_archive
## =============================================================================

## Set this for Debugging only
#set -ex

## Make sure we are calling the script the correct way.
BASEDIR=$(dirname $0)
if [ "$BASEDIR" != "bin" ]; then
  >&2 echo "ERROR: This script must be called from the root directory copy_to_archive [bin/build_api.sh]."
  exit 1
fi


source ../../bin/common/check_returncode.sh
source ../../bin/common/venv_management.sh


## MAIN
## -----------------------------------------------------------------------------
run_and_check_returncode "create_and_activate_venv"
trap 'deactivate_and_delete_venv' EXIT
run_and_check_returncode "pip install -q --upgrade pip==24.2 --trusted-host pypi.org --trusted-host files.pythonhosted.org"

## Install the requirements
pip install -q "pydoc-markdown>=4.0.0,<5.0.0" --trusted-host pypi.org --trusted-host files.pythonhosted.org
check_returncode $? "ERROR: pip install encountered an error."

## Run the documentation command
echo "INFO: Creating API documentation ..."
pydoc-markdown -I . -m copy_to_archive -m sqs_library --render-toc > API.md
check_returncode $? "ERROR: Failed to create API.md file."
