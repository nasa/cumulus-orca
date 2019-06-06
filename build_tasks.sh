#!/bin/sh

set -e

for TASK in `ls tasks`
do
  cd "`pwd`/tasks/${TASK}"
  zip task.zip *.py
  cd ../../
done