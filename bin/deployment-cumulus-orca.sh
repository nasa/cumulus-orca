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

export AWS_ACCESS_KEY_ID=$bamboo_AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$bamboo_AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=$bamboo_AWS_DEFAULT_REGION

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
            bucket = \"$bamboo_PREFIX-tf-state\"
            key    = \"$DATA_PERSISTENCE_KEY\"
            region = \"$bamboo_AWS_DEFAULT_REGION\"
            dynamodb_table = \"$bamboo_PREFIX-tf-locks\"
    }
}" > terraform.tf

terraform fmt
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
cd ../.. && git clone https://github.com/nasa/cumulus-orca.git
cd cumulus-orca && git checkout $bamboo_ORCA_TEST_BRANCH
# run the build script to create lambda zip files
./bin/build_tasks.sh
cd ../cumulus-orca-deploy-template/cumulus-tf
echo "inside cumulus-tf module"
mv terraform.tfvars.example terraform.tfvars

CUMULUS_KEY="$bamboo_PREFIX/cumulus/terraform.tfstate"

# adding variables to orca_variables.tf file
cat << EOF > orca_variables.tf

variable "orca_reports_bucket_name" {
  type        = string
  description = "The name of the bucket to store s3 inventory reports."
}

variable "db_host_endpoint" {
  type        = string
  description = "Database host endpoint to connect to."
}

## OPTIONAL

variable "db_admin_password" {
  description = "Password for RDS database administrator authentication"
  type        = string
}

variable "db_user_password" {
  description = "Password for RDS database user authentication"
  type        = string
}

variable "orca_default_bucket" {
  description = "Default ORCA S3 Glacier bucket to use if no overrides exist."
  type        = string
}

variable "rds_security_group_id" {
  type        = string
  description = "Cumulus' RDS Security Group's ID."
}

## OPTIONAL

variable "dlq_subscription_email" {
  type        = string
  description = "The email to notify users when messages are received in dead letter SQS queue due to restore failure. Sends one email until the dead letter queue is emptied."
}

variable "s3_access_key" {
  type        = string
  description = "Access key for communicating with Orca S3 buckets."
}

variable "s3_secret_key" {
  type        = string
  description = "Secret key for communicating with Orca S3 buckets."
}
EOF


# adding buckets variable to a new file
echo "buckets = {
        default_orca = {
          name = \"$bamboo_PREFIX-orca-primary\"
          type = \"orca\"
          },
        l0archive = {
          name = \"$bamboo_PREFIX-level0\"
          type = \"private\"
          },
        internal = {
            name = \"$bamboo_PREFIX-internal\"
            type = \"internal\"
          },
        private = {
            name = \"$bamboo_PREFIX-private\"
            type = \"private\"
          },
        protected = {
          name = \"$bamboo_PREFIX-protected\"
          type = \"protected\"
        },
        public = {
          name = \"$bamboo_PREFIX-public\"
          type = \"public\"
        },
        provider = {
          name = \"orca-sandbox-s3-provider\"
          type = \"provider\"
        }
      }" > buckets.tfvars

# Ensure remote state is configured for the deployment
echo "terraform {
        backend \"s3\" {
            bucket = \"$bamboo_PREFIX-tf-state\"
            key    = \"$CUMULUS_KEY\"
            region = \"$bamboo_AWS_DEFAULT_REGION\"
            dynamodb_table = \"$bamboo_PREFIX-tf-locks\"
    }
}" > terraform.tf
terraform fmt
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
  -var-file="buckets.tfvars" \
  -var "cumulus_message_adapter_version="$bamboo_CMA_LAYER_VERSION"" \
  -var "cmr_username=$bamboo_CMR_USERNAME" \
  -var "cmr_password=$bamboo_CMR_PASSWORD" \
  -var "cmr_client_id=cumulus-core-$bamboo_DEPLOYMENT" \
  -var "cmr_provider=CUMULUS" \
  -var "cmr_environment=UAT" \
  -var "data_persistence_remote_state_config={ region: \"$bamboo_AWS_DEFAULT_REGION\", bucket: \"$bamboo_PREFIX-tf-state\", key: \"$DATA_PERSISTENCE_KEY\" }" \
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
  -var "permissions_boundary_arn=arn:aws:iam::$bamboo_AWS_ACCOUNT_ID:policy/$bamboo_ROLE_BOUNDARY" \
  -var "db_user_password=$bamboo_PREFIX" \
  -var "orca_default_bucket=$bamboo_PREFIX-orca-primary" \
  -var "db_admin_password=$bamboo_DB_ADMIN_PASSWORD" \
  -var "db_host_endpoint=$bamboo_DB_HOST_ENDPOINT" \
  -var "rds_security_group_id=$bamboo_RDS_SECURITY_GROUP" \
  -var "dlq_subscription_email=$bamboo_DLQ_SUBSCRIPTION_EMAIL" \
  -var "s3_access_key=$bamboo_S3_ACCESS_KEY" \
  -var "s3_secret_key=$bamboo_S3_SECRET_KEY" \
  -var "orca_reports_bucket_name=$bamboo_ORCA_REPORTS_BUCKET_NAME"