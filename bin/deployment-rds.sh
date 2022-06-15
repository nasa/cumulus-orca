#!/bin/bash
set -ex

export AWS_ACCESS_KEY_ID=$bamboo_AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$bamboo_AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=$bamboo_AWS_DEFAULT_REGION

#deploy the S3 buckets and dynamoDB table first
cat << EOF > resources.tf.template
# create buckets
resource "aws_s3_bucket" "tf-state" {
  bucket = "PREFIX-tf-state"
}
resource "aws_s3_bucket" "internal" {
  bucket = "PREFIX-internal"
}
resource "aws_s3_bucket" "public" {
  bucket = "PREFIX-public"
}
resource "aws_s3_bucket" "private" {
  bucket = "PREFIX-private"
}
resource "aws_s3_bucket" "level0" {
  bucket = "PREFIX-level0"
}
resource "aws_s3_bucket" "orca-primary" {
  bucket = "PREFIX-orca-primary"
}
resource "aws_s3_bucket" "protected" {
  bucket = "PREFIX-protected"
}
resource "aws_dynamodb_table" "tf-locks" {
  name           = "PREFIX-tf-locks"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"
  attribute {
    name = "LockID"
    type = "S"
 }
}
EOF

#remove old files from bamboo as they throw error
rm *.tf
#replace prefix with bamboo prefix variable
sed -e 's/PREFIX/'"$bamboo_PREFIX"'/g' resources.tf.template > resources.tf

if ! aws s3 cp terraform.tfstate s3://$bamboo_PREFIX-tf-state/terraform.tfstate .;then
    echo "state file not present. Creating the buckets..."
else
    echo "State file found. Using S3 remote backend"
fi

terraform init -input=false
echo "Deploying S3  buckets and dynamoDB table"
terraform apply \
  -auto-approve \
  -lock=false \
  -input=false

#copy the terraform state file to the created tf-state bucket
aws s3 cp terraform.tfstate s3://$bamboo_PREFIX-tf-state/terraform.tfstate

# Check remote state is configured for the deployment
echo "terraform {
        backend \"s3\" {
            bucket = \"$bamboo_PREFIX-tf-state\"
            region = \"$bamboo_AWS_DEFAULT_REGION\"
            dynamodb_table = \"$bamboo_PREFIX-tf-locks\"
    }
}"
# terraform init
# #remove everything except the terraform state bucket
# terraform state rm aws_s3_bucket.tf-state

#  terraform destroy \
#   -auto-approve \
#   -lock=false \
#   -input=false

# aws s3 rm s3://$bamboo_PREFIX-tf-state --recursive
# aws s3api delete-bucket --bucket $bamboo_PREFIX-tf-state



# #clone cumulus orca template for deploying cumulus and orca
# git clone --branch $bamboo_CUMULUS_ORCA_DEPLOY_TEMPLATE_VERSION --single-branch https://git.earthdata.nasa.gov/scm/orca/cumulus-orca-deploy-template.git
# cd cumulus-orca-deploy-template
# echo "checked out to $bamboo_CUMULUS_ORCA_DEPLOY_TEMPLATE_VERSION branch"


# #deploy rds-cluster-tf module

# cd rds-cluster-tf
# echo "inside rds-cluster-tf"
# mv terraform.tfvars.example terraform.tfvars

# #replacing terraform.tf with proper values
# sed -e 's/PREFIX/'"$bamboo_PREFIX"'/g; s/us-east-1/'"$bamboo_AWS_DEFAULT_REGION"'/g' terraform.tf.example > terraform.tf

# # Initialize deployment
# terraform init \
#   -input=false

# # Deploy drds-cluster-tf via terraform
# echo "Deploying rds-cluster-tf  module to $bamboo_DEPLOYMENT"
# terraform apply \
#   -auto-approve \
#   -lock=false \
#   -input=false \
#   -var-file="terraform.tfvars" \
#   -var "prefix=$bamboo_PREFIX" \
#   -var "region=$bamboo_AWS_DEFAULT_REGION" \
#   -var "subnets=[\"$bamboo_AWS_SUBNET_ID1\", \"$bamboo_AWS_SUBNET_ID2\"]" \
#   -var "db_admin_username=$bamboo_DB_ADMIN_USERNAME" \
#   -var "db_admin_password=$bamboo_DB_ADMIN_PASSWORD" \
#   -var "vpc_id=$bamboo_VPC_ID" \
#   -var "cluster_identifier=$bamboo_PREFIX-cumulus-rds-serverless-default-cluster" \
#   -var "deletion_protection=false"\
#   -var "provision_user_database=false"\
#   -var "engine_version=$bamboo_RDS_ENGINE_VERSION" \
#   -var "permissions_boundary_arn=arn:aws:iam::$bamboo_AWS_ACCOUNT_ID:policy/$bamboo_ROLE_BOUNDARY"