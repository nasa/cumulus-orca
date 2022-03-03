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

export GIT_USER=$bamboo_SECRET_GITHUB_USER
export GIT_PASS=$bamboo_SECRET_GITHUB_TOKEN

# We need to set some git config here so deploy doesn't complain when the commit occurs.
git config --global user.email "$bamboo_SECRET_GITHUB_EMAIL"
git config --global user.name "$GIT_USER"


#configure aws 
aws configure set aws_access_key_id $bamboo_AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $bamboo_AWS_SECRET_ACCESS_KEY
aws configure set default.region $bamboo_AWS_DEFAULT_REGION

#clone cumulus orca template for deploying cumulus and orca
git clone https://git.earthdata.nasa.gov/scm/orca/cumulus-orca-deploy-template.git
cd cumulus-orca-deploy-template
git checkout $bamboo_ORCA_RELEASE_BRANCH
echo "checked out to $bamboo_ORCA_RELEASE_BRANCH branch"


#deploy rds-cluster-tf module

cd rds-cluster-tf
echo "inside rds-cluster-tf"
mv terraform.tfvars.example terraform.tfvars

RDS_CLUSTER_KEY=x"$bamboo_PREFIX/rds-cluster-tf/terraform.tfstate"
# Ensure remote state is configured for the deployment
echo "terraform {
        backend \"s3\" {
            bucket = \"$bamboo_TFSTATE_BUCKET\"
            key    = \"$RDS_CLUSTER_KEY\"
            region = \"$bamboo_AWS_DEFAULT_REGION\"
            dynamodb_table = \"$bamboo_TFSTATE_LOCK_TABLE\"
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
  -var "subnet_ids=[\"$bamboo_AWS_SUBNET_ID1\", \"$bamboo_AWS_SUBNET_ID2\"]" \
  -var "aws_region=$bamboo_AWS_DEFAULT_REGION" \
  -var "db_admin_username=$bamboo_DB_ADMIN_USERNAME" \
  -var "db_admin_password=$bamboo_DB_ADMIN_PASSWORD" \
  -var "vpc_id=$bamboo_VPC_ID" \
  -var "cluster_identifier=$bamboo_RDS_CLUSTER_ID" \
  -var "rds_user_access_secret_arn=$bamboo_RDS_USER_ACCESS_SECRET_ARN" \
  -var "rds_security_group=$bamboo_RDS_SECURITY_GROUP"\
  -var "deletion_protection=false"\
  -var "provision_user_database=false"\
  -var "permissions_boundary_arn=arn:aws:iam::$bamboo_AWS_ACCOUNT_ID:policy/$bamboo_ROLE_BOUNDARY"