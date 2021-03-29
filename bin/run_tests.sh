#!/bin/sh
#TODO This could be better organized
set -e
base=$(pwd)
failed=0

# Crawl the task directories
for taskdir in `ls -d tasks/* | grep -v request_status_for`
do
  # Build and run tests for each task directory
  cd $taskdir
  echo
  echo "Running tests in $taskdir"
  echo
  rm -rf venv
  python3 -m venv venv
  source venv/bin/activate
  pip install -q --upgrade pip
  pip install -q -r requirements-dev.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
  # Currenty just running unit tests until we fix/support large tests
  coverage run --source test/unit_tests/ -m pytest test/unit_tests/
  result=$?
  if [[ $result -eq 1 ]]; then
    failed=1
  fi
  coverage report
  deactivate
  cd $base
done


## Call each tasks testing suite
## TODO: Add more logging output and possibly make asynchronus
for task in $(ls -d tasks/* | grep request_status_)
do
  echo
  echo "Running tests in $task"
  echo

  cd $task
  bin/run_tests.sh
  return_code=$?
  cd -

  if [ $return_code -ne 0 ]; then
    failed=1
  fi
done


exit $failed
