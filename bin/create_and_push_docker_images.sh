#!/bin/bash
## Set this for Debugging only
#set -ex

source bin/common/check_returncode.sh

version_number=$1
github_token=$2

base=$(pwd)
echo "pwd $base"
trap 'cd $base' EXIT

echo $github_token | docker login ghcr.io -u nasa --password-stdin
check_returncode $? "Error logging into Github."

cd graphql
image_name=orca-graphql
run_and_check_returncode "docker build -t $image_name ."
run_and_check_returncode "docker tag $image_name ghcr.io/nasa/$image_name:$version_number"
run_and_check_returncode "docker push ghcr.io/nasa/$image_name:$version_number"
