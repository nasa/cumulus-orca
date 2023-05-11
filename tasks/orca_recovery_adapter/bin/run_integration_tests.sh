#!/bin/bash
## =============================================================================
## NAME: run_integration_tests.sh
##
##
## DESCRIPTION
## -----------------------------------------------------------------------------
## Runs the integration tests.
##
##
## USAGE
## -----------------------------------------------------------------------------
## bin/run_integration_tests.sh
##
## This must be called from the (root) directory tasks/orca_recovery_adapter
## =============================================================================

## Set this for Debugging only
#set -ex

## Make sure we are calling the script the correct way.
BASEDIR=$(dirname $0)
if [ "$BASEDIR" != "bin" ]; then
  >&2 echo "ERROR: This script must be called from the root directory of lambda task[bin/run_integration_tests.sh]."
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

## Run tests
echo "INFO: Running integration tests ..."
python -m pytest test/integration_tests/integration_test_orca_recovery_adapter.py
check_returncode $? "ERROR: Unit tests encountered failures."