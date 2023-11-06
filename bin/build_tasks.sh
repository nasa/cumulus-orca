#!/bin/sh
set -e

source bin/common/check_returncode.sh

echo "pwd $(pwd)"

echo "Pulling awslambda-psycopg2 in preparation for build"
mkdir -p tasks/package
if [ -d "tasks/package/awslambda-psycopg2" ]; then
  rm -rf "tasks/package/awslambda-psycopg2"
fi
if [ ! -d "tasks/package/awslambda-psycopg2" ]; then
  git clone https://github.com/jkehler/awslambda-psycopg2.git "tasks/package/awslambda-psycopg2"
fi

function build_task() {
  local task_dir="$1"
  echo
  echo "Building $task_dir"
  echo
  
  (cd "$task_dir" && bin/build.sh)
  return_code=$?
  if [ $return_code -ne 0 ]; then
    echo "ERROR: Building of $task_dir failed with code $return_code"
  fi
  echo "Completed building $task_dir"
  return $return_code
}
export -f build_task

task_dirs=$(ls -d tasks/* | egrep -v "package")
echo "Build targets: $task_dirs"

echo "Building in parallel..."
# todo: ORCA-681: Repair parallelism and switch back to `--jobs 0`
process_return_code=$?
echo
if [ $process_return_code -ne 0 ]; then
  echo "ERROR: process failed with code $process_return_code."
  exit 1  # process_return_code may indicate how many tasks failed. Flatten to 1 if any number failed.
else
  echo "All builds succeeded."
fi
