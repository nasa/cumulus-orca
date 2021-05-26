#!/bin/sh
#TODO This could be better organized
set -e
base=$(pwd)
failed=0

# Crawl the task directories
for taskdir in `ls -d tasks/* | egrep -v 'request_status_for|shared_libraries|db_deploy|package|copy_files_to_archive|post_copy_request_to_queue' `
do
  # Build and run tests for each task directory
  cd $taskdir
  echo
  echo "Running tests in $taskdir"
  echo
  rm -rf venv
  python3 -m venv venv
  source venv/bin/activate
  pip install -q --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org
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

# runs the test for shared library
for shared_library in $(ls -d tasks/shared_libraries/*)
do
  echo
  echo "Running tests in $shared_library"
  echo

  cd $shared_library
  bin/run_tests.sh
  return_code=$?
  cd -

  if [ $return_code -ne 0 ]; then
    failed=1
  fi
done

## Call each tasks testing suite
## TODO: Add more logging output and possibly make asynchronus
for task in $(ls -d tasks/* | egrep "request_status_|db_deploy|copy_files_to_archive|post_copy_request_to_queue")
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
