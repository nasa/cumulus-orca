#!/bin/sh
#TODO This needs to be better organized
set -e

source bin/common/check_returncode.sh

echo "pwd `pwd`"

function build_task() {
  echo
  echo "Building $1"
  echo
  
  cd $1
  bin/build.sh
  return_code=$?
  if [ $return_code != 0 ]
  then
    echo "ERROR: Building of $1 failed with code $return_code"
  fi
  echo "Completed building $1"
  return $return_code
}
export -f build_task

task_dirs=$(ls -d tasks/* | egrep -v "package")
echo "Build targets: $task_dirs"

echo "Building in parallel..."
# todo: ORCA-681: Repair parallelism and switch back to `--jobs 0`
parallel --jobs 1 -n 1 -X --halt now,fail=1 build_task ::: $task_dirs

process_return_code=$?
echo
if [ $process_return_code -ne 0 ]
then
  echo "ERROR: process failed with code $process_return_code."
  exit 1  # process_return_code may indicate how many tasks failed. Flatten to 1 if any number failed.
else
  echo "All builds succeeded."
fi
