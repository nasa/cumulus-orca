cd ".."
rm -rf build
mkdir build
source ../../venv/bin/activate
pip install -t build -r requirements.txt --trusted-host pypi.org --trusted-host pypi.org --trusted-host files.pythonhosted.org
deactivate
cp *.py build/
cd build
zip -r "../request_status_for_job.zip" .
cd ..
rm -rf build
