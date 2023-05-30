#!/bin/bash
set -ex

source integration_test/shared/orca-terraform.sh

export AWS_ACCESS_KEY_ID=$bamboo_CUMULUS_AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$bamboo_CUMULUS_AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=$bamboo_CUMULUS_AWS_DEFAULT_REGION

cd integration_test
echo "Deploying Cumulus S3 buckets and dynamoDB table"
terraform apply \
  -auto-approve \
  -input=false
cd ..

# Deploy rds-cluster-tf via terraform
cd cumulus-orca-deploy-template/rds-cluster-tf
perform_terraform_command_rds_cluster "apply"

export RDS_USER_ACCESS_SECRET_ARN=$(terraform output admin_db_login_secret_arn)
export DB_HOST_ENDPOINT=$(terraform output rds_endpoint)
export RDS_SECURITY_GROUP=$(terraform output security_group_id)
#-------------------------------------------------------------------

# Deploy data-persistence via terraform
cd ../data-persistence-tf
perform_terraform_command_data_persistence "apply"
#-------------------------------------------------------------------

# Deploy cumulus-tf via terraform
cd ../cumulus-tf
perform_terraform_command_cumulus "apply"