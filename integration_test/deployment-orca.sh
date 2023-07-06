#!/bin/bash
set -ex

source integration_test/shared/orca-terraform.sh

export AWS_ACCESS_KEY_ID=$bamboo_CUMULUS_AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$bamboo_CUMULUS_AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=$bamboo_CUMULUS_AWS_DEFAULT_REGION

cd integration_test
echo "Deploying Cumulus S3 buckets"
terraform apply \
  -auto-approve \
  -input=false
cd ..

# Deploy cumulus-rds-tf via terraform
cd cumulus-orca-deploy-template/terraform-aws-cumulus/tf-modules/cumulus-rds-tf
perform_terraform_command_rds_cluster "apply"

export DB_HOST_ENDPOINT=$(terraform output rds_endpoint)
export RDS_SECURITY_GROUP=$(terraform output security_group_id)
cd ../../../..
#-------------------------------------------------------------------

# Deploy ecs-standalone-tf
cd cumulus-orca-deploy-template/ecs-standalone-tf
perform_terraform_command_ecs "apply"
cd ../..

# Deploy orca via terraform
perform_terraform_command_orca "apply"