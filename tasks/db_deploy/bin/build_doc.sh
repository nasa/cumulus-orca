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
#set -x

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
pip install -q pydoc-markdown==3.10.1 --trusted-host pypi.org --trusted-host files.pythonhosted.org
let return_code=$?

check_rc $return_code "ERROR: pip install encountered an error."

## Get the modules we want to document
file_list=""
first_time="1"
for file in `ls -1 *.py`
do
    module=${file%%".py"}
    if [ "${first_time}" = "1" ]; then
        file_list="-m ${module}"
        first_time="0"
    else
        file_list="${file_list} -m ${module}"
    fi
done

echo "INFO: Creating API markdown file ..."
## Run the documentation command
pydoc-markdown -I . ${file_list} --render-toc > API.md
let return_code=$?

check_rc $return_code "ERROR: Failed to create API.md file."

## Perform cleanup
echo "INFO: Cleaning up environment ..."
deactivate
rm -rf venv
find . -type d -name "__pycache__" -exec rm -rf {} +

exit 0
