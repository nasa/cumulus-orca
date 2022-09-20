#!/bin/bash
# Sets up TF files in a consistent manner.
set -ex
cwd=$(pwd)

export AWS_ACCESS_KEY_ID=$bamboo_DR_AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$bamboo_DR_AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=$bamboo_AWS_DEFAULT_REGION

#remove old files from bamboo as they throw error
rm *.tf

git clone --branch ${bamboo_BRANCH_NAME} --single-branch https://github.com/nasa/cumulus-orca.git
cd integration_test
echo "Cloned Orca, branch ${bamboo_BRANCH_NAME}"
#replace prefix with bamboo prefix variable
sed -e 's/PREFIX/'"$bamboo_PREFIX"'/g' dr-buckets.tf.template > dr-buckets.tf

#configuring S3 backend
echo "terraform {
  backend \"s3\" {
    bucket = \"${bamboo_PREFIX}-dr-tf-state\"
    region = \"${bamboo_AWS_DEFAULT_REGION}\"
    key    = \"terraform.tfstate\"
    dynamodb_table = \"${bamboo_PREFIX}-dr-tf-locks\"
  }
}" >> terraform.tf

cd "${cwd}"