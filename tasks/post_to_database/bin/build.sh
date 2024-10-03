#!/bin/bash
## =============================================================================
## NAME: build.sh
##
##
## DESCRIPTION
## -----------------------------------------------------------------------------
## Builds the lambda (task) zip file for post_to_database.
##
##
## USAGE
## -----------------------------------------------------------------------------
## bin/build.sh
##
## This must be called from the (root) lambda directory /tasks/post_to_database
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
## Create the build directory. Remove it if it exists.
echo "INFO: Creating build directory ..."
if [ -d build ]; then
    rm -rf build
fi

run_and_check_returncode "mkdir build"
trap 'rm -rf build' EXIT

run_and_check_returncode "create_and_activate_venv"
trap 'deactivate_and_delete_venv;rm -rf build;' EXIT
run_and_check_returncode "pip install -q --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org"

## Install the requirements
pip install -q -t build -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
check_returncode $? "ERROR: pip install encountered an error."

## Copy the lambda files to build
echo "INFO: Creating the Lambda package ..."
cp *.py build/
check_returncode $? "ERROR: Failed to copy lambda files to build directory."

## Copy the schema files to build
echo "INFO: Copying schema files ..."
cp -r schemas/ build/schemas/
check_returncode $? "ERROR: Failed to copy schema files to build directory."

## Create the zip archive
cd build
trap 'cd -;deactivate_and_delete_venv;rm -rf build;' EXIT
run_and_check_returncode "zip -qr ../post_to_database.zip ."

