#!/bin/sh
#TODO This needs to be better organized
set -e

rm -rf venv
python3 -m venv venv
source venv/bin/activate
trap 'deactivate' EXIT
pip install -q --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org
echo "pwd `pwd`"

echo "Pulling awslambda-psycopg2 in preparation for build"
mkdir -p tasks/package
cd tasks/package
if [ ! -d "../package/awslambda-psycopg2/psycopg2-3.9" ]; then
  rm -d -f -r "../package/awslambda-psycopg2"
fi
if [ ! -d "awslambda-psycopg2" ]
then
  git clone https://github.com/jkehler/awslambda-psycopg2.git
fi
cd ../../

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
  return $return_code
}
export -f build_task

task_dirs=$(ls -d tasks/* | egrep -v "package")

echo "Building in parallel..."
parallel --jobs 0 -n 1 -X --halt now,fail=1 build_task ::: $task_dirs

process_return_code=$?
echo
if [ $process_return_code -ne 0 ]
then
  echo "ERROR: process failed with code $process_return_code."
  exit 1  # process_return_code may indicate how many tasks failed. Flatten to 1 if any number failed.
else
  echo "All builds succeeded."
fi
