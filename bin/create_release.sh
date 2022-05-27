#!/bin/bash
## =============================================================================
## NAME: create_release.sh
##
##
## DESCRIPTION
## -----------------------------------------------------------------------------
## Creates a GitHub release for the Cumulus-Orca repository at
## https://github.com/nasa/cumulus-orca/releases. Uploads the artifacts for the
## release.
##
##
## ENVIRONMENT SETTINGS
## -----------------------------------------------------------------------------
## bamboo_SECRET_GITHUB_TOKEN (string) - GitHub Secret Token needed to access
##                                       the cumulus-orca repo.
##
## bamboo_ORCA_VERSION (string) - ORCA semantic application version being released.
##
##
## USAGE
## -----------------------------------------------------------------------------
## bin/create_release.sh
##
## This must be called from the (root) git repo directory.
## =============================================================================
## Set this for Debugging only
#set -ex

## Make sure we are calling the script the correct way.
BASEDIR=$(dirname $0)
if [ "$BASEDIR" != "bin" ]; then
  >&2 echo "ERROR: This script must be called from the root directory of the repo [bin/create_release.sh]."
  exit 1
fi

## Validate that the release flag is set
if [[ ! $bamboo_RELEASE_FLAG == true ]]; then
  >&2 echo "WARN: Skipping Release ORCA code step, PUBLISH_FLAG is [ $bamboo_RELEASE_FLAG ]"
  exit 0
fi

## Release the Code
## TODO: Make this more robust. Check for errors see if release already created, etc.
cd dist

# Create Release
export RELEASE_URL=$(curl \
    -H "Authorization: token $bamboo_SECRET_GITHUB_TOKEN" \
    -d "{\"tag_name\": \"v$bamboo_ORCA_VERSION\", \"target_commitsh\": \"v$bamboo_ORCA_VERSION\", \"name\": \"v$bamboo_ORCA_VERSION\", \"body\": \"Release v$bamboo_ORCA_VERSION\" }" \
    -H "Content-Type: application/json" \
    -X POST \
    "https://api.github.com/repos/$GITHUB_REPO/releases"\
    | grep \"url\" \
    | grep releases \
    | sed -e 's/.*\(https.*\)\"\,/\1/' \
    | sed -e 's/api/uploads/')

# Release Package
echo $RELEASE_URL
curl \
    -X POST \
    -H "Authorization: token $bamboo_SECRET_GITHUB_TOKEN" \
    --data-binary "@cumulus-orca-terraform.zip" \
    -H "Content-type: application/octet-stream" \
    $RELEASE_URL/assets?name=cumulus-orca-terraform.zip

cd ..
