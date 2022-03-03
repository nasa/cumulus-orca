#!/bin/bash
set -ex
export TERRAFORM_VERSION="0.13.6"
# CLI utilities
yum install -y git unzip wget zip

# AWS & Terraform
yum install -y python3-devel awscli
wget "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip"
unzip *.zip
chmod +x terraform
mv terraform /usr/local/bin

#configure aws 
aws configure set aws_access_key_id $bamboo_AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $bamboo_AWS_SECRET_ACCESS_KEY
aws configure set default.region $bamboo_AWS_DEFAULT_REGION

#clone cumulus orca template for deploying cumulus and orca
git clone https://git.earthdata.nasa.gov/scm/orca/cumulus-orca-deploy-template.git
cd cumulus-orca-deploy-template
git checkout $bamboo_ORCA_RELEASE_BRANCH
echo "checked out to $bamboo_ORCA_RELEASE_BRANCH branch"


#deploy data persistence tf module

cd data-persistence-tf
echo "inside data persistence tf"
mv terraform.tfvars.example terraform.tfvars

DATA_PERSISTENCE_KEY="$bamboo_PREFIX/data-persistence-tf/terraform.tfstate"
# Ensure remote state is configured for the deployment
echo "terraform {
        backend \"s3\" {
            bucket = \"$bamboo_TFSTATE_BUCKET\"
            key    = \"$DATA_PERSISTENCE_KEY\"
            region = \"$bamboo_AWS_DEFAULT_REGION\"
            dynamodb_table = \"$bamboo_TFSTATE_LOCK_TABLE\"
    }
}" > terraform.tf

terraform fmt
# Initialize deployment
terraform init \
  -input=false

#validate the terraform files
terraform validate
# Deploy data-persistence via terraform
echo "Deploying Cumulus data-persistence module to $bamboo_DEPLOYMENT"
terraform apply \
  -auto-approve \
  -lock=false \
  -input=false \
  -var-file="terraform.tfvars" \
  -var "prefix=$bamboo_PREFIX" \
  -var "aws_region=$bamboo_AWS_DEFAULT_REGION" \
  -var "subnet_ids=[\"$bamboo_AWS_SUBNET_ID1\"]" \
  -var "vpc_id=$bamboo_VPC_ID" \
  -var "rds_user_access_secret_arn=$bamboo_RDS_USER_ACCESS_SECRET_ARN" \
  -var "rds_security_group=$bamboo_RDS_SECURITY_GROUP"\
  -var "permissions_boundary_arn=arn:aws:iam::$bamboo_AWS_ACCOUNT_ID:policy/$bamboo_ROLE_BOUNDARY"

# script for deploying cumulus-tf module
cd ..
cd ..
git clone https://github.com/nasa/cumulus-orca.git
cd cumulus-orca
git checkout $bamboo_ORCA_TEST_BRANCH
./bin/build_tasks.sh
cd ..
cd cumulus-orca-deploy-template/cumulus-tf
echo "inside cumulus-tf module"
mv terraform.tfvars.example terraform.tfvars

CUMULUS_KEY="$bamboo_PREFIX/cumulus/terraform.tfstate"
# Ensure remote state is configured for the deployment
echo "terraform {
        backend \"s3\" {
            bucket = \"$bamboo_TFSTATE_BUCKET\"
            key    = \"$CUMULUS_KEY\"
            region = \"$bamboo_AWS_DEFAULT_REGION\"
            dynamodb_table = \"$bamboo_TFSTATE_LOCK_TABLE\"
    }
}" > terraform.tf

terraform fmt
# Initialize deployment
terraform init \
  -input=false

#validate the terraform files
terraform validate
# Deploy data-persistence via terraform
echo "Deploying Cumulus data-persistence module to $bamboo_DEPLOYMENT"
terraform apply \
  -auto-approve \
  -lock=false \
  -input=false \
  -var-file="terraform.tfvars" \
  -var "cumulus_message_adapter_version=$bamboo_CMA_LAYER_VERSION" \
  -var "cmr_username=$bamboo_CMR_USERNAME" \
  -var "cmr_password=$bamboo_CMR_PASSWORD" \
  -var "cmr_client_id=cumulus-core-$bamboo_DEPLOYMENT" \
  -var "cmr_provider=CUMULUS" \
  -var "cmr_environment=UAT" \
  -var "data_persistence_remote_state_config={ region: \"$bamboo_AWS_DEFAULT_REGION\", bucket: \"$TFSTATE_BUCKET\", key: \"$DATA_PERSISTENCE_KEY\" }" \
  -var "region=$bamboo_AWS_DEFAULT_REGION" \
  -var "vpc_id=$bamboo_VPC_ID" \
  -var "lambda_subnet_ids=[\"$bamboo_AWS_SUBNET_ID1\", \"$bamboo_AWS_SUBNET_ID2\"]" \
  -var "urs_client_id=$bamboo_EARTHDATA_CLIENT_ID" \
  -var "urs_client_password=$bamboo_EARTHDATA_CLIENT_PASSWORD" \
  -var "urs_url=https://uat.urs.earthdata.nasa.gov" \
  -var "api_users=[\"bhazuka\", \"andrew.dorn\", \"rizbi.hassan\", \"scott.saxon\"]" \
  -var "cmr_oauth_provider=$bamboo_CMR_OAUTH_PROVIDER" \
  -var "key_name=$bamboo_PREFIX" \
  -var "prefix=$bamboo_PREFIX" \
  -var "permissions_boundary_arn=arn:aws:iam::$bamboo_AWS_ACCOUNT_ID:policy/$bamboo_ROLE_BOUNDARY"
  -var "db_user_password=$bamboo_PREFIX" \
  -var "orca_default_bucket=rizbi-bamboo-new-orca-primary" \ #replace this
  -var "db_admin_password=$bamboo_DB_ADMIN_PASSWORD" \
  -var "db_host_endpoint=$bamboo_RDS_ENDPOINT"
  -var "rds_security_group_id=$bamboo_RDS_SECURITY_GROUP"
