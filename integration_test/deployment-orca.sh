#!/bin/bash
set -ex

source integration_test/shared/orca-terraform.sh

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
echo "Deploying Cumulus S3 buckets and dynamoDB table"
terraform apply \
  -auto-approve \
  -input=false
cd ..

# Deploy rds-cluster-tf via terraform
cd cumulus-orca-deploy-template/rds-cluster-tf
perform_terraform_command_rds_cluster "apply"

export RDS_USER_ACCESS_SECRET_ARN=$(terraform output admin_db_login_secret_arn)
export DB_HOST_ENDPOINT=$(terraform output rds_endpoint)
export RDS_SECURITY_GROUP=$(terraform output security_group_id)
#-------------------------------------------------------------------

# Deploy data-persistence via terraform
cd ../data-persistence-tf
perform_terraform_command_data_persistence "apply"
#-------------------------------------------------------------------

# Deploy cumulus-tf via terraform
cd ../cumulus-tf
perform_terraform_command_cumulus "apply"