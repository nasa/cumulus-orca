#!/bin/sh
#TODO This could be better organized
set -e
base=$(pwd)
failed=0

# Crawl the task directories
for taskdir in tasks/*/
do
  # Build and run tests for each task directory
  cd $taskdir
  echo "Running tests in $taskdir"
  rm -rf venv
  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements-dev.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
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

exit $failed
