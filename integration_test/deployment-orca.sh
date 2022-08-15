#!/bin/bash
set -ex

if aws s3api head-bucket --bucket ${bamboo_PREFIX}-tf-state;then
    echo "terraform state bucket already present. Using existing state file"
else
    echo "Something went wrong when checking terraform state bucket. Creating ..."
    aws s3api create-bucket --bucket ${bamboo_PREFIX}-tf-state  --region ${bamboo_AWS_DEFAULT_REGION} --create-bucket-configuration LocationConstraint=${bamboo_AWS_DEFAULT_REGION}
    
    aws s3api put-bucket-versioning \
    --bucket ${bamboo_PREFIX}-tf-state \
    --versioning-configuration Status=Enabled

    aws dynamodb create-table \
      --table-name ${bamboo_PREFIX}-tf-locks \
      --attribute-definitions AttributeName=LockID,AttributeType=S \
      --key-schema AttributeName=LockID,KeyType=HASH \
      --billing-mode PAY_PER_REQUEST \
      --region ${bamboo_AWS_DEFAULT_REGION}
fi

cd integration_test

terraform init -input=false
echo "Deploying Cumulus S3 buckets and dynamoDB table"
terraform apply \
  -auto-approve \
  -input=false

#cumulus orca template for deploying RDS cluster
cd ..
cd cumulus-orca-deploy-template

#deploy rds-cluster-tf module
cd rds-cluster-tf

# Initialize Terraform
terraform init \
  -input=false

# Deploy rds-cluster-tf via terraform
echo "Deploying rds-cluster-tf  module to $bamboo_DEPLOYMENT"
terraform apply \
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

export RDS_USER_ACCESS_SECRET_ARN=$(terraform output admin_db_login_secret_arn)
export DB_HOST_ENDPOINT=$(terraform output rds_endpoint)
export RDS_SECURITY_GROUP=$(terraform output security_group_id)

#-------------------------------------------------------------------

#deploy data persistence tf module
cd ../data-persistence-tf

# Initialize deployment
terraform init \
  -input=false

# Deploy data-persistence via terraform
echo "Deploying Cumulus data-persistence module to $bamboo_DEPLOYMENT"
terraform apply \
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
#-------------------------------------------------------------------

# script for deploying cumulus-tf module
cd ../cumulus-tf

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