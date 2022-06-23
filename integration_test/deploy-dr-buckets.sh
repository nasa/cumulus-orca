#!/bin/bash
set -ex

export AWS_ACCESS_KEY_ID=$bamboo_AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$bamboo_AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=$bamboo_AWS_DEFAULT_REGION

#remove old files from bamboo as they throw error
rm *.tf
git clone --branch develop --single-branch https://github.com/nasa/cumulus-orca.git && cd integration_test
#replace prefix with bamboo prefix variable
sed -e 's/PREFIX/'"$bamboo_PREFIX"'/g' dr-buckets.tf.template > dr-buckets.tf

if ! aws s3 cp s3://$bamboo_PREFIX-tf-state/dr-buckets-tf/terraform.tfstate .;then
    echo "terraform state file not present in S3. Creating the buckets in DR account."
else
    echo "Terraform state file found in S3 bucket. Using S3 remote backend"
fi

terraform init -input=false
echo "Deploying S3  buckets in Disaaster Recovery account"
terraform apply \
  -auto-approve \
  -input=false

#copy terraform state file to the created tf-state bucket
aws s3 cp terraform.tfstate s3://$bamboo_PREFIX-tf-state/dr-buckets-tf/terraform.tfstate