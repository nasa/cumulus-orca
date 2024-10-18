#!/bin/bash
## =============================================================================
## NAME: build_doc.sh
##
##
## DESCRIPTION
## -----------------------------------------------------------------------------
## Builds the lambda (task) API documentation.
##
##
## USAGE
## -----------------------------------------------------------------------------
## bin/build_doc.sh
##
## This must be called from the (root) lambda directory /tasks/db_deploy
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
source ../../bin/common/venv_management.sh


## MAIN
## -----------------------------------------------------------------------------
run_and_check_returncode "create_and_activate_venv"
trap 'deactivate_and_delete_venv' EXIT
run_and_check_returncode "pip install -q --upgrade pip==24.2 --trusted-host pypi.org --trusted-host files.pythonhosted.org"

## Install the requirements
pip install -q pydoc-markdown==3.10.1 --trusted-host pypi.org --trusted-host files.pythonhosted.org
check_returncode $? "ERROR: pip install encountered an error."

## Get the modules we want to document
file_list=$(find . \
    -type d \
    \( -path ./test -o -path ./venv -o -path ./.vscode \) -prune \
    -o -type f \
    -name "*.py" \
    -print \
    | sed 's|^./||' \
    | sort)
module_list=""
first_time="1"
for file in $file_list
do
    module=${file%%".py"}
    if [ "${first_time}" = "1" ]; then
        module_list="-m ${module}"
        first_time="0"
    else
        module_list="${module_list} -m ${module}"
    fi
done

echo "INFO: Creating API markdown file ..."
## Run the documentation command
echo "INFO: Creating API documentation ..."
pydoc-markdown -I . ${module_list} --render-toc > API.md
check_returncode $? "ERROR: Failed to create API.md file."

## Perform cleanup
echo "INFO: Cleaning up environment ..."
