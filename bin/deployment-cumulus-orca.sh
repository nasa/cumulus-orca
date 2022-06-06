#!/bin/bash
set -ex

export AWS_ACCESS_KEY_ID=$bamboo_AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$bamboo_AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=$bamboo_AWS_DEFAULT_REGION

#clone cumulus orca template for deploying cumulus and orca
git clone --branch $bamboo_ORCA_RELEASE_BRANCH --single-branch https://git.earthdata.nasa.gov/scm/orca/cumulus-orca-deploy-template.git
cd cumulus-orca-deploy-template
echo "checked out to $bamboo_ORCA_RELEASE_BRANCH branch"


#deploy data persistence tf module
cd data-persistence-tf
mv terraform.tfvars.example terraform.tfvars
#replacing terraform.tf with proper values
sed -e 's/PREFIX/'"$bamboo_PREFIX"'/g; s/us-east-1/'"$bamboo_AWS_DEFAULT_REGION"'/g' terraform.tf.example > terraform.tf

# Initialize deployment
terraform init \
  -input=false

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
# clone cumulus-orca repo and run build_tasks.sh to create the lambda zip files first
cd ../.. && git clone --branch $bamboo_ORCA_TEST_BRANCH --single-branch https://github.com/nasa/cumulus-orca.git
cd cumulus-orca
# run the build script to create lambda zip files
./bin/build_tasks.sh
cd ../cumulus-orca-deploy-template/cumulus-tf

CUMULUS_KEY="$bamboo_PREFIX/cumulus/terraform.tfstate"

#replacing .tf files with proper values
sed 's/PREFIX/'"$bamboo_PREFIX"'/g' terraform.tfvars.example > terraform.tfvars
sed -e 's/PREFIX/'"$bamboo_PREFIX"'/g; s/us-east-1/'"$bamboo_AWS_DEFAULT_REGION"'/g' terraform.tf.example > terraform.tf

# Initialize deployment
terraform init \
  -input=false

# Deploy cumulus-tf via terraform
echo "Deploying Cumulus tf module to $bamboo_DEPLOYMENT"
terraform apply \
  -auto-approve \
  -lock=false \
  -input=false \
  -var-file="terraform.tfvars" \
  -var "cmr_username=$bamboo_CMR_USERNAME" \
  -var "cmr_password=$bamboo_CMR_PASSWORD" \
  -var "cmr_client_id=cumulus-core-$bamboo_DEPLOYMENT" \
  -var "cmr_provider=CUMULUS" \
  -var "cmr_environment=UAT" \
  -var "data_persistence_remote_state_config={ region: \"$bamboo_AWS_DEFAULT_REGION\", bucket: \"$bamboo_PREFIX-tf-state\", key: \"$bamboo_PREFIX/data-persistence/terraform.tfstate\" }" \
  -var "region=$bamboo_AWS_DEFAULT_REGION" \
  -var "vpc_id=$bamboo_VPC_ID" \
  -var "system_bucket=$bamboo_PREFIX-internal" \
  -var "lambda_subnet_ids=[\"$bamboo_AWS_SUBNET_ID1\", \"$bamboo_AWS_SUBNET_ID2\"]" \
  -var "urs_client_id=$bamboo_EARTHDATA_CLIENT_ID" \
  -var "urs_client_password=$bamboo_EARTHDATA_CLIENT_PASSWORD" \
  -var "urs_url=https://uat.urs.earthdata.nasa.gov" \
  -var "api_users=[\"bhazuka\", \"andrew.dorn\", \"rizbi.hassan\", \"scott.saxon\"]" \
  -var "cmr_oauth_provider=$bamboo_CMR_OAUTH_PROVIDER" \
  -var "key_name=$bamboo_PREFIX" \
  -var "prefix=$bamboo_PREFIX" \
  -var "permissions_boundary_arn=arn:aws:iam::$bamboo_AWS_ACCOUNT_ID:policy/$bamboo_ROLE_BOUNDARY" \
  -var "db_user_password=$bamboo_DB_USER_PASSWORD" \
  -var "orca_default_bucket=$bamboo_PREFIX-orca-primary" \
  -var "db_admin_password=$bamboo_DB_ADMIN_PASSWORD" \
  -var "db_host_endpoint=$bamboo_DB_HOST_ENDPOINT" \
  -var "rds_security_group_id=$bamboo_RDS_SECURITY_GROUP"