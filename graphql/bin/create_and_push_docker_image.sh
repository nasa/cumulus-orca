#!/bin/bash
## =============================================================================
## NAME: create_and_push_docker_image.sh
##
##
## DESCRIPTION
## -----------------------------------------------------------------------------
## Builds the GraphQL image and pushes it to NASA Github Packages.
##
## USAGE
## -----------------------------------------------------------------------------
## bin/create_and_push_docker_image.sh
##
## This must be called from the (root) graphql directory /graphql
##
## Args:
##   $1 - The version number to create in Github.
##   $2 - An access token with the `write:packages` permission on the NASA organization.
## =============================================================================

## Set this for Debugging only
#set -ex

## Make sure we are calling the script the correct way.
BASEDIR=$(dirname $0)
if [ "$BASEDIR" != "bin" ]; then
  >&2 echo "ERROR: This script must be called from the root directory of the component [bin/create_and_push_docker_image.sh]."
  exit 1
fi


source ../bin/common/check_returncode.sh

version_number=$1
github_token=$2

echo $github_token | docker login ghcr.io -u nasa --password-stdin
check_returncode $? "Error logging into Github."

image_name=graphql
run_and_check_returncode "docker build -t $image_name --build-arg VERSION_NUMBER=$version_number ."
run_and_check_returncode "docker tag $image_name ghcr.io/nasa/cumulus-orca/$image_name:$version_number"
run_and_check_returncode "docker push ghcr.io/nasa/cumulus-orca/$image_name:$version_number"
