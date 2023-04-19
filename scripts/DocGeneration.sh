#!/bin/sh
cd ..
repoDir=${PWD}
tasks=("copy_from_archive" "copy_from_archive.py"
        #"copy_to_archive" "handler.py"
        #"db_deploy" "db_deploy.py"
        #"extract_filepaths_for_granule" "extract_filepaths_for_granule.py"
        #"request_from_archive" "request_from_archive.py"
        #"request_status" "request_status.py"
        )

echo "${repoDir}"

for (( i=0; i<${#tasks[@]}; i=i+2 ))
do
  newDir="${repoDir}/tasks/${tasks[i]}"
  cd "${newDir}" || exit

  echo "Running for ${tasks[i]}/${tasks[i+1]}"
  source venv/Scripts/activate
  python -m pydoc "${tasks[i+1]%%.*}"
  docs=$(python -m pydoc "${tasks[i+1]%%.*}")
  docs=$(source python -m pydoc "${tasks[i+1]%%.*}")
  docs=source $(python -m pydoc "${tasks[i+1]%%.*}")
  echo "${docs}"
  source venv/Scripts/deactivate.bat
  # source deactivate
done

echo "Done"