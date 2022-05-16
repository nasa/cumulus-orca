#!/bin/bash
set -ex
export TERRAFORM_VERSION="0.13.6"
# CLI utilities
yum install -y git unzip wget zip

# AWS & Terraform
yum install -y awscli
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


#deploy rds-cluster-tf module

cd rds-cluster-tf
echo "inside rds-cluster-tf"
mv terraform.tfvars.example terraform.tfvars

RDS_CLUSTER_KEY="$bamboo_PREFIX/rds-cluster-tf/terraform.tfstate"
# Ensure remote state is configured for the deployment
echo "terraform {
        backend \"s3\" {
            bucket = \"$bamboo_PREFIX-tf-state\"
            key    = \"$RDS_CLUSTER_KEY\"
            region = \"$bamboo_AWS_DEFAULT_REGION\"
            dynamodb_table = \"$bamboo_PREFIX-tf-locks\"
    }
}" > terraform.tf

terraform fmt
# Initialize deployment
terraform init \
  -input=false

#validate the terraform files
terraform validate
# Deploy drds-cluster-tf via terraform
echo "Deploying rds-cluster-tf  module to $bamboo_DEPLOYMENT"
terraform apply \
  -auto-approve \
  -lock=false \
  -input=false \
  -var-file="terraform.tfvars" \
  -var "prefix=$bamboo_PREFIX" \
  -var "region=$bamboo_AWS_DEFAULT_REGION" \
  -var "subnets=[\"$bamboo_AWS_SUBNET_ID1\", \"$bamboo_AWS_SUBNET_ID2\"]" \
  -var "db_admin_username=$bamboo_DB_ADMIN_USERNAME" \
  -var "db_admin_password=$bamboo_DB_ADMIN_PASSWORD" \
  -var "vpc_id=$bamboo_VPC_ID" \
  -var "cluster_identifier=$bamboo_PREFIX-cumulus-rds-serverless-default-cluster" \
  -var "deletion_protection=false"\
  -var "provision_user_database=false"\
  -var "engine_version=10.14"\
  -var "permissions_boundary_arn=arn:aws:iam::$bamboo_AWS_ACCOUNT_ID:policy/$bamboo_ROLE_BOUNDARY"