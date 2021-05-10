#!/bin/sh
#TODO This needs to be better organized
set -e

rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -q --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org
deactivate
echo "pwd `pwd`"

echo "Pulling awslambda-psycopg2 in preparation for build"
mkdir -p tasks/package
cd tasks/package
if [ ! -d "awslambda-psycopg2" ]; then
  git clone https://github.com/jkehler/awslambda-psycopg2.git
fi
cd ../../


TASK='tasks/extract_filepaths_for_granule/'
echo "Building `pwd`/${TASK}"
cd "`pwd`/${TASK}"
rm -rf build
mkdir build
source ../../venv/bin/activate
pip install -q -t build -r requirements.txt --trusted-host pypi.org --trusted-host pypi.org --trusted-host files.pythonhosted.org
deactivate
cp *.py build/
cd build
zip -qr "../extract_filepaths_for_granule.zip" .
cd ../../../


TASK='tasks/copy_files_to_archive/'
echo "Building `pwd`/${TASK}"
cd "`pwd`/${TASK}"
rm -rf build
mkdir build
source ../../venv/bin/activate
pip install -q -t build -r requirements.txt --trusted-host pypi.org --trusted-host pypi.org --trusted-host files.pythonhosted.org
deactivate
cp copy_files_to_archive.py build/
cd build
mkdir psycopg2
cd ..
cp ../package/awslambda-psycopg2/psycopg2-3.7/* build/psycopg2/
cd build
zip -qr "../copy_files_to_archive.zip" .
cd ..
rm -rf build
cd ../../


TASK='tasks/request_files/'
echo "Building `pwd`/${TASK}"
cd "`pwd`/${TASK}"
rm -rf build
mkdir build
source ../../venv/bin/activate
pip install -q -t build -r requirements.txt --trusted-host pypi.org --trusted-host pypi.org --trusted-host files.pythonhosted.org
deactivate
cp request_files.py build/
cd build
mkdir psycopg2
cd ..
cp ../package/awslambda-psycopg2/psycopg2-3.7/* build/psycopg2/
cd build
zip -qr "../request_files.zip" .
cd ..
rm -rf build
cd ../../


TASK='tasks/copy_to_glacier/'
echo "Building `pwd`/${TASK}"
cd "`pwd`/${TASK}"
rm -rf build
mkdir build
source ../../venv/bin/activate
pip install -q -t build -r requirements.txt --trusted-host pypi.org --trusted-host pypi.org --trusted-host files.pythonhosted.org
deactivate
cp *.py build/
cd build
zip -qr "../copy_to_glacier.zip" .
cd ..
rm -rf build
cd ../../


failure=0
for TASK in $(ls -d tasks/* | egrep "request_status_|db_deploy")
do
  echo "Building ${TASK}"
  cd ${TASK}
  bin/build.sh
  return_code=$?
  cd -

  if [ $return_code -ne 0 ]; then
    echo "ERROR: Building of $TASK failed."
    failure=1
  fi
done


exit $failure
