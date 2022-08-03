#!/bin/bash
set -ex

export CUMULUS_AWS_ACCESS_KEY_ID=$bamboo_CUMULUS_AWS_ACCESS_KEY_ID
export CUMULUS_AWS_SECRET_ACCESS_KEY=$bamboo_CUMULUS_AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=$bamboo_CUMULUS_AWS_DEFAULT_REGION

#remove old files from bamboo as they throw error
rm *.tf
#deploy the S3 buckets and dynamoDB table first
git clone --branch develop --single-branch https://github.com/nasa/cumulus-orca.git && cd integration_test
#replace prefix with bamboo prefix variable
sed -e 's/PREFIX/'"$bamboo_PREFIX"'/g' buckets.tf.template > buckets.tf

if aws s3api head-bucket --bucket ${bamboo_PREFIX}-tf-state;then
    echo "terraform state bucket already present. Using existing state file"
else
    echo "terraform state bucket is not created. Creating ..."
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

#copy terraform state file to the created tf-state bucket
aws s3 cp terraform.tfstate s3://$bamboo_PREFIX-tf-state/buckets-tf/terraform.tfstate

#clone cumulus orca template for deploying RDS cluster
git clone --branch $bamboo_CUMULUS_ORCA_DEPLOY_TEMPLATE_VERSION --single-branch https://git.earthdata.nasa.gov/scm/orca/cumulus-orca-deploy-template.git
cd cumulus-orca-deploy-template
echo "cloned $bamboo_CUMULUS_ORCA_DEPLOY_TEMPLATE_VERSION branch"

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
echo "Deploying rds-cluster-tf module to $bamboo_DEPLOYMENT"
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