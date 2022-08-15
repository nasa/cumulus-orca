#!/bin/bash
set -ex
export AWS_ACCESS_KEY_ID=$bamboo_CUMULUS_AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$bamboo_CUMULUS_AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=$bamboo_CUMULUS_AWS_DEFAULT_REGION

#remove old files from bamboo as they throw error
rm *.tf

git clone --branch ${bamboo_BRANCH_NAME} --single-branch https://github.com/nasa/cumulus-orca.git && cd integration_test
echo "Cloned Orca, branch ${bamboo_BRANCH_NAME}"

#replace prefix with bamboo prefix variable
sed -e 's/PREFIX/'"$bamboo_PREFIX"'/g' buckets.tf.template > buckets.tf

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

#configuring S3 backend
echo "terraform {
  backend \"s3\" {
    bucket = \"${bamboo_PREFIX}-tf-state\"
    region = \"${bamboo_AWS_DEFAULT_REGION}\"
    key    = \"terraform.tfstate\"
    dynamodb_table = \"${bamboo_PREFIX}-tf-locks\"
  }
}" >> terraform.tf

terraform init -input=false
echo "Deploying Cumulus S3 buckets and dynamoDB table"
terraform apply \
  -auto-approve \
  -input=false

#clone cumulus orca template for deploying RDS cluster
git clone --branch $bamboo_CUMULUS_ORCA_DEPLOY_TEMPLATE_VERSION --single-branch https://git.earthdata.nasa.gov/scm/orca/cumulus-orca-deploy-template.git
cd cumulus-orca-deploy-template
echo "cloned Cumulus, branch $bamboo_CUMULUS_ORCA_DEPLOY_TEMPLATE_VERSION"

#deploy rds-cluster-tf module
cd rds-cluster-tf
echo "inside rds-cluster-tf"
mv terraform.tfvars.example terraform.tfvars

#replacing terraform.tf with proper values
sed -e 's/PREFIX/'"$bamboo_PREFIX"'/g; s/us-east-1/'"$bamboo_AWS_DEFAULT_REGION"'/g' terraform.tf.example > terraform.tf

export AWS_ACCOUNT_ID=$(aws sts get-caller-identity | jq -r '.Account')
export VPC_ID=$(aws ec2 describe-vpcs | jq -r '.Vpcs | to_entries | .[] | .value.VpcId')
export AWS_SUBNET_ID1=$(aws ec2 describe-subnets --filters "Name=availability-zone,Values=us-west-2a"| jq -r '.Subnets | .[] | select (.Tags | .[] | .Value | contains ("Private application ")) | .SubnetId ')
export AWS_SUBNET_ID2=$(aws ec2 describe-subnets --filters "Name=availability-zone,Values=us-west-2b"| jq -r '.Subnets | .[] | select (.Tags | .[] | .Value | contains ("Private application ")) | .SubnetId ')
export AWS_SUBNET_ID3=$(aws ec2 describe-subnets --filters "Name=availability-zone,Values=us-west-2c"| jq -r '.Subnets | .[] | select (.Tags | .[] | .Value | contains ("Private application ")) | .SubnetId ')

# Initialize deployment
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