#!/bin/sh

set -e

for TASK in `ls -d tasks/*/`
do
  if [ ${TASK} != 'tasks/testfiles/' ]; then
    echo "Building `pwd`/${TASK}"
    cd "`pwd`/${TASK}"
    rm -rf build
    mkdir build
    pip install -r requirements.txt -t build
    cp *.py build/
    cd build
    zip -r ../task.zip .
    cd ../../../
  fi 
done
