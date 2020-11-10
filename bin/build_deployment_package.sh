#!/bin/sh
#TODO This needs to be better organized
set -e

rm -rf build
mkdir build
mkdir build/tasks

cp -r database build
cp -r modules build
cp *.tf build
cp README.md build
cp LICENSE.txt build
cp terraform.tfvars.example build

for package in $(find . -name *.zip);
do
  cp $package build/tasks/
done 
