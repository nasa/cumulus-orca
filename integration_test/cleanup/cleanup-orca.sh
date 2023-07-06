#!/bin/bash
# Sets up TF files in a consistent manner.
# todo: Is all this needed? Theoretically, should be able to delete everything referenced in the state.
set -ex

source integration_test/shared/orca-terraform.sh

# Destroy orca via terraform
cd cumulus-orca
perform_terraform_command_orca "destroy"
cd ..

cd cumulus-orca-deploy-template/ecs-standalone-tf
# Destroy ecs-standalone-tf via terraform
perform_terraform_command_ecs "destroy"
cd ../..

cd cumulus-orca-deploy-template/terraform-aws-cumulus/tf-modules/cumulus-rds-tf
# Destroy rds via terraform
perform_terraform_command_rds_cluster "destroy"
cd ../../../..

cd integration_test
echo "Destroying Cumulus S3 buckets and dynamoDB table"
terraform destroy \
  -auto-approve \
  -input=false
cd ..

aws rds delete-db-cluster-snapshot --db-cluster-snapshot-identifier ${bamboo_PREFIX}-cumulus-rds-serverless-default-cluster-final-snapshot
