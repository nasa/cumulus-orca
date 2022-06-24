#!/bin/sh
#TODO This needs to be better organized
set -e

rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -q --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org
deactivate
echo "pwd `pwd`"

echo "Pulling awslambda-psycopg2 in preparation for build"
mkdir -p tasks/package
cd tasks/package
if [ ! -d "awslambda-psycopg2" ]; then
  git clone https://github.com/jkehler/awslambda-psycopg2.git
fi
cd ../../

function build_task() {
  echo "Building $1"
  cd $1
  bin/build.sh
  return_code=$?
  if [ $return_code != 0 ]; then
    echo "ERROR: Building of $1 failed."
  fi
  return $return_code
}
export -f build_task

task_dirs=$(ls -d tasks/* | egrep -v "package")

parallel -X --halt now,fail=1 build_task ::: $task_dirs

process_return_code=$?
if [ $process_return_code -ne 0 ]; then
  exit 1  # process_return_code indicates how many tasks failed. Flatten to 1 if any number failed.
