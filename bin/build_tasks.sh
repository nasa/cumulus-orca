#!/bin/sh

set -e

if [ -z ${DR_VERSION+x} ]; then
  DR_VERSION=$1
fi

rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
deactivate
echo "pwd `pwd`"

echo "Pulling awslambda-psycopg2 in preparation for build"
mkdir -p tasks/package
cd tasks/package
if [ ! -d "awslambda-psycopg2" ]; then
  git clone https://github.com/jkehler/awslambda-psycopg2.git
fi
cd ../../

TASK='tasks/db_deploy/'
echo "Building `pwd`/${TASK}"
cd "`pwd`/${TASK}"
rm -rf build
mkdir build
source ../../venv/bin/activate
pip install -t build -r requirements.txt --trusted-host pypi.org
deactivate
cp db_deploy.py build/
cd build
mkdir psycopg2
mkdir ddl
cd ..
cp ../package/awslambda-psycopg2/psycopg2-3.7/* build/psycopg2/
cp -r ../../database/ddl/base/* build/ddl/
cd build
zip -r "../dbdeploy-${DR_VERSION}.zip" .
cd ../../../

TASK='tasks/extract_filepaths_for_granule/'
echo "Building `pwd`/${TASK}"
cd "`pwd`/${TASK}"
rm -rf build
mkdir build
source ../../venv/bin/activate
pip install -t build -r requirements.txt --trusted-host pypi.org
deactivate
cp *.py build/
cd build
zip -r "../extract-${DR_VERSION}.zip" .
cd ../../../

TASK='tasks/request_status/'
echo "Building `pwd`/${TASK}"
cd "`pwd`/${TASK}"
rm -rf build
mkdir build
source ../../venv/bin/activate
pip install -t build -r requirements.txt --trusted-host pypi.org
deactivate
cp request_status.py build/
cd build
mkdir psycopg2
cd ..
cp ../package/awslambda-psycopg2/psycopg2-3.7/* build/psycopg2/
cd build
zip -r "../status-${DR_VERSION}.zip" .
cd ../../../

TASK='tasks/copy_files_to_archive/'
echo "Building `pwd`/${TASK}"
cd "`pwd`/${TASK}"
rm -rf build
mkdir build
source ../../venv/bin/activate
pip install -t build -r requirements.txt --trusted-host pypi.org
deactivate
cp copy_files_to_archive.py build/
cd build
mkdir psycopg2
cd ..
cp ../package/awslambda-psycopg2/psycopg2-3.7/* build/psycopg2/
cd build
zip -r "../copy-${DR_VERSION}.zip" .
cd ../../../
	
TASK='tasks/request_files/'
echo "Building `pwd`/${TASK}"
cd "`pwd`/${TASK}"
rm -rf build
mkdir build
source ../../venv/bin/activate
pip install -t build -r requirements.txt --trusted-host pypi.org
deactivate
cp request_files.py build/
cd build
mkdir psycopg2
cd ..
cp ../package/awslambda-psycopg2/psycopg2-3.7/* build/psycopg2/
cd build
zip -r "../request-${DR_VERSION}.zip" .
cd ../../../
