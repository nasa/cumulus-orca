#!/bin/bash
set -ex

export AWS_ACCESS_KEY_ID=$bamboo_DR_AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$bamboo_DR_AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=$bamboo_AWS_DEFAULT_REGION

#remove old files from bamboo as they throw error
rm *.tf
git clone --branch develop --single-branch https://github.com/nasa/cumulus-orca.git && cd integration_test
#replace prefix with bamboo prefix variable
sed -e 's/PREFIX/'"$bamboo_PREFIX"'/g' dr-buckets.tf.template > dr-buckets.tf

if ! aws s3api head-bucket --bucket $bamboo_PREFIX-dr-tf-state;then
    echo "terraform state bucket is not created. Creating ..."
    aws s3api create-bucket --bucket $bamboo_PREFIX-dr-tf-state  --region $bamboo_AWS_DEFAULT_REGION --create-bucket-configuration LocationConstraint=$bamboo_AWS_DEFAULT_REGION
    
    aws s3api put-bucket-versioning \
    --bucket $bamboo_PREFIX-dr-tf-state \
    --versioning-configuration Status=Enabled

    aws dynamodb create-table \
      --table-name $bamboo_PREFIX-dr-tf-locks \
      --attribute-definitions AttributeName=LockID,AttributeType=S \
      --key-schema AttributeName=LockID,KeyType=HASH \
      --billing-mode PAY_PER_REQUEST \
      --region $bamboo_AWS_DEFAULT_REGION
else
    echo "terraform state bucket present."
fi

#configruing S3 backend
echo "terraform {
  backend \"s3\" {
    bucket = \"$bamboo_PREFIX-dr-tf-state\"
    region = \"$bamboo_AWS_DEFAULT_REGION\"
    key    = \"terraform.tfstate\"
    dynamodb_table = \"$bamboo_PREFIX-dr-tf-locks\"
  }
}" >> terraform.tf

terraform init -input=false
echo "Deploying S3  buckets in Disaaster Recovery account"
terraform apply \
  -auto-approve \
  -input=false