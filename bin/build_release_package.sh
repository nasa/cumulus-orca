#!/bin/sh
#TODO This needs to be better organized
set -ex

if [[ ! $bamboo_PUBLISH_FLAG == true ]]; then
  >&2 echo "******Skipping publish to npm step as PUBLISH_FLAG is not set"
  exit 0
fi

# Create the lambda zips
./bin/build_tasks.sh

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

# create distribution package
mkdir dist

cd build
zip -r "../dist/cumulus-orca-terraform.zip" .
cd ..

# Create the GitHub release
./bin/create_release.sh
