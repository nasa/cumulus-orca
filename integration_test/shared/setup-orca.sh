#!/bin/bash
# Sets up TF files in a consistent manner.
set -ex

export AWS_ACCESS_KEY_ID=$bamboo_CUMULUS_AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$bamboo_CUMULUS_AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=$bamboo_CUMULUS_AWS_DEFAULT_REGION

#remove old files from bamboo as they throw error
rm *.tf

git clone --branch ${bamboo_BRANCH_NAME} --single-branch https://github.com/nasa/cumulus-orca.git
echo "Cloned Orca, branch ${bamboo_BRANCH_NAME}"

cd integration_test
#replace prefix with bamboo prefix variable
sed -e 's/PREFIX/'"$bamboo_PREFIX"'/g' buckets.tf.template > buckets.tf

#configuring S3 backend
echo "terraform {
  backend \"s3\" {
    bucket = \"${bamboo_PREFIX}-tf-state\"
    region = \"${bamboo_AWS_DEFAULT_REGION}\"
    key    = \"terraform.tfstate\"
    dynamodb_table = \"${bamboo_PREFIX}-tf-locks\"
  }
}" >> terraform.tf

#clone cumulus orca template for deploying RDS cluster
cd ..
git clone --branch $bamboo_CUMULUS_ORCA_DEPLOY_TEMPLATE_VERSION --single-branch https://git.earthdata.nasa.gov/scm/orca/cumulus-orca-deploy-template.git
echo "cloned Cumulus, branch $bamboo_CUMULUS_ORCA_DEPLOY_TEMPLATE_VERSION"

#rds-cluster-tf module
cd cumulus-orca-deploy-template/rds-cluster-tf
echo "inside rds-cluster-tf"
mv terraform.tfvars.example terraform.tfvars

#replacing terraform.tf and environment variables with proper values
sed -e 's/PREFIX/'"$bamboo_PREFIX"'/g; s/us-east-1/'"$bamboo_AWS_DEFAULT_REGION"'/g' terraform.tf.example > terraform.tf
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity | jq -r '.Account')
export VPC_ID=$(aws ec2 describe-vpcs | jq -r '.Vpcs | to_entries | .[] | .value.VpcId')
export AWS_SUBNET_ID1=$(aws ec2 describe-subnets --filters "Name=availability-zone,Values=us-west-2a"| jq -r '.Subnets | .[] | select (.Tags | .[] | .Value | contains ("Private application ")) | .SubnetId ')
export AWS_SUBNET_ID2=$(aws ec2 describe-subnets --filters "Name=availability-zone,Values=us-west-2b"| jq -r '.Subnets | .[] | select (.Tags | .[] | .Value | contains ("Private application ")) | .SubnetId ')
export AWS_SUBNET_ID3=$(aws ec2 describe-subnets --filters "Name=availability-zone,Values=us-west-2c"| jq -r '.Subnets | .[] | select (.Tags | .[] | .Value | contains ("Private application ")) | .SubnetId ')

#data persistence tf module
cd ../data-persistence-tf
mv terraform.tfvars.example terraform.tfvars
#replacing terraform.tf with proper values
sed -e 's/PREFIX/'"$bamboo_PREFIX"'/g; s/us-east-1/'"$bamboo_AWS_DEFAULT_REGION"'/g' terraform.tf.example > terraform.tf

cd ../cumulus-tf
#replacing .tf files with proper values
sed 's/PREFIX/'"$bamboo_PREFIX"'/g' terraform.tfvars.example > terraform.tfvars
sed -e 's/PREFIX/'"$bamboo_PREFIX"'/g; s/us-east-1/'"$bamboo_AWS_DEFAULT_REGION"'/g' terraform.tf.example > terraform.tf
