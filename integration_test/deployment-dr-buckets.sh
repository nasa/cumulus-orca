#!/bin/bash
set -ex

if aws s3api head-bucket --bucket ${bamboo_PREFIX}-dr-tf-state;then
    echo "terraform state bucket already present. Using existing state file"
else
    echo "Something went wrong when checking terraform state bucket. Creating ..."
    aws s3api create-bucket --bucket ${bamboo_PREFIX}-dr-tf-state  --region ${bamboo_AWS_DEFAULT_REGION} --create-bucket-configuration LocationConstraint=${bamboo_AWS_DEFAULT_REGION}
    
    aws s3api put-bucket-versioning \
    --bucket ${bamboo_PREFIX}-dr-tf-state \
    --versioning-configuration Status=Enabled

    aws dynamodb create-table \
      --table-name ${bamboo_PREFIX}-dr-tf-locks \
      --attribute-definitions AttributeName=LockID,AttributeType=S \
      --key-schema AttributeName=LockID,KeyType=HASH \
      --billing-mode PAY_PER_REQUEST \
      --region ${bamboo_AWS_DEFAULT_REGION}
fi

cd integration_test

#initialize terraform
terraform init -input=false
#deploy using terraform
echo "Deploying DR S3 buckets in Disaster Recovery account"
terraform apply \
  -auto-approve \
  -input=false