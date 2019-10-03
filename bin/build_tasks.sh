#!/bin/sh

set -e
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip    
deactivate
echo "pwd1 `pwd`"

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
rm -rf build_db
mkdir build_db
cp db_deploy.py build_db/
cd build_db
mkdir psycopg2
mkdir ddl
cd ..
cp ../package/awslambda-psycopg2/psycopg2-3.7/* build_db/psycopg2/
cp -r ../../database/ddl/base/* build_db/ddl/
cd build_db
mkdir utils
cp ../utils/*.py utils/
zip -r ../dbdeploy.zip .
cd ../../../
echo "pwd6 `pwd`"

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
echo "pwd2 `pwd`"

TASK='tasks/request_files/'
echo "Building `pwd`/${TASK}/request_status"
cd "`pwd`/${TASK}"
rm -rf build_rs
mkdir build_rs
cp request_status.py build_rs/
cp requests.py build_rs/
cd build_rs
mkdir psycopg2
cd ..
cp ../package/awslambda-psycopg2/psycopg2-3.7/* build_rs/psycopg2/
cd build_rs
mkdir utils
cp ../utils/*.py utils/
zip -r ../status.zip .
cd ../../../
echo "pwd3 `pwd`"

TASK='tasks/request_files/'
echo "Building `pwd`/${TASK}/copy_files"
cd "`pwd`/${TASK}"
echo "pwd3b `pwd`"
rm -rf build_cp
mkdir build_cp
cp copy_files_to_archive.py build_cp/
cp requests.py build_cp/
cd build_cp
mkdir psycopg2
cd ..
cp ../package/awslambda-psycopg2/psycopg2-3.7/* build_cp/psycopg2/
cd build_cp
mkdir utils
cp ../utils/*.py utils/
zip -r ../copy.zip .
cd ../../../
echo "pwd4 `pwd`"
	
TASK='tasks/request_files/'
echo "Building `pwd`/${TASK}/request_files"
cd "`pwd`/${TASK}"
rm -rf build_rf
mkdir build_rf
source ../../venv/bin/activate
pip install -t build_rf -r requirements.txt
deactivate
cp request_files.py build_rf/
cp requests.py build_rf/
cd build_rf
mkdir psycopg2
cd ..
cp ../package/awslambda-psycopg2/psycopg2-3.7/* build_rf/psycopg2/
cd build_rf
mkdir utils
cp ../utils/*.py utils/
zip -r ../request.zip .
cd ../../../
echo "pwd5 `pwd`"
