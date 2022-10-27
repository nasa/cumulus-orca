#!/bin/bash
## Set this for Debugging only
#set -ex

source bin/common/check_returncode.sh

github_token=$1
version_number=$2

base=$(pwd)
echo $"pwd" `base`"
trap 'cd $base' EXIT

run_and_check_returncode "echo $github_token | docker login ghcr.io -u nasa --password-stdin"

cd graphql
image_name=orca-graphql
docker build -t $image_name .
docker tag $image_name ghcr.io/nasa/$image_name:$version_number
docker push ghcr.io/nasa/$image_name:$version_number
