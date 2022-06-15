#!/bin/bash
set -ex

export AWS_ACCESS_KEY_ID=$bamboo_AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$bamboo_AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=$bamboo_AWS_DEFAULT_REGION


# Ensure remote state is configured for the deployment
# echo "terraform {
#         backend \"s3\" {
#             bucket = \"$bamboo_PREFIX-tf-state\"
#             key    = \"deploy_resources\"
#             region = \"$bamboo_AWS_DEFAULT_REGION\"
#             dynamodb_table = \"$bamboo_PREFIX-tf-locks\"
#     }
# }" > resources.tf

cat << EOF > resources.tf
# create the ECR repo
resource "aws_sqs_queue" "test_queue" {
  ## OPTIONAL
  name                        = "test-queue"
}
EOF

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