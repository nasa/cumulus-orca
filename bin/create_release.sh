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


source bin/common/check_returncode.sh


## Validate that the release flag is set
if [[ ! $bamboo_RELEASE_FLAG == true ]]; then
  >&2 echo "WARN: Skipping Release ORCA code step, PUBLISH_FLAG is [ $bamboo_RELEASE_FLAG ]"
  exit 0
fi

export url="https://github.com/nasa/cumulus-orca/releases/download/v$bamboo_ORCA_VERSION/cumulus-orca-terraform.zip"
curl_result=$(curl -Is "$url" | head -1)
# Remove the ' ^M' that curl tacks on to the results.
curl_result=${curl_result::${#curl_result}-2}
# debug step for showing hidden characters.
# echo $curl_result | cat -v
# 302 is found, 404 for not found
if [ "$curl_result" == "HTTP/2 302" ]; then
  echo "$url already exists. Exiting."
  exit 1
elif [ "$curl_result" == "HTTP/2 404" ]; then
  echo "$url has not been released. Proceeding."
else
  echo "Unexpected response from $url: $curl_result"
  exit 1
fi

## Release the Code
cd dist

# Create Release
export RELEASE_URL=$(curl \
    -H "Authorization: token $bamboo_SECRET_GITHUB_TOKEN" \
    -d "{\"tag_name\": \"v$bamboo_ORCA_VERSION\", \"target_commitsh\": \"v$bamboo_ORCA_VERSION\", \"name\": \"v$bamboo_ORCA_VERSION\", \"body\": \"Release v$bamboo_ORCA_VERSION\" }" \
    -H "Content-Type: application/json" \
    -X POST \
    https://api.github.com/repos/nasa/cumulus-orca/releases \
    | grep \"url\" \
    | grep releases \
    | sed -e 's/.*\(https.*\)\"\,/\1/' \
    | sed -e 's/api/uploads/')

# Release URL is created only if there is valid github token
if [[ ! $RELEASE_URL ]]; then
  echo "RELEASE_URL is empty. This may be caused by an invalid 'GITHUB_TOKEN'. Exiting"
  exit 1
else
  echo "$RELEASE_URL has not been released. Proceeding."
fi

curl \
    -X POST \
    -H "Authorization: token $bamboo_SECRET_GITHUB_TOKEN" \
    --data-binary "@cumulus-orca-terraform.zip" \
    -H "Content-type: application/octet-stream" \
    $RELEASE_URL/assets?name=cumulus-orca-terraform.zip
check_returncode $? "Error during curl command."

cd ..

exit 0
