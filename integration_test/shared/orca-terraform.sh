function perform_terraform_command_rds_cluster () {
  ## Performs the given Terraform command with environment variables.
  ## 
  ## Args:
  ##   $1 - The command to run in Terraform. Either "apply" or "destroy"
  echo "${1}ing cumulus-rds-tf module in $bamboo_DEPLOYMENT"
  terraform $1 \
    -auto-approve \
    -input=false \
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
}

function perform_terraform_command_ecs () {
  ## Performs the given Terraform command with environment variables.
  ## 
  ## Args:
  ##   $1 - The command to run in Terraform. Either "apply" or "destroy"
  terraform init -input=false
  echo "${1}ing ecs module in $bamboo_DEPLOYMENT"
  terraform $1 \
    -auto-approve \
    -input=false \
    -var "prefix=$bamboo_PREFIX" \
    -var "buckets=$orca_BUCKETS" \
    -var "key_name=$bamboo_PREFIX" \
    -var "rds_security_group=$RDS_SECURITY_GROUP" \
    -var "vpc_id=$VPC_ID" \
    -var "permissions_boundary_arn=arn:aws:iam::$AWS_ACCOUNT_ID:policy/$bamboo_ROLE_BOUNDARY" \
    -var "ecs_cluster_instance_subnet_ids=[\"$AWS_SUBNET_ID1\", \"$AWS_SUBNET_ID2\", \"$AWS_SUBNET_ID3\"]" \
    -var "system_bucket=$bamboo_PREFIX-internal"
}

function perform_terraform_command_orca () {
  ## Performs the given Terraform command with environment variables.
  ## 
  ## Args:
  ##   $1 - The command to run in Terraform. Either "apply" or "destroy"
  echo "${1}ing orca module in $bamboo_DEPLOYMENT"
  terraform $1 \
    -auto-approve \
    -lock=false \
    -input=false \
    -var "aws_region=$bamboo_AWS_DEFAULT_REGION" \
    -var "buckets=$orca_BUCKETS" \
    -var "lambda_subnet_ids=[\"$AWS_SUBNET_ID1\", \"$AWS_SUBNET_ID2\", \"$AWS_SUBNET_ID3\"]" \
    -var "permissions_boundary_arn=arn:aws:iam::$AWS_ACCOUNT_ID:policy/$bamboo_ROLE_BOUNDARY" \
    -var "prefix=$bamboo_PREFIX" \
    -var "system_bucket=$bamboo_PREFIX-internal" \
    -var "vpc_id=$VPC_ID" \
    -var "db_admin_username=$bamboo_DB_ADMIN_USERNAME" \
    -var "db_admin_password=$bamboo_DB_ADMIN_PASSWORD" \
    -var "db_user_password=$bamboo_DB_USER_PASSWORD" \
    -var "db_host_endpoint=$DB_HOST_ENDPOINT" \
    -var "dlq_subscription_email=rhassan@contractor.usgs.gov" \
    -var "orca_default_bucket=$bamboo_PREFIX-orca-primary" \
    -var "orca_reports_bucket_name=$bamboo_PREFIX-orca-reports" \
    -var "rds_security_group_id=$RDS_SECURITY_GROUP" \
    -var "s3_access_key=dummy" \
    -var "s3_secret_key=dummy"
}
