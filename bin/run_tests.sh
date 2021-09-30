#!/bin/sh
#TODO This could be better organized
set -e
base=$(pwd)
failed=0

# runs the test for shared library (OLD)
# This should be removed once all lambdas are converted to using pip.
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

# run tests for shared libraries
echo
echo "Running tests in shared_libraries"
echo

cd shared_libraries
bin/run_tests.sh
return_code=$?
cd -

if [ $return_code -ne 0 ]; then
  failed=1
fi


## Call each task's testing suite
## TODO: Add more logging output and possibly make asynchronus
for task in $(ls -d tasks/* | egrep -v "dr_dbutils|pg_utils|shared_libraries|package")
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
