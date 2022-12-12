# Be sure to source check_returncode.sh when using this library.
function create_and_activate_venv () {
  ## Removes any pre-existing virtual environment if present.
  ## Then creates a virtual environment and activates it, and sources in its scripts.

  ## Create the virtual env. Remove it if it already exists.
  echo "INFO: Creating virtual environment ..."
  if [ -d venv ]; then
    run_and_check_returncode "rm -rf venv"
    find . -type d -name "__pycache__" -exec rm -rf {} +
  fi
  
  run_and_check_returncode "python3.9 -m venv venv"
  run_and_check_returncode "source venv/bin/activate"

  echo "INFO: Virtual environment ready."
}

function deactivate_and_delete_venv () {
  run_and_check_returncode "deactivate"
  ## Perform cleanup
  echo "INFO: Cleaning up virtual environment ..."
  run_and_check_returncode "rm -rf venv"
  find . -type d -name "__pycache__" -exec rm -rf {} +
}
