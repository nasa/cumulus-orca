#!/bin/bash
# Sets up TF files in a consistent manner.
# todo: Is all this needed? Theoretically, should be able to delete everything referenced in the state.
set -ex

source integration_test/shared/orca-terraform.sh

cd cumulus-orca-deploy-template/cumulus-tf
# Destroy cumulus-tf via terraform
perform_terraform_command_cumulus "destroy"
cd ../..

cd cumulus-orca-deploy-template/data-persistence-tf
# Destroy data-persistence via terraform
perform_terraform_command_data_persistence "destroy"
cd ../..

cd cumulus-orca-deploy-template/rds-cluster-tf
# Destroy rds-cluster-tf via terraform
perform_terraform_command_rds_cluster "destroy"
cd ../..

cd integration_test
echo "Destroying Cumulus S3 buckets and dynamoDB table"
terraform destroy \
  -auto-approve \
  -input=false