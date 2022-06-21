#!/bin/bash
set -ex

export AWS_ACCESS_KEY_ID=$bamboo_AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$bamboo_AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=$bamboo_AWS_DEFAULT_REGION

#remove old files from bamboo as they throw error
rm *.tf
#deploy the S3 buckets and dynamoDB table first
git clone --branch feature/ORCA-test-bamboo --single-branch https://github.com/nasa/cumulus-orca.git && cd integration_test
#replace prefix with bamboo prefix variable
sed -e 's/PREFIX/'"$bamboo_PREFIX"'/g' buckets.tf.template > buckets.tf

if ! aws s3 cp s3://$bamboo_PREFIX-tf-state/buckets-tf/terraform.tfstate .;then
    echo "terraform state file not present in S3. Creating the buckets and dynamoDB table..."
else
    echo "Terraform state file found in S3 bucket. Using S3 remote backend"
fi

terraform init -input=false
echo "Deploying S3  buckets and dynamoDB table"
terraform apply \
  -auto-approve \
  -input=false

#copy terraform state file to the created tf-state bucket
aws s3 cp terraform.tfstate s3://$bamboo_PREFIX-tf-state/buckets-tf/terraform.tfstate

#clone cumulus orca template for deploying RDS cluster
git clone --branch $bamboo_CUMULUS_ORCA_DEPLOY_TEMPLATE_VERSION --single-branch https://git.earthdata.nasa.gov/scm/orca/cumulus-orca-deploy-template.git
cd cumulus-orca-deploy-template
echo "checked out to $bamboo_CUMULUS_ORCA_DEPLOY_TEMPLATE_VERSION branch"

#deploy rds-cluster-tf module
cd rds-cluster-tf
echo "inside rds-cluster-tf"
mv terraform.tfvars.example terraform.tfvars

#replacing terraform.tf with proper values
sed -e 's/PREFIX/'"$bamboo_PREFIX"'/g; s/us-east-1/'"$bamboo_AWS_DEFAULT_REGION"'/g' terraform.tf.example > terraform.tf

# Initialize deployment
terraform init \
  -input=false

# Deploy drds-cluster-tf via terraform
echo "Deploying rds-cluster-tf  module to $bamboo_DEPLOYMENT"
terraform apply \
  -auto-approve \
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
  -var "engine_version=$bamboo_RDS_ENGINE_VERSION" \
  -var "permissions_boundary_arn=arn:aws:iam::$bamboo_AWS_ACCOUNT_ID:policy/$bamboo_ROLE_BOUNDARY"