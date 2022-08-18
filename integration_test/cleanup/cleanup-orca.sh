#!/bin/bash
# Sets up TF files in a consistent manner.
# todo: Is all this needed? Theoretically, should be able to delete everything referenced in the state.
set -ex

cd cumulus-orca-deploy-template/cumulus-tf

# Destroy cumulus-tf via terraform
echo "Destroying Cumulus tf module in $bamboo_DEPLOYMENT"
terraform destroy \
  -auto-approve \
  -lock=false \
  -input=false \
  -var-file="terraform.tfvars" \
  -var "data_persistence_remote_state_config={ region: \"$bamboo_AWS_DEFAULT_REGION\", bucket: \"$bamboo_PREFIX-tf-state\", key: \"$bamboo_PREFIX/data-persistence/terraform.tfstate\" }" \
  -var "region=$bamboo_AWS_DEFAULT_REGION" \
  -var "vpc_id=$VPC_ID" \
  -var "system_bucket=$bamboo_PREFIX-internal" \
  -var "ecs_cluster_instance_subnet_ids=[\"$AWS_SUBNET_ID1\", \"$AWS_SUBNET_ID2\", \"$AWS_SUBNET_ID3\"]" \
  -var "lambda_subnet_ids=[\"$AWS_SUBNET_ID1\", \"$AWS_SUBNET_ID2\", \"$AWS_SUBNET_ID3\"]" \
  -var "urs_client_id=$bamboo_EARTHDATA_CLIENT_ID" \
  -var "urs_client_password=$bamboo_EARTHDATA_CLIENT_PASSWORD" \
  -var "urs_url=https://uat.urs.earthdata.nasa.gov" \
  -var "api_users=[\"bhazuka\", \"andrew.dorn\", \"rizbi.hassan\", \"scott.saxon\"]" \
  -var "cmr_oauth_provider=$bamboo_CMR_OAUTH_PROVIDER" \
  -var "key_name=$bamboo_PREFIX" \
  -var "prefix=$bamboo_PREFIX" \
  -var "permissions_boundary_arn=arn:aws:iam::$AWS_ACCOUNT_ID:policy/$bamboo_ROLE_BOUNDARY" \
  -var "db_user_password=$bamboo_DB_USER_PASSWORD" \
  -var "orca_default_bucket=$bamboo_PREFIX-orca-primary" \
  -var "db_admin_username=$bamboo_DB_ADMIN_USERNAME" \
  -var "db_admin_password=$bamboo_DB_ADMIN_PASSWORD" \
  -var "db_host_endpoint=$DB_HOST_ENDPOINT" \
  -var "rds_security_group_id=$RDS_SECURITY_GROUP"
cd ../..

cd cumulus-orca-deploy-template/data-persistence-tf

# Destroy data-persistence via terraform
echo "Destroying Cumulus data-persistence module in $bamboo_DEPLOYMENT"
terraform destroy \
  -auto-approve \
  -input=false \
  -var-file="terraform.tfvars" \
  -var "prefix=$bamboo_PREFIX" \
  -var "aws_region=$bamboo_AWS_DEFAULT_REGION" \
  -var "subnet_ids=[\"$AWS_SUBNET_ID1\"]" \
  -var "vpc_id=$VPC_ID" \
  -var "rds_user_access_secret_arn=$RDS_USER_ACCESS_SECRET_ARN" \
  -var "rds_security_group=$RDS_SECURITY_GROUP"\
  -var "permissions_boundary_arn=arn:aws:iam::$AWS_ACCOUNT_ID:policy/$bamboo_ROLE_BOUNDARY"
cd ../..

cd cumulus-orca-deploy-template/rds-cluster-tf

# Destroy rds-cluster-tf via terraform
echo "Destroying rds-cluster-tf module in $bamboo_DEPLOYMENT"
terraform destroy \
  -auto-approve \
  -input=false \
  -var-file="terraform.tfvars" \
  -var "prefix=$bamboo_PREFIX" \
  -var "region=$bamboo_AWS_DEFAULT_REGION" \
  -var "subnets=[\"$AWS_SUBNET_ID1\", \"$AWS_SUBNET_ID2\", \"$AWS_SUBNET_ID3\"]" \
  -var "db_admin_username=$bamboo_DB_ADMIN_USERNAME" \
  -var "db_admin_password=$bamboo_DB_ADMIN_PASSWORD" \
  -var "vpc_id=$VPC_ID" \
  -var "cluster_identifier=$bamboo_PREFIX-cumulus-rds-serverless-default-cluster" \
  -var "deletion_protection=false"\
  -var "provision_user_database=false"\
  -var "engine_version=$bamboo_RDS_ENGINE_VERSION" \
  -var "permissions_boundary_arn=arn:aws:iam::$AWS_ACCOUNT_ID:policy/$bamboo_ROLE_BOUNDARY"

# todo: Do we need the exports from deployment-orca.sh?
cd ../..
cd integration_test
echo "Destroying Cumulus S3 buckets and dynamoDB table"
terraform destroy \
  -auto-approve \
  -input=false