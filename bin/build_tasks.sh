#!/bin/sh

set -e

for TASK in `ls -d tasks/*/`
do
  if [ ${TASK} != 'tasks/testfiles/' ]; then
    echo "Building `pwd`/${TASK}"
    cd "`pwd`/${TASK}"
    zip task.zip *.py
    cd ../../
  fi 
done