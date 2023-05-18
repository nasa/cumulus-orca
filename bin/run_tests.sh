#!/bin/sh
#TODO This could be better organized
set -e
base=$(pwd)
failed=0

# run tests for shared libraries
echo
echo "Running tests in shared_libraries"
echo

cd shared_libraries
bin/run_tests.sh
return_code=$?
cd -

if [ $return_code -ne 0 ]
then
  failed=1
fi

function run_unit_tests() {
  echo
  echo "Running tests in $1"
  echo

  cd $1
  bin/run_tests.sh
  return_code=$?

  if [ $return_code -ne 0 ]
  then
    echo "ERROR: Testing of $1 failed with code $return_code"
  fi
  return $return_code
}
export -f run_unit_tests

task_dirs=$(ls -d tasks/* | egrep -v "package")

## Call each task's testing suite
## TODO: Add more logging output
echo "Running unit tests in parallel..."
# todo: ORCA-681: Repair parallelism and switch back to `--jobs 0`
parallel --jobs 1 -n 1 -X --halt now,fail=1 run_unit_tests ::: $task_dirs

process_return_code=$?
echo
if [ $process_return_code -ne 0 ]
then
  echo "ERROR: process failed with code $process_return_code."
  exit 1  # process_return_code may indicate how many tasks failed. Flatten to 1 if any number failed.
else
  echo "All tests succeeded."
fi