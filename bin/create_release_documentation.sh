#!/bin/bash
## =============================================================================
## NAME: create_release_documentation.sh
##
##
## DESCRIPTION
## -----------------------------------------------------------------------------
## Builds the Cumulus-Orca documentation at https://nasa.github.io/cumulus-orca
## and deploys the updated documentation.
##
##
## ENVIRONMENT SETTINGS
## -----------------------------------------------------------------------------
## bamboo_RELEASE_FLAG (boolean) - Determines if the build should occur and be
##                                 released to GitHub release.
##
## bamboo_SECRET_GITHUB_TOKEN (string) - GitHub Secret Token needed to access
##                                       the cumulus-orca repo.
##
## bamboo_GITHUB_USER (string) - GitHub user performing the commit for the
##                               application documentation.
##
##
## USAGE
## -----------------------------------------------------------------------------
## bin/create_release.sh
##
## This must be called from the (root) git repo directory.
## =============================================================================
## Set this for Debugging only
set -ex

## Make sure we are calling the script the correct way.
BASEDIR=$(dirname $0)
if [ "$BASEDIR" != "bin" ]; then
  >&2 echo "ERROR: This script must be called from the root directory of the repo [bin/create_release_documentation.sh]."
  exit 1
fi


## Validate that the release flag is set
if [[ ! $bamboo_RELEASE_FLAG == true ]]; then
  >&2 echo "WARN: Skipping Release ORCA documentation step as bamboo_PUBLISH_FLAG is not set"
  #exit 0  # Commented out for testing
fi


## FUNCTIONS
## -----------------------------------------------------------------------------
function check_rc () {
  ## Checks the return code of call and if not equal to 0, emits an error and
  ## exits the script with a failure.
  COMMAND=$1

  echo "INFO: Running '$COMMAND' ..."

  $COMMAND
  let RC=$?

  if [ $RC -ne 0 ]; then
      >&2 echo "ERROR: '$COMMAND' failed with a return code of [$RC]!"
      exit 1
  fi
}


## MAIN
## -----------------------------------------------------------------------------
## Release the Documentation
# Go to the documentation directory
check_rc "cd website"

# Install Node.js and the proper packages
check_rc "npm install"

# Run the deployment See: https://docusaurus.io/docs/deployment
export DEPLOYMENT_BRANCH=gh-pages-test
export GIT_USER=$bamboo_GITHUB_USER
export GIT_PASS=$bamboo_SECRET_GITHUB_TOKEN

check_rc "npm run deploy"

cd ..

exit 0

