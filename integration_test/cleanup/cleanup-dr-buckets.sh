#!/bin/bash
set -ex

#initialize terraform
terraform init -input=false
#destroy using terraform
echo "Deploying DR S3 buckets in Disaster Recovery account"
terraform destroy \
  -auto-approve \
  -input=false