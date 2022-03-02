#!/bin/bash
set -ex
export NODE_VERSION="16.x"
export TERRAFORM_VERSION="0.13.6"
# Add NodeJS and Yarn repos & update package index
# curl -sL https://rpm.nodesource.com/setup_${NODE_VERSION} | bash - 
# curl -sL https://dl.yarnpkg.com/rpm/yarn.repo | tee /etc/yum.repos.d/yarn.repo
# yum update -y
# CLI utilities
yum install -y git unzip wget zip
# Python 3 & NodeJS
# yum install -y python3-devel
# yum install -y nodejs yarn
# AWS & Terraform
yum install -y awscli
wget "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip"
unzip *.zip
chmod +x terraform
mv terraform /usr/local/bin
# # SSM SessionManager plugin
# curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/linux_64bit/session-manager-plugin.rpm" -o "session-manager-plugin.rpm"
# yum install -y session-manager-plugin.rpm


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


#deploy data persistence tf module

cd data-persistence-tf
echo "inside data persistence tf"
mv terraform.tfvars.example terraform.tfvars
mv terraform.tf.example terraform.tf



DATA_PERSISTENCE_KEY="$bamboo_PREFIX/data-persistence-tf/terraform.tfstate"
# Ensure remote state is configured for the deployment
echo "terraform {
        backend \"s3\" {
            bucket = \"$bamboo_TFSTATE_BUCKET\"
            key    = \"$DATA_PERSISTENCE_KEY\"
            region = \"$bamboo_AWS_DEFAULT_REGION\"
            dynamodb_table = \"$bamboo_TFSTATE_LOCK_TABLE\"
    }
}" > terraform.tf
echo "listing the dir"
ls
less terraform.tf
terraform fmt
less terraform.tf
# Initialize deployment
terraform init \
  -input=false

# Deploy data-persistence via terraform
echo "Deploying Cumulus data-persistence module to $bamboo_DEPLOYMENT"
terraform apply \
  -auto-approve \
  -input=false \
  -var-file="terraform.tfvars" \
  -var-file="terraform.tf" \
  -var "aws_region=$bamboo_AWS_DEFAULT_REGION" \
  -var "subnet_ids=["$bamboo_AWS_SUBNET"]" \
  -var "vpc_id=$bamboo_VPC_ID" \
  -var "rds_admin_access_secret_arn=$bamboo_RDS_ADMIN_ACCESS_SECRET_ARN" \
  -var "rds_security_group=$bamboo_RDS_SECURITY_GROUP"\
  -var "permissions_boundary_arn=arn:aws:iam::$bamboo_AWS_ACCOUNT_ID:policy/$bamboo_ROLE_BOUNDARY"














# Steps for deploying cumulus
# cd ../cumulus-tf
# # Ensure remote state is configured for the deployment
# echo "terraform {
#   backend \"s3\" {
#     bucket = \"$TFSTATE_BUCKET\"
#     key    = \"$DEPLOYMENT/cumulus/terraform.tfstate\"
#     region = \"$AWS_REGION\"
#     dynamodb_table = \"$TFSTATE_LOCK_TABLE\"
#   }
# }" >> ci_backend.tf

# # Initialize deployment
# ../terraform init \
#   -input=false

# # Deploy cumulus-tf via terraform
# echo "Deploying Cumulus example to $DEPLOYMENT"
# ../terraform apply \
#   -auto-approve \
#   -input=false \
#   -var-file="../deployments/cumulus/$BASE_VAR_FILE" \
#   -var-file="../deployments/cumulus/$DEPLOYMENT.tfvars" \
#   -var "cumulus_message_adapter_lambda_layer_version_arn=arn:aws:lambda:us-east-1:$AWS_ACCOUNT_ID:layer:Cumulus_Message_Adapter:$CMA_LAYER_VERSION" \
#   -var "cmr_username=$CMR_USERNAME" \
#   -var "cmr_password=$CMR_PASSWORD" \
#   -var "cmr_client_id=cumulus-core-$DEPLOYMENT" \
#   -var "cmr_provider=CUMULUS" \
#   -var "cmr_environment=UAT" \
#   -var "csdap_client_id=$CSDAP_CLIENT_ID" \
#   -var "csdap_client_password=$CSDAP_CLIENT_PASSWORD" \
#   -var "launchpad_passphrase=$LAUNCHPAD_PASSPHRASE" \
#   -var "data_persistence_remote_state_config={ region: \"$AWS_REGION\", bucket: \"$TFSTATE_BUCKET\", key: \"$DATA_PERSISTENCE_KEY\" }" \
#   -var "region=$AWS_REGION" \
#   -var "vpc_id=$VPC_ID" \
#   -var "lambda_subnet_ids=[$AWS_LAMBDA_SUBNET]" \
#   -var "urs_client_id=$EARTHDATA_CLIENT_ID" \
#   -var "urs_client_password=$EARTHDATA_CLIENT_PASSWORD" \
#   -var "token_secret=$TOKEN_SECRET" \
#   -var "permissions_boundary_arn=arn:aws:iam::$AWS_ACCOUNT_ID:policy/$ROLE_BOUNDARY" \
#   -var "pdr_node_name_provider_bucket=$PDR_NODE_NAME_PROVIDER_BUCKET" \
#   -var "rds_admin_access_secret_arn=$RDS_ADMIN_ACCESS_SECRET_ARN" \
#   -var "orca_db_user_password=$ORCA_DATABASE_USER_PASSWORD" \