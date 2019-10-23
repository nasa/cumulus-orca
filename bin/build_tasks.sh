#!/bin/sh

set -e
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
cp db_deploy.py build/
cd build
mkdir psycopg2
mkdir ddl
cd ..
cp ../package/awslambda-psycopg2/psycopg2-3.7/* build/psycopg2/
cp -r ../../database/ddl/base/* build/ddl/
cd build
mkdir utils
cp ../utils/*.py utils/
zip -r ../dbdeploy.zip .
cd ../../../

TASK='tasks/extract_filepaths_for_granule/'
echo "Building `pwd`/${TASK}"
cd "`pwd`/${TASK}"
rm -rf build
mkdir build
source ../../venv/bin/activate
pip install -t build -r requirements.txt
deactivate
cp *.py build/
cd build
zip -r ../extract.zip .
cd ../../../

TASK='tasks/request_status/'
echo "Building `pwd`/${TASK}"
cd "`pwd`/${TASK}"
rm -rf build
mkdir build
source ../../venv/bin/activate
pip install -t build -r requirements.txt
deactivate
cp request_status.py build/
cd build
mkdir psycopg2
cd ..
cp ../package/awslambda-psycopg2/psycopg2-3.7/* build/psycopg2/
cd build
zip -r ../status.zip .
cd ../../../

TASK='tasks/copy_files_to_archive/'
echo "Building `pwd`/${TASK}"
cd "`pwd`/${TASK}"
rm -rf build
mkdir build
source ../../venv/bin/activate
pip install -t build -r requirements.txt
deactivate
cp copy_files_to_archive.py build/
cd build
mkdir psycopg2
cd ..
cp ../package/awslambda-psycopg2/psycopg2-3.7/* build/psycopg2/
cd build
zip -r ../copy.zip .
cd ../../../
	
TASK='tasks/request_files/'
echo "Building `pwd`/${TASK}"
cd "`pwd`/${TASK}"
rm -rf build
mkdir build
source ../../venv/bin/activate
pip install -t build -r requirements.txt
deactivate
cp request_files.py build/
cd build
mkdir psycopg2
cd ..
cp ../package/awslambda-psycopg2/psycopg2-3.7/* build/psycopg2/
cd build
zip -r ../request.zip .
cd ../../../
