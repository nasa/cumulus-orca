function check_returncode () {
  ## Checks the return code of call and if not equal to 0, emits an error and
  ## exits the script with a failure.
  ##
  ## Args:
  ##   $1 - Return Code from command
  ##   $2 - Error message if failure occurs.
  let RC=$1
  MESSAGE=$2
  if [ $RC -ne 0 ]; then
      >&2 echo "$MESSAGE"
      exit 1
  fi
}

function run_and_check_returncode () {
  ## Checks the return code of call and if not equal to 0, emits an error and
  ## exits the script with a failure.
  ##
  ## Args:
  ##   $1 - The command to run.
  COMMAND=$1

  echo "INFO: Running '$COMMAND' ..."

  $COMMAND
  RC=$?
  check_returncode $RC "ERROR: '$COMMAND' failed with a return code of [$RC]!"
}
