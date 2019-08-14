#!/bin/sh

set -e
rm -rf venv
python3 -m venv venv
for TASK in `ls -d tasks/*/`
do
  if [ ${TASK} != 'tasks/testfiles/' ]; then
    echo "Building `pwd`/${TASK}"
    cd "`pwd`/${TASK}"
    rm -rf build
    mkdir build
    source ../../venv/bin/activate
    pip install --upgrade pip    
    pip install -t build -r requirements.txt
    deactivate
    cp *.py build/
    cd build
    if [ ${TASK} == 'tasks/request_files/' ]; then
      mkdir psycopg2
      cd ..
      cp awslambda-psycopg2/psycopg2-3.7/* build/psycopg2/
      cd build
      mkdir utils
      cp ../utils/*.py utils/
    fi
    zip -r ../task.zip .
    cd ../../../
  fi 
done
