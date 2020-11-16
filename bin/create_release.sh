#!/bin/bash

set -ex

cd dist

# Create Release
export RELEASE_URL=$(curl -H\
  "Authorization: token $bamboo_GITHUB_TOKEN"\
   -d "{\"tag_name\": \"v$bamboo_ORCA_VERSION\", \"target_commitsh\": \"v$bamboo_ORCA_VERSION\", \"name\": \"v$bamboo_ORCA_VERSION\", \"body\": \"Release v$bamboo_ORCA_VERSION\" }"\
   -H "Content-Type: application/json"\
   -X POST\
   https://api.github.com/repos/nasa/cumulus-orca/releases |grep \"url\" |grep releases |sed -e 's/.*\(https.*\)\"\,/\1/'| sed -e 's/api/uploads/')

# Release Package
echo $RELEASE_URL
curl -X POST -H "Authorization: token $bamboo_GITHUB_TOKEN" --data-binary "@cumulus-orca-terraform.zip" -H "Content-type: application/octet-stream" $RELEASE_URL/assets?name=cumulus-orca-terraform.zip
