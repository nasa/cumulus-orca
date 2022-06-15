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
resource "aws_s3_bucket_versioning" "versioning-tf-state" {
  bucket = aws_s3_bucket.tf-state.id
  versioning_configuration {
    status = "Enabled"
  }
}
resource "aws_dynamodb_table" "tf-locks" {
  name           = "PREFIX-tf-locks"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"
  attribute {
    name = "LockID"
    type = "S"
}
EOF

#replace prefix with bamboo prefix variable
sed -e 's/PREFIX/'"$bamboo_PREFIX"'/g' resources.tf.template > resources.tf

#remove old files from bamboo as they are giving error
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