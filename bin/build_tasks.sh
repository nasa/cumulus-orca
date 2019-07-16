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
    pip3 install -t build -r requirements.txt
    deactivate
    cp *.py build/
    cd build
    zip -r ../task.zip .
    cd ../../../
  fi 
done
