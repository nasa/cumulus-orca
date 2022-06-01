#!/bin/sh
#TODO This needs to be better organized
set -e

rm -rf venv
python3 -m venv venv
. venv/bin/activate
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

failure=0
for TASK in $(ls -d tasks/* | egrep -v "package|get_current_archive_list|perform_orca_reconcile") #todo update once the lambdas are created
do
  echo "Building ${TASK}"
  cd ${TASK}
  bin/build.sh
  return_code=$?
  cd -

  if [ $return_code -ne 0 ]; then
    echo "ERROR: Building of $TASK failed."
    failure=1
  fi
done


exit $failure
