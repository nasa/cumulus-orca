#!/bin/bash
set -ex

export AWS_ACCESS_KEY_ID=$bamboo_AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$bamboo_AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=$bamboo_AWS_DEFAULT_REGION

cat << EOF > resources.tf.template
# create buckets
resource "aws_s3_bucket" "tf-state" {
  bucket = "PREFIX-tf-state"
}

# create buckets
resource "aws_s3_bucket" "internal" {
  bucket = "PREFIX-internal"
}
EOF

sed -e 's/PREFIX/'"$bamboo_PREFIX"'/g' resources.tf.template > resources.tf

#remove old files from bamboo
rm variables.tf outputs.tf main.tf
# Initialize deployment
terraform init \
  -input=false

# Deploy buckets and dynamodb table via terraform
echo "Deploying S3  buckets and dynamoDB table"
terraform apply \
  -auto-approve \
  -lock=false \
  -input=false